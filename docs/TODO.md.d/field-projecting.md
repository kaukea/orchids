- created: 2026-07-21
- created_by: Sebastien Lambla

## Blockers

- None.

## Questions

- **Labels overlap**: since this task was written, the tags-and-labels build
  (Decision-035) already landed a full label vocabulary in `tools/board_gh.py`
  (`labels_for`/`TYPE_LABELS`/`URGENCY_LABELS`/`AREA_LABELS`/`TAG_LABELS`) — type,
  urgency, component, and tags all project as GitHub labels today. Does this
  task's "labels" bullet drop as already-done, or does it mean something
  additional (e.g. a *separate* project-field representation on top of the
  labels)? Recommendation: drop the labels bullet — it duplicates shipped work —
  and keep this task scoped to what's still missing: a native "Priority"
  project field (today only "Urgency" exists, single-select, not obviously the
  same scale), a native "Type" project field (none exists — `Status`, `Urgency`,
  `Readiness`, `Component` are the only synced fields), and blocked-by/blocking
  relationship sync (not implemented at all).

## Findings

- Operator sizing note (2026-07-21): very mechanical work — mapping badge fields
  the board already carries onto GitHub fields GitHub already supports, inside
  the existing board→GitHub sync.
- 2026-07-22 recheck: nested-tasks-projecting's indentation fix (commit
  495a48d) is orthogonal to this task — it fixed line-parsing, not field
  content; no overlap there.
- 2026-07-22 recheck: `project_sync` in `tools/board_gh.py` already syncs
  Status, Urgency, Readiness, Component as GitHub Project custom fields — no
  Priority or Type field exists yet, and no relationship (blocked-by/blocking)
  sync exists.

## Proposal

GitHub supports native fields the board already carries; the mirror leaves them
empty today. Fill them at synchronization so the GitHub view shows exactly the
board's values:

- **priority** — from the badge's urgency (critical / normal / nice-to-have /
  idea);
- **type** — from the badge's type (bug / feature / refactor / housekeeping /
  completion);
- **relationships** — blocked-by AND blocking, from the board's ⊘ edges
  (blocking is the reverse direction of a blocked-by edge);
- **labels** — the additional labels of the tag/label vocabulary the board
  already carries (Decision-035).

Expectation set by the operator: on the next synchronization after this lands,
every mirrored issue carries exactly the same values as the board. Parent/child
sub-issue nesting stays with [[nested-tasks-projecting]]; the label vocabulary
itself stays with [[tags-and-labels]] — this task only projects what exists.

## Testing

One live synchronization, then verify on a sample covering each case — an issue
with urgency set, one with ⊘ edges in both directions, one with tags — that
priority, type, both relationship directions, and labels equal the board's
values exactly.
