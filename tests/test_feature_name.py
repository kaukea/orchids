"""Unit tests for tools/feature_name.py — the canonical human-name lookup
for a feature id (sidebar-polish item 11, "GRAMMAR — RESOLVED").

Priority under test: board short-title -> sidecar H1 -> mechanical
id.replace('-', ' ') fallback. Runs under both `python3 -m unittest
discover` and `pytest`.
"""
import os
import subprocess
import sys
import tempfile
import unittest

_TOOLS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools",
)
if _TOOLS_DIR not in sys.path:
    sys.path.insert(0, _TOOLS_DIR)

import feature_name as fn  # noqa: E402

_SCRIPT = os.path.join(_TOOLS_DIR, "feature_name.py")


def _write(path: str, content: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)


class FeatureNameTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = self._tmp.name

    def tearDown(self):
        self._tmp.cleanup()

    def _board(self, body: str) -> None:
        _write(os.path.join(self.root, "docs", "TODO.md"), body)

    def _sidecar(self, feature_id: str, body: str) -> None:
        _write(os.path.join(self.root, "docs", "TODO.md.d", f"{feature_id}.md"), body)

    def test_board_short_title_wins(self):
        self._board(
            "## Process machinery\n\n"
            "- `feature · todo · · queued · process ·` "
            "[Field projection: sidecar maps to GitHub](TODO.md.d/field-projecting.md)\n"
        )
        self._sidecar("field-projecting", "# field-projecting stub\n")
        self.assertEqual(
            fn.feature_name("field-projecting", root=self.root),
            "Field projection: sidecar maps to GitHub",
        )

    def test_sidecar_h1_used_when_board_entry_missing(self):
        self._board("## Process machinery\n\nno matching entry here\n")
        self._sidecar("some-feature", "# Some feature, properly named\n\nbody\n")
        self.assertEqual(
            fn.feature_name("some-feature", root=self.root),
            "Some feature, properly named",
        )

    def test_sidecar_h1_used_when_board_file_absent(self):
        self._sidecar("only-sidecar", "# Only the sidecar exists\n")
        self.assertEqual(
            fn.feature_name("only-sidecar", root=self.root),
            "Only the sidecar exists",
        )

    def test_mechanical_fallback_when_neither_present(self):
        self.assertEqual(
            fn.feature_name("brand-new-stub", root=self.root),
            "brand new stub",
        )

    def test_mechanical_fallback_when_root_missing_entirely(self):
        missing_root = os.path.join(self.root, "does-not-exist")
        self.assertEqual(
            fn.feature_name("brand-new-stub", root=missing_root),
            "brand new stub",
        )

    def test_cancelled_title_strikethrough_is_stripped(self):
        self._board(
            "## Process\n\n"
            "- `bug · cancelled · nice-to-have · complete · process ·` "
            "[~~Self-install: root link entries collide~~](TODO.md.d/self-install-link-collision.md)\n"
        )
        self.assertEqual(
            fn.feature_name("self-install-link-collision", root=self.root),
            "Self-install: root link entries collide",
        )

    def test_malformed_board_line_does_not_crash_falls_through(self):
        self._board(
            "## Process\n\n"
            "- this line is not a well-formed board entry at all `` [[broken\n"
            "- `feature · todo · · queued · process ·` no link here, just text\n"
        )
        self._sidecar("weird-id", "# Weird id sidecar heading\n")
        self.assertEqual(
            fn.feature_name("weird-id", root=self.root),
            "Weird id sidecar heading",
        )

    def test_never_returns_claude(self):
        cases = [
            ("brand-new-stub", None, None),
            ("has-board", "Has board short title", None),
            ("has-sidecar", None, "Has sidecar heading"),
        ]
        for feature_id, board_title, sidecar_h1 in cases:
            with self.subTest(feature_id=feature_id):
                if board_title:
                    self._board(
                        "## Process\n\n"
                        f"- `feature · todo · · queued · process ·` "
                        f"[{board_title}](TODO.md.d/{feature_id}.md)\n"
                    )
                if sidecar_h1:
                    self._sidecar(feature_id, f"# {sidecar_h1}\n")
                self.assertNotEqual(fn.feature_name(feature_id, root=self.root), "claude")

    def test_falsy_feature_id_returns_none(self):
        self.assertIsNone(fn.feature_name(None, root=self.root))
        self.assertIsNone(fn.feature_name("", root=self.root))

    def test_cli_prints_resolved_name(self):
        self._sidecar("cli-feature", "# CLI feature heading\n")
        out = subprocess.run(
            [sys.executable, _SCRIPT, "--id", "cli-feature", "--root", self.root],
            capture_output=True, text=True, check=True,
        )
        self.assertEqual(out.stdout.strip(), "CLI feature heading")


if __name__ == "__main__":
    unittest.main()
