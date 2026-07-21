- created: 2026-07-21
- created_by: fable-5
- completed: 2026-07-21
- completed_during: orchestrator session
- created_during: orchestrator session

## Blockers

- None.

## Questions

- None — mechanical fix.

## Findings

- Live-fire 2026-07-21: `board_gh.py push` created issues for every unbadged TOP-LEVEL
  board line (10 created) but silently skipped every NESTED line — the task regex does
  not accept leading indentation, so none of the Orchard children (session-naming,
  tmux-topology, cloud-architect, …) were projected. session-naming (gh#34) was
  projected by hand to unblock the cloud live-fire.
- The tool also has no per-task filter (`push` is all-or-nothing); worth considering
  while in there, per "no silent caps" — a skipped line should at least be reported.

## Proposal

Make the board task regex indentation-tolerant so nested children project like
top-level tasks, and report (not silently skip) any line that fails to parse.

## Testing

`push` on a board with nested unbadged children creates their issues and writes the
badges back; a dry run reports every line it would skip.

### Resolution (2026-07-21)

Fixed 2026-07-21 in the tags-and-labels build: LINE_RE is indentation-tolerant, children project as issues (18 created), parent issues link children by number (verified on the orchard parent, gh#25).
