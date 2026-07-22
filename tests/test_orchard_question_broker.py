"""Unit tests for tools/orchard-question-broker.py's PURE decision logic
(sidebar-polish item 12) — match_option_key(), is_operator_busy(), and
pending_questions(). These are exactly the pieces separable from tty/tmux
I/O (mirroring tools/sidebar.py's render_lines()/curses split), so they run
with no live tmux session and no real keypress.

What this file deliberately does NOT cover — and cannot, without a live
tmux session and a real terminal — is documented in the module docstring
of tools/orchard-question-broker.py and repeated in this step's report:
an actual `tmux display-popup` rendering, and a genuine keypress being read
by _popup_read_main(). Those need a human/live check.

Runs under both `python3 -m unittest discover` and `pytest`.
"""
import importlib.util
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

# The module's filename has hyphens, so it cannot be `import`ed directly.
_SPEC = importlib.util.spec_from_file_location(
    "orchard_question_broker", os.path.join(_TOOLS_DIR, "orchard-question-broker.py"),
)
broker = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(broker)

from support import make_repo, envelope, write_message  # noqa: E402
import sidebar_model  # noqa: E402


class MatchOptionKeyTests(unittest.TestCase):
    """Item 12d: only the defined numbered-option keys register; every
    other keypress is ignored — no default, no dismiss-on-any-key."""

    def test_valid_digit_keys_map_to_zero_based_index(self):
        self.assertEqual(broker.match_option_key("1", 3), 0)
        self.assertEqual(broker.match_option_key("2", 3), 1)
        self.assertEqual(broker.match_option_key("3", 3), 2)

    def test_digit_outside_range_is_ignored(self):
        self.assertIsNone(broker.match_option_key("4", 3))
        self.assertIsNone(broker.match_option_key("0", 3))

    def test_non_digit_keys_are_ignored(self):
        for key in ("a", "\r", "\x1b", " ", "y", "Y", "\t"):
            self.assertIsNone(broker.match_option_key(key, 3), f"key={key!r}")

    def test_multi_char_input_is_ignored(self):
        self.assertIsNone(broker.match_option_key("12", 3))

    def test_empty_input_is_ignored(self):
        self.assertIsNone(broker.match_option_key("", 3))

    def test_feed_non_option_keys_then_a_valid_one_only_the_valid_one_registers(self):
        """Direct test of the required scenario: non-option keys first, then
        an option key — only the option key registers (the actual read loop
        lives in _popup_read_main and needs a live tty; this exercises the
        same per-keystroke decision it relies on, one call per keystroke)."""
        stream = ["x", "\r", "9", "a", "2"]
        result = None
        for key in stream:
            result = broker.match_option_key(key, 3)
            if result is not None:
                break
        self.assertEqual(result, 1)  # "2" -> option index 1, first valid key seen


class IsOperatorBusyTests(unittest.TestCase):
    """Item 12e: defer while input is in flight; clear on idle recency OR a
    just-completed submit."""

    def test_no_activity_ever_seen_is_not_busy(self):
        self.assertFalse(broker.is_operator_busy(now=100.0, last_submit_ts=None,
                                                  last_activity_ts=None, idle_seconds=5.0))

    def test_recent_activity_with_no_submit_is_busy(self):
        self.assertTrue(broker.is_operator_busy(now=100.0, last_submit_ts=None,
                                                 last_activity_ts=99.0, idle_seconds=5.0))

    def test_activity_older_than_idle_window_is_not_busy(self):
        self.assertFalse(broker.is_operator_busy(now=100.0, last_submit_ts=None,
                                                  last_activity_ts=90.0, idle_seconds=5.0))

    def test_submit_at_or_after_last_activity_clears_busy(self):
        # the submit keystroke IS the most recent activity too — clear
        self.assertFalse(broker.is_operator_busy(now=100.0, last_submit_ts=99.0,
                                                  last_activity_ts=99.0, idle_seconds=5.0))

    def test_activity_after_an_older_submit_is_busy_again(self):
        # they submitted a while ago, then started typing something new
        self.assertTrue(broker.is_operator_busy(now=100.0, last_submit_ts=95.0,
                                                 last_activity_ts=99.0, idle_seconds=5.0))


class PendingQuestionsTests(unittest.TestCase):
    """pending_questions() scans bus roots non-destructively (never deletes,
    mirroring tools/sidebar_model.py's own scan) and de-dupes by
    question_id, since a broadcast lands one copy per peer inbox."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.repo = make_repo(self._tmp.name)
        self.bus_root = sidebar_model.iter_bus_roots([self.repo])[0]

    def _put(self, folder, msg_id, sender, question_id, question, options):
        env = envelope(msg_id, sender, body=f"orchid:activity:{question}", notify_user=True)
        env["question_id"] = question_id
        env["question"] = question
        env["options"] = options
        write_message(self.bus_root, folder, env)

    def test_finds_a_new_question(self):
        self._put("peerA", "m1", "askerX", "q1", "Proceed?", ["Yes", "No"])

        found = broker.pending_questions([self.bus_root], seen_ids=set())

        self.assertEqual(len(found), 1)
        self.assertEqual(found[0]["question_id"], "q1")
        self.assertEqual(found[0]["question"], "Proceed?")
        self.assertEqual(found[0]["options"], ["Yes", "No"])
        self.assertEqual(found[0]["asker"], "askerX")

    def test_same_question_id_in_multiple_peer_inboxes_is_reported_once(self):
        self._put("peerA", "m1", "askerX", "q1", "Proceed?", ["Yes", "No"])
        self._put("peerB", "m2", "askerX", "q1", "Proceed?", ["Yes", "No"])

        found = broker.pending_questions([self.bus_root], seen_ids=set())

        self.assertEqual(len(found), 1)

    def test_already_seen_question_id_is_not_returned_again(self):
        self._put("peerA", "m1", "askerX", "q1", "Proceed?", ["Yes", "No"])

        found = broker.pending_questions([self.bus_root], seen_ids={"q1"})

        self.assertEqual(found, [])

    def test_messages_without_question_id_are_ignored(self):
        write_message(self.bus_root, "peerA",
                      envelope("m1", "someoneX", body="orchid:activity:just working"))

        found = broker.pending_questions([self.bus_root], seen_ids=set())

        self.assertEqual(found, [])

    def test_never_deletes_the_files_it_scans(self):
        self._put("peerA", "m1", "askerX", "q1", "Proceed?", ["Yes", "No"])

        broker.pending_questions([self.bus_root], seen_ids=set())

        self.assertTrue((Path(self.bus_root) / "peerA" / "m1.json").exists())


if __name__ == "__main__":
    unittest.main()
