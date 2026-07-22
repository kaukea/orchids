"""Unit tests for tools/bus.py's operator_origin provenance flag, and the
`ask`/answer question protocol (sidebar-polish item 12c-f).

Mirrors the notify_user coverage style used elsewhere in this suite (see
tests/test_sidebar_model.py, tests/support.py): a real git-init'd temp repo,
the module under test exercised end to end rather than mocked.

Runs under both `python3 -m unittest discover` and `pytest`.
"""
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

try:
    import jsonschema
except ImportError:  # pragma: no cover - environment-dependent
    jsonschema = None

_TOOLS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools",
)
if _TOOLS_DIR not in sys.path:
    sys.path.insert(0, _TOOLS_DIR)

import bus  # noqa: E402

from support import make_repo  # noqa: E402

_SCHEMA_PATH = os.path.join(_TOOLS_DIR, "message.schema.json")
_BUS_PY = os.path.join(_TOOLS_DIR, "bus.py")


def _schema() -> dict:
    with open(_SCHEMA_PATH, encoding="utf-8") as f:
        return json.load(f)


class MakeEnvelopeTests(unittest.TestCase):
    """Unit-level: make_envelope() itself, no subprocess involved."""

    def test_operator_origin_true_is_present(self):
        env = bus.make_envelope("senderX", "recipientA", operator_origin=True)
        self.assertTrue(env["operator_origin"])

    def test_operator_origin_false_is_absent(self):
        env = bus.make_envelope("senderX", "recipientA")
        self.assertNotIn("operator_origin", env)

    @unittest.skipIf(jsonschema is None, "jsonschema not installed")
    def test_operator_origin_envelope_validates_against_schema(self):
        env = bus.make_envelope("senderX", "recipientA", operator_origin=True)
        jsonschema.validate(instance=env, schema=_schema())


class IdentityOfExitGraceTests(unittest.TestCase):
    """Unit-level: identity_of()'s exit_grace_seconds field, no subprocess."""

    def test_default_is_ten_seconds(self):
        self.assertEqual(bus.identity_of()["exit_grace_seconds"], 10)
        self.assertEqual(bus.DEFAULT_EXIT_GRACE_SECONDS, 10)

    def test_override_is_carried_through(self):
        self.assertEqual(bus.identity_of(30)["exit_grace_seconds"], 30)


class CliRoundTripTests(unittest.TestCase):
    """CLI-level: `send --operator-origin` then `receive`, in a real repo."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.repo = make_repo(self._tmp.name)

    def _bus(self, *args):
        return subprocess.run(
            [sys.executable, _BUS_PY, *args],
            cwd=self.repo, check=True, capture_output=True, text=True,
        )

    def test_operator_origin_round_trips_through_send_and_receive(self):
        self._bus("init", "recipientA")
        self._bus(
            "send", "--from", "senderX", "--to", "recipientA",
            "--operator-origin", "--body", "hello",
        )

        out = self._bus("receive", "recipientA")
        messages = json.loads(out.stdout)

        self.assertEqual(len(messages), 1)
        msg = messages[0]
        self.assertTrue(msg["operator_origin"])
        self.assertEqual(msg["from"], "senderX")
        self.assertEqual(msg["body"], "hello")

        if jsonschema is not None:
            jsonschema.validate(instance=msg, schema=_schema())

    def test_broadcast_operator_origin_round_trips(self):
        self._bus("init", "senderX")
        self._bus("init", "recipientA")
        self._bus("broadcast", "--from", "senderX", "--operator-origin", "--body", "hi")

        out = self._bus("receive", "recipientA")
        messages = json.loads(out.stdout)

        self.assertEqual(len(messages), 1)
        self.assertTrue(messages[0]["operator_origin"])


class AnnounceExitGraceCliTests(unittest.TestCase):
    """CLI-level: `announce --exit-grace-seconds N` reaches peers on the field,
    and omitting the flag still defaults to 10 (identity_of()'s default)."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.repo = make_repo(self._tmp.name)

    def _bus(self, *args, session_id):
        env = dict(os.environ, CLAUDE_CODE_SESSION_ID=session_id)
        return subprocess.run(
            [sys.executable, _BUS_PY, *args],
            cwd=self.repo, check=True, capture_output=True, text=True, env=env,
        )

    def test_exit_grace_seconds_flag_is_broadcast(self):
        self._bus("init", "peerA", session_id="peerA")
        self._bus("announce", "--exit-grace-seconds", "45", session_id="announcerX")

        out = self._bus("receive", "peerA", session_id="peerA")
        messages = json.loads(out.stdout)

        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]["body"]["exit_grace_seconds"], 45)
        self.assertEqual(messages[0]["from"], "announcerX")

    def test_announce_without_flag_defaults_to_ten(self):
        self._bus("init", "peerB", session_id="peerB")
        self._bus("announce", session_id="announcerY")

        out = self._bus("receive", "peerB", session_id="peerB")
        messages = json.loads(out.stdout)

        self.assertEqual(messages[0]["body"]["exit_grace_seconds"], 10)


