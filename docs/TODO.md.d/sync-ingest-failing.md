# Sync ingest failing: board-sync's GitHub→board direction exits 1

- created: 2026-07-22
- created_by: Sebastien Lambla
- completed: 2026-07-22
- completed_during: f/field-projecting

## Blockers

- None.

## Questions

- ~~Reproduce needed?~~ RESOLVED — six fresh failures 2026-07-22 (provoked
  by field-projecting's live sync) were read by the wake-checker while the
  logs lived: `NameError: name 'ensure_label' is not defined. Did you
  mean: 'ensure_labels'?` at `tools/board_gh.py` line 432 in `pull()` —
  the issues-event path calls the singular name; the tags-and-labels build
  shipped the plural. Same signature across all six runs.
- ~~Delivery?~~ RULED (operator, 2026-07-22): option 1 — delegated to the
  ACTIVE [[field-projecting]] build (it owns board_gh.py; relayed
  operator-origin with the green issues-run test added). This task closes
  with that build's merge.

## Findings

- Two failures observed, both `issues`-event-triggered `board-sync` runs, both
  in the "Ingest GitHub-born changes into the board" step (exit 1):
  run 29831369050 (2026-07-21T12:44Z, issue "Testing, do not act on it") and
  run 29802639504 (2026-07-21T04:57Z, issue "Session and feature naming…").
  The push direction (board→issues) succeeds consistently in the same window.
- Step logs were no longer retrievable via `gh run view --log` at intake time
  (empty output) — the defect needs a live reproduce (open/edit a test issue)
  rather than log archaeology.
- Run annotations show two deprecations (Node 20 forced to 24 on
  actions/checkout@v4; `app-id` deprecated in favour of `client-id` on the
  callabloom token mint) — noted, not established as the cause.

## Proposal

Rename the call at `tools/board_gh.py:432` (`ensure_label` →
`ensure_labels`, arguments per the plural's signature) so the
issues-triggered ingest direction survives again. The two run-annotation
deprecations (Node 20 on checkout@v4; `app-id` → `client-id` on the token
mint) proved unrelated to the failure — separate cheap follow-ups if ever.

## Testing

A live issues-triggered run (open + edit a test issue) completes green in
both directions; the test issue's change lands on the board.

### Resolution (2026-07-22)

Fixed inside the field-projecting build per the operator's delegation
(commit c984121 on the branch; squash d010887): ensure_labels renamed at
the pull() call site. Verified in that build's live test — `board_gh.py
pull` completed end-to-end (1 ingested, no crash) after twelve consecutive
NameError failures earlier the same day.
