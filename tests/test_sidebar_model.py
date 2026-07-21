"""Unit tests for tools/sidebar_model.py — the bus reader/aggregator.

Runs under both `python3 -m unittest discover` and `pytest`; stdlib only.
Fixtures are real git-init'd temp repos with bus message files written by
hand (see tests/support.py) — build_model() is exercised end to end, never
mocked.
"""
import os
import sys
import tempfile
import unittest

_TOOLS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools",
)
if _TOOLS_DIR not in sys.path:
    sys.path.insert(0, _TOOLS_DIR)

import sidebar_model  # noqa: E402

from support import (  # noqa: E402
    make_repo, bus_root_of, identity_body, lifecycle_body, envelope, write_message,
)


class _BusFixtureTestCase(unittest.TestCase):
    """One fresh git repo + bus root per test."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.repo = make_repo(self._tmp.name)
        self.bus_root = bus_root_of(self.repo)

    def _put(self, folder, msg_id, sender, body, ts, notify_user=None):
        write_message(
            self.bus_root, folder,
            envelope(msg_id, sender, body=body, ts=ts, notify_user=notify_user),
        )

    def _architect(self, session_id, feature_id, folder=None):
        """Write the identity announce that makes session_id a renderable
        architect feature."""
        folder = folder or session_id
        self._put(
            folder, f"{session_id}-id", session_id,
            identity_body(session_id, agent_type="architect", feature_id=feature_id,
                          name=feature_id.replace("-", " ")),
            ts="2026-01-01T00:00:00.000000+00:00",
        )
        return folder


class StatusMappingTests(_BusFixtureTestCase):
    def test_lifecycle_states_map_to_expected_status(self):
        expected = {
            "started": "running",
            "building": "running",
            "testing": "running",
            "done": "standby",
            "finished": "completed",
            "abandoned": "failed",
        }
        for state, _status in expected.items():
            session_id = f"arch-{state}"
            feature_id = f"feat-{state}"
            self._architect(session_id, feature_id)
            self._put(
                session_id, f"{session_id}-lc", session_id,
                lifecycle_body(state, feature_id=feature_id),
                ts="2026-01-01T00:00:01.000000+00:00",
            )

        fleet = sidebar_model.build_model([self.repo])
        self.assertEqual(len(fleet.repos), 1)
        features = {f.feature_id: f for f in fleet.repos[0].features}

        for state, status in expected.items():
            with self.subTest(state=state):
                feature_id = f"feat-{state}"
                self.assertIn(feature_id, features)
                self.assertEqual(features[feature_id].status, status)


class WaitingTests(_BusFixtureTestCase):
    def test_notify_user_flag_marks_waiting(self):
        self._architect("arch-notify", "feat-notify")
        self._put("arch-notify", "arch-notify-act", "arch-notify",
                  "orchid:activity:need input",
                  ts="2026-01-01T00:00:01.000000+00:00", notify_user=True)

        fleet = sidebar_model.build_model([self.repo])
        feature = fleet.repos[0].features[0]
        self.assertTrue(feature.waiting)
        self.assertEqual(feature.status, "waiting")

    def test_blocked_lifecycle_marks_waiting(self):
        self._architect("arch-blocked", "feat-blocked")
        self._put("arch-blocked", "arch-blocked-lc", "arch-blocked",
                  lifecycle_body("blocked", feature_id="feat-blocked"),
                  ts="2026-01-01T00:00:01.000000+00:00")

        fleet = sidebar_model.build_model([self.repo])
        feature = fleet.repos[0].features[0]
        self.assertTrue(feature.waiting)
        self.assertEqual(feature.status, "waiting")


class AttributionTests(_BusFixtureTestCase):
    def test_activity_attributed_to_sender_not_folder(self):
        self._architect("arch-A", "feat-A")
        # activity FROM arch-A, physically written inside a DIFFERENT
        # session's folder ("arch-B") -- simulates fan_out delivering a copy
        # into a peer's inbox. Attribution must follow envelope['from'],
        # never the folder the file was found in, and no phantom "arch-B"
        # feature must appear (arch-B never announced an identity).
        self._put("arch-B", "arch-A-act", "arch-A", "orchid:activity:working on A",
                  ts="2026-01-01T00:00:01.000000+00:00")

        fleet = sidebar_model.build_model([self.repo])
        self.assertEqual(len(fleet.repos[0].features), 1)
        feature = fleet.repos[0].features[0]
        self.assertEqual(feature.feature_id, "feat-A")
        self.assertEqual(feature.activity, "working on A")


class SubagentTests(_BusFixtureTestCase):
    def test_start_without_done_is_present(self):
        self._architect("arch-sub1", "feat-sub1")
        self._put("arch-sub1", "arch-sub1-s1", "arch-sub1",
                  "orchid:subagent:start:build-agent",
                  ts="2026-01-01T00:00:01.000000+00:00")

        fleet = sidebar_model.build_model([self.repo])
        labels = [s.label for s in fleet.repos[0].features[0].subagents]
        self.assertEqual(labels, ["build-agent"])

    def test_start_then_done_is_absent(self):
        self._architect("arch-sub2", "feat-sub2")
        self._put("arch-sub2", "arch-sub2-s1", "arch-sub2",
                  "orchid:subagent:start:build-agent",
                  ts="2026-01-01T00:00:01.000000+00:00")
        self._put("arch-sub2", "arch-sub2-s2", "arch-sub2",
                  "orchid:subagent:done:build-agent",
                  ts="2026-01-01T00:00:02.000000+00:00")

        fleet = sidebar_model.build_model([self.repo])
        labels = [s.label for s in fleet.repos[0].features[0].subagents]
        self.assertEqual(labels, [])

    def test_self_reported_messaging_label_excluded(self):
        self._architect("arch-sub3", "feat-sub3")
        self._put("arch-sub3", "arch-sub3-s1", "arch-sub3",
                  "orchid:subagent:start:messaging",
                  ts="2026-01-01T00:00:01.000000+00:00")

        fleet = sidebar_model.build_model([self.repo])
        self.assertEqual(fleet.repos[0].features[0].subagents, [])

    def test_bus_sidecar_child_session_excluded(self):
        self._architect("arch-sub4", "feat-sub4")
        # a bus sidecar child session (agent_type "bus") whose parent_session
        # points at the architect must never surface as a subagent row, even
        # though it satisfies the generic parent_session-match rule.
        self._put("bus-child", "bus-child-id", "bus-child",
                  identity_body("bus-child", agent_type="bus", name="messaging",
                                parent_session="arch-sub4"),
                  ts="2026-01-01T00:00:01.000000+00:00")

        fleet = sidebar_model.build_model([self.repo])
        self.assertEqual(fleet.repos[0].features[0].subagents, [])


class CrossRepoTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)

    def test_two_repos_both_appear_in_fleet(self):
        repo1 = make_repo(self._tmp.name)
        repo2 = make_repo(self._tmp.name)
        for repo, tag in ((repo1, "one"), (repo2, "two")):
            root = bus_root_of(repo)
            write_message(
                root, f"arch-{tag}",
                envelope(
                    f"arch-{tag}-id", f"arch-{tag}",
                    body=identity_body(f"arch-{tag}", agent_type="architect",
                                       feature_id=f"feat-{tag}"),
                    ts="2026-01-01T00:00:00.000000+00:00",
                ),
            )

        fleet = sidebar_model.build_model([repo1, repo2])
        self.assertEqual(len(fleet.repos), 2)
        self.assertEqual({r.path for r in fleet.repos}, {repo1, repo2})
        feature_ids = {r.features[0].feature_id for r in fleet.repos}
        self.assertEqual(feature_ids, {"feat-one", "feat-two"})


class DedupTests(_BusFixtureTestCase):
    def test_same_id_second_occurrence_across_scans_is_ignored(self):
        # _BusAggregator (not the throwaway one build_model() uses internally)
        # exercised directly across TWO scans -- this is the only way to
        # observe the id-dedup contract described in sidebar_model's own
        # docstring (state persists and re-delivery of an already-seen id is a
        # no-op), since build_model() always starts a fresh aggregator.
        write_message(
            self.bus_root, "arch-dedup",
            envelope("arch-dedup-id", "arch-dedup",
                    body=identity_body("arch-dedup", agent_type="architect",
                                        feature_id="feat-dedup"),
                    ts="2026-01-01T00:00:00.000000+00:00"),
        )
        write_message(
            self.bus_root, "arch-dedup",
            envelope("dup-1", "arch-dedup", body="orchid:activity:first",
                    ts="2026-01-01T00:00:01.000000+00:00"),
        )

        agg = sidebar_model._BusAggregator()
        agg.scan(self.bus_root)
        first_pass = agg.repo(self.repo)
        self.assertEqual(first_pass.features[0].activity, "first")

        # SAME envelope id "dup-1", different body, delivered as a second
        # file (simulates a stale re-delivery) -- must not be re-applied once
        # that id was seen in an earlier scan.
        write_message(
            self.bus_root, "arch-dedup",
            envelope("dup-1", "arch-dedup", body="orchid:activity:second",
                    ts="2026-01-01T00:00:02.000000+00:00"),
            filename="dup-1-retry.json",
        )
        agg.scan(self.bus_root)
        second_pass = agg.repo(self.repo)
        self.assertEqual(second_pass.features[0].activity, "first",
                         "message with an already-seen id must not be re-applied")


if __name__ == "__main__":
    unittest.main()
