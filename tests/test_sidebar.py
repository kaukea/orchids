"""Unit tests for tools/sidebar.py's pure presentation layer: flatten() and
render_lines(). No curses involved — these are plain functions over
dataclasses, exactly the split the module's own docstring calls out as what
gets tested.

Runs under both `python3 -m unittest discover` and `pytest`; stdlib only.
"""
import os
import sys
import unittest

_TOOLS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools",
)
if _TOOLS_DIR not in sys.path:
    sys.path.insert(0, _TOOLS_DIR)

import sidebar  # noqa: E402
import sidebar_model as sm  # noqa: E402


def _fleet():
    return sm.Fleet(repos=[
        sm.Repo(
            path="/tmp/repoA", name="repoA", activity="", status="running", waiting=False,
            features=[
                sm.Feature(
                    feature_id="feat-1", name="feat one", activity="doing work",
                    status="running", waiting=False,
                    subagents=[sm.Subagent(label="sub-a")],
                ),
            ],
        ),
    ])


class FlattenTests(unittest.TestCase):
    def test_depth_kind_and_target_per_row(self):
        rows = sidebar.flatten(_fleet())
        self.assertEqual(len(rows), 3)

        repo_row, feature_row, sub_row = rows
        self.assertEqual((repo_row.depth, repo_row.kind, repo_row.target),
                         (0, "repo", "repoA"))
        self.assertEqual((feature_row.depth, feature_row.kind, feature_row.target),
                         (1, "feature", "repoA ▸ feat one"))
        # a subagent row's target is its OWNING feature's target, not its own
        # label -- navigation from a subagent row targets the feature window.
        self.assertEqual((sub_row.depth, sub_row.kind, sub_row.target),
                         (2, "subagent", "repoA ▸ feat one"))
        self.assertTrue(sub_row.is_subagent)
        self.assertFalse(feature_row.is_subagent)
        self.assertFalse(repo_row.is_subagent)


class RenderLinesTests(unittest.TestCase):
    def test_status_emoji_per_row(self):
        fleet = sm.Fleet(repos=[
            sm.Repo(path="/r", name="r-running", activity="", status="running", waiting=False),
            sm.Repo(path="/r", name="r-standby", activity="", status="standby", waiting=False),
            sm.Repo(path="/r", name="r-done", activity="", status="completed", waiting=False),
            sm.Repo(path="/r", name="r-failed", activity="", status="failed", waiting=False),
        ])
        lines = sidebar.render_lines(fleet, width=64)
        self.assertIn("🟢", lines[0])
        self.assertIn("🟡", lines[1])
        self.assertIn("✅", lines[2])
        self.assertIn("❌", lines[3])

    def test_indentation_increases_with_depth(self):
        lines = sidebar.render_lines(_fleet(), width=64)
        # strip the leading selection-marker column (always ' ' or '>')
        bodies = [line[1:] for line in lines]
        indents = [len(b) - len(b.lstrip(" ")) for b in bodies]
        self.assertEqual(indents, [0, 2, 4])

    def test_subagent_row_shows_spinner_frame(self):
        lines = sidebar.render_lines(_fleet(), spinner_frame=3, width=64)
        expected = sidebar.SPINNER_FRAMES[3 % len(sidebar.SPINNER_FRAMES)]
        self.assertIn(expected, lines[2])

    def test_waiting_row_flashes_hourglass(self):
        fleet = _fleet()
        fleet.repos[0].features[0].waiting = True
        on = sidebar.render_lines(fleet, flash_on=True, width=64)[1]
        off = sidebar.render_lines(fleet, flash_on=False, width=64)[1]
        self.assertIn("⏳", on)
        self.assertNotIn("⏳", off)
        # same column, blank instead of the emoji when not flashing
        emoji_pos = on.index("⏳")
        self.assertEqual(off[emoji_pos], " ")

    def test_selected_row_has_leading_marker(self):
        lines = sidebar.render_lines(_fleet(), selected=1, width=64)
        self.assertTrue(lines[1].startswith(">"))
        self.assertTrue(lines[0].startswith(" "))
        self.assertTrue(lines[2].startswith(" "))

    def test_lines_truncated_to_width(self):
        lines = sidebar.render_lines(_fleet(), width=6)
        for line in lines:
            self.assertLessEqual(len(line), 6)


if __name__ == "__main__":
    unittest.main()
