- created: 2026-07-22
- created_by: gh-ingest
- created_during: interactive

## Blockers
- None known yet.

## Questions
- Ingested from GitHub issue #124 — needs triage: type, component,
  urgency, scope.

## Findings
- Filed on GitHub (https://github.com/kaukea/orchids/issues/124); original body preserved below.

#tmux #workflow #architect #orchestrator #panes #windows #topology #peek #subagents #handoff

Operator rulings settling [[tmux-topology]] (2026-07-21); supersedes Decision-006
(pane-beside) and carries its tags:

- SESSION per repository → WINDOW per architect (one per active feature). The
  architect is something the operator interacts with — never a side-by-side or
  horizontal split. Spawn uses `tmux new-window`; the pane keeps its `arch:<id>`
  title, so the title-based teardown (Decision-028) works unchanged — killing the
  window's last pane closes the window and focus returns to the orchestrator.
- SUBAGENTS (builders, prep, sidecars) are hidden by default — never named
  sessions, surfaced in the sidebar via the bus — but hidden does NOT mean
  unpeekable: a PEEK opens a disposable pane tailing the subagent's live
  transcript, on demand, and closes when done.
- Peeks (and any deliberately visible subagent) live in a dedicated RIGHT COLUMN
  of the architect's window, stacked vertically, capped — never appended below
  the architect (the unusable default `split-window -v`). The cap is a
  build-time knob.
