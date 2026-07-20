- created: 2026-07-20
- created_by: Sebastien Lambla

## Blockers

- None; timing is free ("at some point" — operator).

## Questions

- Scope of the rename: the board file itself (`docs/TODO.md` → `docs/TASKS.md`?), the
  sidecar directory, the §TODO section of `AGENTS.files.md`, prose across skills/agents,
  and the tooling (`board_*.py`) — one sweep or file-name-last to spare consumers?
- A file move is a managed-artifact change for consuming repos → needs a dated migration
  in the same branch (§Migrations).

## Findings

- Operator (2026-07-20): "I really don't like this to-do list. It should be a task list."
  A naming change only — structure and format stay.

## Proposal

Rename the TODO board vocabulary to "task list" across file names, rule files, skills,
agent definitions and tooling, with the §Migrations entry for the file moves; sequenced
so consuming repos converge on one sync.

## Testing

Grep the corpus for the old vocabulary after the sweep; a consuming repo syncs cleanly
and its hooks/tools still resolve the board.
