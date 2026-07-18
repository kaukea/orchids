- created: 2026-07-18
- created_by: operator
- created_during: f/workstream-log
- completed: 2026-07-18
- completed_during: f/workstream-log

## Blockers
- None.

## Questions
- None — ruled interactively (Decision-011).

## Findings
- The end-of-session handover structurally cannot serve resets: a dead or bloated
  session never writes one. Rolling per-session logs invert this — successors
  find state on disk by construction.
- Section format is held loosely by design: operator wants agent behaviour across
  repos to drive iteration; the migrations machinery makes later format changes
  cheap.
- Hook glob `the-works/*/_closed` is one level deep, so `_ingested/<stream>/_closed`
  stays silent — verified.
- Positive record duplicates commits/changelog; negative record (dead ends,
  failures) exists ONLY in these logs — the reason ingestion archives rather than
  deletes (provisional).

## Proposal
Per-session rolling logs in .git/the-works/<stream>/, `_closed` marker, ingest =
promote (single-writer) → archive to `_ingested/`; legacy HANDOVER*.md folded by
migration into a closed `legacy` stream.

## Testing
Hook exercised per state (open stream silent; `_closed` fires; legacy flat file
fires; archived stream silent). Migration block run verbatim on a synthetic repo:
both flat files folded with sortable names + `_closed`, idempotent rerun, exit 0.
Dogfooded: this workstream kept its own rolling log from anchor to close. NOT
tested: a real cross-session relay after a reset — first live reset is the test.

Result: done — squash-merged to `main` (tombstone `archive/workstream-log`).
