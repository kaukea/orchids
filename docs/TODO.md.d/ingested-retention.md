- created: 2026-07-18
- created_by: operator
- created_during: f/workstream-log

## Blockers
- Needs a few weeks of accumulated `_ingested/` streams (from ~2026-08-04) before
  the evaluation is meaningful.

## Questions
- Did anyone actually open `.git/the-works/_ingested/` to cross-check README,
  CHANGELOG, or commit claims since 2026-07-18?

## Findings

## Proposal
Decide the retention policy for ingested workstream logs: keep the archive (and
maybe point the close gate's readme/changelog checks at it), bound it (age/count),
or reinstate delete-on-ingest. Ruled provisional in Decision-011.

## Testing
Operator judgement on observed value; no mechanical test.
