---
name: groom
description: Run a board-grooming pass — dispatch the prep-only groomer over the stalest opted-in tasks so their sidecars advance through the readiness pipeline without the operator driving each one. NOT a cron; a manual/on-demand trigger fired by the operator ("groom the board") or by the orchestrator when it notices the change signal (docs/decisions.md or a sidecar moved since the last swept SHA). Prep-only, commit-only, N=2 per pass.
roles: [process/workflow]
share: github
compatibility: Requires git
metadata:
  tags: [groom, board, grooming, readiness, staleness, orchestrator, groomer, trigger, on-demand]
---

# Intent (groom)

Grooming keeps parked tasks *ready* — it advances their sidecars through the readiness
pipeline (`queued → working → blocked-on-answers → plan-ready`) so that when the operator
picks one up, the discovery is already done. It is a **subagent dispatched on a trigger**, not
a scheduled cron (Decision — grooming is change-triggered / on-demand). Automatic scheduling
(a cloud routine wrapping the *same* groomer) stays a possible later enhancement; the groomer
is trigger-agnostic, so adding a schedule later changes only how it is kicked off.

# Triggers (either fires a pass)

1. **Operator asks** — "groom the board", "do a grooming pass", etc.
2. **Orchestrator notices the change signal** — `docs/decisions.md` or a sidecar moved since
   the last swept SHA. The orchestrator evaluates this live at a natural board-holding moment;
   there is no clock. No change → no pass → no board churn.

# The pass (what the orchestrator / operator runs)

1. **Find candidates.** Run the staleness walk:
   - default: `python3 .claude/tools/board_stale.py --n 2` — the 2 stalest groomable tasks.
   - change-signal check: `python3 .claude/tools/board_stale.py --since "$(cat .claude/state/last-groom.sha)"`
     lists groomable tasks whose sidecar or a hard dep moved since the last pass; groom the
     stalest 2 of those.
   Groomable = a parked task (`status` todo|functional); `done`/`cancelled` are terminal.
   **Cost cap: N=2 per pass** — never fan the groomer over the whole board at once.
2. **Dispatch the groomer** on each chosen `<id>` — `Agent` tool `subagent_type: groomer` (or
   `claude --bg --agent groomer`), one task per groomer. The groomer is **prep-only**: it
   advances the stage, fleshes the sidecar, projects the readiness badge, runs `board_lint.py`,
   and commits (`🌱 groom: <id> → <stage>`). It never builds, branches, or opens a PR — a
   build-ready task is left at `plan-ready` for the operator.
3. **Record the swept SHA.** After the pass, write HEAD so the next change-signal check has a
   baseline: `git rev-parse HEAD > .claude/state/last-groom.sha` and commit it.
4. **Re-triage.** The orchestrator ingests the groomers' one-line results (and any Questions
   they raised for the operator) and folds them into the board-walk.

# Boundaries

- **Single writer** — the groomer only touches *parked* tasks, never the one the operator is
  actively building (no grooming a task with an open worktree / `f/<id>` branch).
- **Commit-only, no push** — the operator/orchestrator pushes; grooming never reaches a remote
  on its own. The human merge/review gate is preserved (nothing autonomous reaches `main`).
- **Supervised first** — review the groomer's commits before enabling any recurring schedule
  (there is none yet); the first autonomous-to-`main` path stays gated off.
