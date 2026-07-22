- created: 2026-07-21
- created_by: Sebastien Lambla

## Blockers

- None.

## Questions

- ~~Duplicate/superseded close mechanics?~~ RULED (operator, 2026-07-22):
  NATIVE — the UI closes as duplicate, so the API does too: the close
  mutation's duplicate state with its duplicate-of reference. Body-note
  ("Superseded by #N"/"Duplicate of #N") remains the FALLBACK only if the
  API path proves narrower than the UI. Superseded decisions close
  not-planned with the superseded-by reference.

- **Duplicate close reason: native `state_reason=DUPLICATE`, or a body-note
  fallback like the merged `~related` gap?** field-projecting (merged
  d010887, Decision-053) confirmed GitHub has no native equivalent for
  `~related` and fell back to a body-text list — the schema-introspected
  precedent this proposal's "duplicate" plan should follow if the native path
  isn't cheap. Checked the merged `tools/board_gh.py`: task closing today is
  a single path, `gh issue close -c "Board: task reached \`{status}\`."` —
  there is no `--reason` distinction at all (not even completed vs
  not-planned), and no duplicate-of linking. Native GitHub duplicate marking
  needs `state_reason: DUPLICATE` PLUS a canonical-issue reference, which
  `gh issue close --reason` does not expose (CLI only offers `completed` /
  `not planned`); reaching it means a raw GraphQL `closeIssue`/duplicate
  mutation the codebase doesn't have yet. Recommendation: for decisions,
  close superseded/duplicate entries with `--reason "not planned"` plus a
  body/comment note ("Superseded by #N" / "Duplicate of #N") — same
  schema-gap fallback shape as `~related`, no new GraphQL surface. Reserve
  true native duplicate-state for a later task if GitHub's CLI gains it.
  Confirm this is acceptable, or say if native duplicate-state is worth the
  extra GraphQL call now.

## Findings

- Type creation is a non-issue: `ensure_issue_types` (merged, org-scoped,
  create-if-missing) is generic over any type name — adding a "Decision"
  type is a one-line extension of `TYPE_ISSUE_TYPES`-style mapping, not new
  machinery. Confirmed against `tools/board_gh.py:286-298`.
- Decisions are not board tasks — they don't come from `board.tasks()` (which
  reads TODO sidecars). `sync_issue_types`/the close loop in `push()` iterate
  tasks only, so decision-projecting needs its OWN sync pass over
  `docs/decisions.md` entries in parallel, reusing the type/close primitives
  rather than hooking into the existing per-task loops. Consistent with the
  proposal's "same way tasks do, with a different type" — not a scope change,
  just confirming the shape for the architect.
- Native Priority and Issue Dependencies (Decision-053) don't apply to this
  proposal's scope — decisions don't carry urgency or `⊘` blocking edges
  today, so no reuse/question there.

## Proposal

Decisions (docs/decisions.md entries) synchronize to the GitHub task board the
same way tasks do, with a DIFFERENT type than tasks so they can be referenced
correctly from issues and from each other.

Lifecycle mirrors exactly what the decisions file already does, using the
fields GitHub currently has:

- each decision becomes a mirrored item of its own type, referenceable by
  number/link;
- a SUPERSEDED decision closes on GitHub, pointing at the decision that
  replaces it (the file's strike + superseded-by marker, projected);
- a decision considered a DUPLICATE closes as a duplicate;
- task issues close as they do today — the closing conventions apply to both
  issues and decisions.

No new vocabulary, no new lifecycle states: project the existing semantics
onto GitHub's available fields, nothing more.

## Testing

One live synchronization against the current decisions file: every decision
appears with the decision type and is referenceable; a superseded decision
(e.g. one carrying a strike + superseded-by marker) shows closed with its
replacement referenced; a live decision shows open. Duplicate-closing verified
on a crafted duplicate or the first real one.