class SignalOnBehalfOfTests(unittest.TestCase):
    """CLI-level: `signal --on-behalf-of ID` attributes the envelope to ID, not
    the caller — the orchestrator's path for broadcasting a killed agent's own
    terminal lifecycle signal (docs/TODO.md.d/sidebar-polish.md item 2)."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.repo = make_repo(self._tmp.name)

    def _bus(self, *args, session_id):
        env = dict(os.environ, CLAUDE_CODE_SESSION_ID=session_id)
        return subprocess.run(
            [sys.executable, _BUS_PY, *args],
            cwd=self.repo, check=True, capture_output=True, text=True, env=env,
        )

    def test_on_behalf_of_sets_envelope_from(self):
        self._bus("init", "watcher", session_id="watcher")
        # the orchestrator's own session ("orchestratorZ") issues the signal,
        # naming the killed architect ("killed-arch-1") as the sender.
        self._bus(
            "signal", "--state", "abandoned", "--feature", "some-feature",
            "--on-behalf-of", "killed-arch-1", session_id="orchestratorZ",
        )

        out = self._bus("receive", "watcher", session_id="watcher")
        messages = json.loads(out.stdout)

        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]["from"], "killed-arch-1")
        self.assertEqual(messages[0]["body"]["state"], "abandoned")
        self.assertEqual(messages[0]["body"]["feature_id"], "some-feature")

    def test_without_on_behalf_of_signal_still_uses_caller(self):
        self._bus("init", "watcher2", session_id="watcher2")
        self._bus(
            "signal", "--state", "finished", "--feature", "own-feature",
            session_id="selfSignallerA",
        )

        out = self._bus("receive", "watcher2", session_id="watcher2")
        messages = json.loads(out.stdout)

        self.assertEqual(messages[0]["from"], "selfSignallerA")


class QuestionEnvelopeUnitTests(unittest.TestCase):
    """Unit-level: _question_envelope() itself, no subprocess involved."""

    def test_carries_notify_user_and_activity_body_for_the_existing_sidebar_signal(self):
        env = bus._question_envelope("askerX", "peerA", "q1", "Proceed?", ["Yes", "No"])
        self.assertTrue(env["notify_user"])
        self.assertEqual(env["body"], "orchid:activity:Proceed?")

    def test_carries_question_fields(self):
        env = bus._question_envelope("askerX", "peerA", "q1", "Proceed?", ["Yes", "No"])
        self.assertEqual(env["question_id"], "q1")
        self.assertEqual(env["question"], "Proceed?")
        self.assertEqual(env["options"], ["Yes", "No"])

    @unittest.skipIf(jsonschema is None, "jsonschema not installed")
    def test_question_envelope_validates_against_schema(self):
        env = bus._question_envelope("askerX", "peerA", "q1", "Proceed?", ["Yes", "No"])
        jsonschema.validate(instance=env, schema=_schema())


class MatchAnswerUnitTests(unittest.TestCase):
    """Unit-level: _match_answer() — consumes only the matching reply,
    leaves every other message in the inbox untouched."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.box = Path(self._tmp.name)

    def _write(self, name, env):
        (self.box / name).write_text(json.dumps(env), encoding="utf-8")

    def test_no_reply_yet_returns_none(self):
        self._write("unrelated.json", {"id": "1", "from": "x", "to": "y", "body": "hi"})
        self.assertIsNone(bus._match_answer(self.box, "q1"))
        self.assertTrue((self.box / "unrelated.json").exists())

    def test_matching_reply_is_consumed_and_returned(self):
        self._write("other.json", {"id": "1", "from": "x", "to": "y",
                                    "in_reply_to": "q-other", "body": "not this one"})
        self._write("answer.json", {"id": "2", "from": "question-broker", "to": "askerX",
                                     "in_reply_to": "q1", "body": '{"index": 0, "option": "Yes"}'})

        answer = bus._match_answer(self.box, "q1")

        self.assertEqual(answer, '{"index": 0, "option": "Yes"}')
        self.assertFalse((self.box / "answer.json").exists())
        self.assertTrue((self.box / "other.json").exists())  # untouched — belongs to someone else


