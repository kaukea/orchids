"""Unit tests for tools/bus.py's operator_origin provenance flag.

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
import unittest

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


if __name__ == "__main__":
    unittest.main()
