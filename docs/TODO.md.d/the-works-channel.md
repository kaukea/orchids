- created: 2026-07-18
- created_by: operator
- created_during: f/the-works-channel
- completed: 2026-07-18
- completed_during: f/the-works-channel

## Blockers
- None.

## Questions
- None — all spec points ruled interactively (Decisions 008–010).

## Findings
- The uncommittable channel moved to `.git/the-works/` (from flat `.git/`,
  itself post-2026-07-11; before that, gitignored root files). A gitignored
  root file is convention-guarded and `git clean -xd`-fragile; `.git/` is
  structural; the namespace removes collision risk with git's own files.
- Migrations: dated, state-guarded instruction files merge safely — an agent
  reads all pending entries and applies the net effect, so sequence-position
  assumptions are the one authoring hazard (banned in §Migrations).
- The migration shell block must end `true`: an all-guards-false idempotent
  rerun otherwise exits 1 and reads as failure.
- Hook coverage: `HANDOVER*.md` glob (not bare `HANDOVER.md`) is required or
  provenance-stamped gathered strays are never announced.
- `kauk` is not on PATH in this repo's sessions — `kauk sync --status` could
  not run during the workflow (ignored per workflow rules).

## Proposal
Namespace the channel, add the migrations system (watermark + hook + two
entries, one backdated), batch handover ingest, narrow cross-repo write
permissions to content surfaces with an agent-behaviour norm, and add the
micro-task path. All shipped in one branch.

## Testing
Hook commands executed in isolation across their trigger states (pending /
current / stale watermark; handover present / absent / legacy-named); the
2026-07-18 migration block run verbatim on a synthetic legacy repo with a
worktree — 4/4 files gathered, contents preserved, rerun idempotent, exit 0.

Result: done — squash-merged to `main` (tombstone `archive/the-works-channel`);
hooks + migration block tested as above; prose rules land fleet-wide on next
`kauk sync`.
