---
name: ripen-tasks
description: Run a board-ripening pass — dispatch the prep-only ripener over the stalest opted-in tasks so their sidecars advance through the readiness pipeline without the operator driving each one. NOT a cron; a manual/on-demand trigger fired by the operator ("ripen the board") or by the orchestrator when it notices the change signal (docs/decisions.md or a sidecar moved since the last swept SHA). Prep-only, commit-only, N=2 per pass.
roles: [process/workflow]
share: github
compatibility: Requires git
metadata:
  tags: [ripen, board, ripening, readiness, staleness, orchestrator, ripener, trigger, on-demand]
---

# Intent (ripen)

Ripening keeps parked tasks *ready* — it advances their sidecars through the readiness
pipeline (`queued → working → blocked-on-answers → plan-ready`) so that when the operator
picks one up, the discovery is already done. It is a **subagent dispatched on a trigger**, not
a scheduled cron (Decision — ripening is change-triggered / on-demand). Automatic scheduling
(a cloud routine wrapping the *same* ripener) stays a possible later enhancement; the ripener
is trigger-agnostic, so adding a schedule later changes only how it is kicked off.

# Triggers (either fires a pass)

1. **Operator asks** — "ripen the board", "do a ripening pass", etc.
2. **Orchestrator notices the change signal** — `docs/decisions.md` or a sidecar moved since
   the last swept SHA. The orchestrator evaluates this live at a natural board-holding moment;
   there is no clock. No change → no pass → no board churn.

# The pass (what the orchestrator / operator runs)

1. **Find candidates.** Run the staleness walk:
   - default: `python3 .claude/tools/board_stale.py --n 2` — the 2 stalest ripenable tasks.
   - change-signal check: `python3 .claude/tools/board_stale.py --since "$(cat .claude/state/last-ripen.sha)"`
     lists ripenable tasks whose sidecar or a hard dep moved since the last pass; ripen the
     stalest 2 of those.
   Ripenable = a parked task (`status` todo|functional); `done`/`cancelled` are terminal.
   **Cost cap: N=2 per pass** — never fan the ripener over the whole board at once.
2. **Dispatch the ripener** on each chosen `<id>` — `Agent` tool `subagent_type: ripener` (or
   `claude --bg --agent ripener --name "orchids ▸ ${id//-/ }"`), one task per ripener — the
   `--name` carries the feature's human name (id with `-` → spaces), never the role. The
   ripener is **prep-only**: it
   advances the stage, fleshes the sidecar, projects the readiness badge, runs `board_lint.py`,
   and commits (`🌱 ripen: <id> → <stage>`). It never builds, branches, or opens a PR — a
   build-ready task is left at `plan-ready` for the operator.
3. **Record the swept SHA.** After the pass, write HEAD so the next change-signal check has a
   baseline: `git rev-parse HEAD > .claude/state/last-ripen.sha` and commit it.
4. **Re-triage.** The orchestrator ingests the ripeners' one-line results (and any Questions
   they raised for the operator) and folds them into the board-walk.

# Boundaries

- **Single writer** — the ripener only touches *parked* tasks, never the one the operator is
  actively building (no ripening a task with an open worktree / `f/<id>` branch).
- **Commit-only, no push** — the operator/orchestrator pushes; ripening never reaches a remote
  on its own. The human merge/review gate is preserved (nothing autonomous reaches `main`).
- **Supervised first** — review the ripener's commits before enabling any recurring schedule
  (there is none yet); the first autonomous-to-`main` path stays gated off.
