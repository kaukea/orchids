"""Unit tests for tools/orchard_registry.py — the fleet-sidebar repo registry
(docs/TODO.md.d/sidebar-polish.md item 7: dynamic appearance + conversational
hide/show, replacing the reverted `/orchard add <path>`).

Every test points `registry_path` at a private tempfile so the real
`~/.config/orchids/sidebar-registry.json` is never touched.
"""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

_TOOLS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools",
)
if _TOOLS_DIR not in sys.path:
    sys.path.insert(0, _TOOLS_DIR)

import orchard_registry  # noqa: E402


class _RegistryTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.registry_path = Path(self._tmp.name) / "sidebar-registry.json"

    def _repo(self, name: str, with_ai_toml: bool = True) -> str:
        repo_dir = Path(self._tmp.name) / name
        repo_dir.mkdir(parents=True, exist_ok=True)
        if with_ai_toml:
            (repo_dir / ".ai.toml").write_text("# managed by kauk\n", encoding="utf-8")
        return str(repo_dir)


class RegisterTests(_RegistryTestCase):
    def test_register_path_with_ai_toml_appears(self):
        repo = self._repo("a")
        changed = orchard_registry.register_repo(repo, registry_path=self.registry_path)
        self.assertTrue(changed)
        self.assertIn(repo, orchard_registry.registered_repos(registry_path=self.registry_path))

    def test_register_without_ai_toml_is_noop(self):
        repo = self._repo("no-ai-toml", with_ai_toml=False)
        changed = orchard_registry.register_repo(repo, registry_path=self.registry_path)
        self.assertFalse(changed)
        self.assertEqual(orchard_registry.registered_repos(registry_path=self.registry_path), [])

    def test_register_twice_is_idempotent(self):
        repo = self._repo("dup")
        orchard_registry.register_repo(repo, registry_path=self.registry_path)
        second = orchard_registry.register_repo(repo, registry_path=self.registry_path)
        self.assertFalse(second)
        repos = orchard_registry.registered_repos(registry_path=self.registry_path)
        self.assertEqual(repos.count(repo), 1)

    def test_missing_registry_file_starts_empty_not_crash(self):
        self.assertEqual(orchard_registry.registered_repos(registry_path=self.registry_path), [])
        self.assertEqual(orchard_registry.hidden_repos(registry_path=self.registry_path), [])

    def test_corrupt_registry_file_recovers_to_empty(self):
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self.registry_path.write_text("{not json", encoding="utf-8")
        self.assertEqual(orchard_registry.registered_repos(registry_path=self.registry_path), [])


class PersistenceTests(_RegistryTestCase):
    """A 'fresh load' is just a fresh call with the same registry_path — this
    module holds no in-process cache, so persistence-across-load is exercised
    by simply calling the read functions again after a write."""

    def test_registration_persists_across_fresh_load(self):
        repo = self._repo("persist")
        orchard_registry.register_repo(repo, registry_path=self.registry_path)

        # a distinct, "fresh" read of the same file
        self.assertIn(repo, orchard_registry.registered_repos(registry_path=self.registry_path))
        raw = json.loads(self.registry_path.read_text(encoding="utf-8"))
        self.assertEqual(raw["repos"], [repo])

    def test_hide_then_show_persists_across_fresh_load(self):
        repo = self._repo("hideshow")
        orchard_registry.register_repo(repo, registry_path=self.registry_path)

        hidden_changed = orchard_registry.hide_repo(repo, registry_path=self.registry_path)
        self.assertTrue(hidden_changed)
        self.assertIn(repo, orchard_registry.hidden_repos(registry_path=self.registry_path))
        self.assertEqual(orchard_registry.visible_repos(registry_path=self.registry_path), [])

        shown_changed = orchard_registry.show_repo(repo, registry_path=self.registry_path)
        self.assertTrue(shown_changed)
        self.assertEqual(orchard_registry.hidden_repos(registry_path=self.registry_path), [])
        self.assertEqual(orchard_registry.visible_repos(registry_path=self.registry_path), [repo])

    def test_hiding_unregistered_path_is_noop(self):
        changed = orchard_registry.hide_repo("/nowhere", registry_path=self.registry_path)
        self.assertFalse(changed)
        self.assertEqual(orchard_registry.hidden_repos(registry_path=self.registry_path), [])

    def test_hide_twice_second_call_reports_no_change(self):
        repo = self._repo("hidetwice")
        orchard_registry.register_repo(repo, registry_path=self.registry_path)
        self.assertTrue(orchard_registry.hide_repo(repo, registry_path=self.registry_path))
        self.assertFalse(orchard_registry.hide_repo(repo, registry_path=self.registry_path))


class SelfHealTests(_RegistryTestCase):
    def test_repo_whose_ai_toml_disappeared_is_dropped(self):
        repo = self._repo("vanishing")
        orchard_registry.register_repo(repo, registry_path=self.registry_path)
        self.assertIn(repo, orchard_registry.registered_repos(registry_path=self.registry_path))

        (Path(repo) / ".ai.toml").unlink()

        healed = orchard_registry.registered_repos(registry_path=self.registry_path)
        self.assertNotIn(repo, healed)
        # persisted, not just returned transiently
        raw = json.loads(self.registry_path.read_text(encoding="utf-8"))
        self.assertNotIn(repo, raw["repos"])

    def test_hidden_entry_pruned_once_its_repo_is_uninstalled(self):
        repo = self._repo("hidden-then-gone")
        orchard_registry.register_repo(repo, registry_path=self.registry_path)
        orchard_registry.hide_repo(repo, registry_path=self.registry_path)

        (Path(repo) / ".ai.toml").unlink()

        self.assertNotIn(repo, orchard_registry.hidden_repos(registry_path=self.registry_path))
        self.assertNotIn(repo, orchard_registry.registered_repos(registry_path=self.registry_path))


class VisibleReposTests(_RegistryTestCase):
    def test_visible_excludes_hidden_but_keeps_others(self):
        shown = self._repo("shown")
        hidden = self._repo("hidden")
        orchard_registry.register_repo(shown, registry_path=self.registry_path)
        orchard_registry.register_repo(hidden, registry_path=self.registry_path)
        orchard_registry.hide_repo(hidden, registry_path=self.registry_path)

        visible = orchard_registry.visible_repos(registry_path=self.registry_path)
        self.assertEqual(visible, [shown])
        self.assertEqual(
            set(orchard_registry.registered_repos(registry_path=self.registry_path)),
            {shown, hidden},
        )


class RepoNamedTests(_RegistryTestCase):
    def test_exact_path_match(self):
        repo = self._repo("exact")
        self.assertEqual(orchard_registry.repo_named(repo, [repo, "/other"]), repo)

    def test_exact_displayed_name_match(self):
        repo = self._repo("myname")
        self.assertEqual(
            orchard_registry.repo_named("myname", [repo, "/somewhere/else"]), repo,
        )

    def test_no_match_returns_none(self):
        repo = self._repo("known")
        self.assertIsNone(orchard_registry.repo_named("unknown", [repo]))

    def test_ambiguous_name_returns_none(self):
        base = Path(self._tmp.name)
        a = base / "dup" / "x"
        b = base / "dup2" / "x"
        for p in (a, b):
            p.mkdir(parents=True)
            (p / ".ai.toml").write_text("", encoding="utf-8")
        # both display as "x" -- ambiguous, must not silently pick one
        self.assertIsNone(orchard_registry.repo_named("x", [str(a), str(b)]))


if __name__ == "__main__":
    unittest.main()