class AskCliRoundTripTests(unittest.TestCase):
    """CLI-level: `ask` broadcasts, blocks, and returns once a reply
    addressed back to it (via the existing `send --in-reply-to`) arrives —
    the live-tmux-popup half of item 12c is NOT exercised here (see the
    orchard-question-broker tests/report for that boundary); this is the
    bus message protocol only."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.repo = make_repo(self._tmp.name)

    def _bus(self, *args, session_id=None, **kwargs):
        env = dict(os.environ)
        if session_id is not None:
            env["CLAUDE_CODE_SESSION_ID"] = session_id
        return subprocess.run(
            [sys.executable, _BUS_PY, *args],
            cwd=self.repo, capture_output=True, text=True, env=env, **kwargs,
        )

    def test_ask_round_trips_to_an_answer(self):
        self._bus("init", "peerA", session_id="peerA")

        proc = subprocess.Popen(
            [sys.executable, _BUS_PY, "ask", "--question", "Proceed?",
             "--option", "Yes", "--option", "No", "--poll-interval", "0.05"],
            cwd=self.repo, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            env=dict(os.environ, CLAUDE_CODE_SESSION_ID="askerX"),
        )
        try:
            # the broadcast lands in peerA's inbox almost immediately
            deadline = time.time() + 5
            question_id = None
            while time.time() < deadline and question_id is None:
                out = self._bus("receive", "peerA", session_id="peerA")
                messages = json.loads(out.stdout)
                for m in messages:
                    if m.get("question_id"):
                        question_id = m["question_id"]
                        received = m
                if question_id is None:
                    time.sleep(0.05)
            self.assertIsNotNone(question_id, "ask() never broadcast a question")

            self.assertTrue(received["notify_user"])
            self.assertEqual(received["question"], "Proceed?")
            self.assertEqual(received["options"], ["Yes", "No"])
            self.assertEqual(received["body"], "orchid:activity:Proceed?")

            # the "broker" (standing in for tools/orchard-question-broker.py)
            # answers directly over the bus, exactly like it would after a
            # real popup returned a keypress
            self._bus(
                "send", "--from", "question-broker", "--to", "askerX",
                "--in-reply-to", question_id, "--body", '{"index": 0, "option": "Yes"}',
            )

            stdout, stderr = proc.communicate(timeout=5)
        finally:
            if proc.poll() is None:
                proc.kill()
                proc.communicate()

        self.assertEqual(proc.returncode, 0, stderr)
        self.assertEqual(json.loads(stdout), {"index": 0, "option": "Yes"})

    def test_ask_requires_at_least_two_options(self):
        proc = self._bus(
            "ask", "--question", "Proceed?", "--option", "OnlyOne",
            session_id="askerY",
        )
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("at least two", proc.stderr)


if __name__ == "__main__":
    unittest.main()
