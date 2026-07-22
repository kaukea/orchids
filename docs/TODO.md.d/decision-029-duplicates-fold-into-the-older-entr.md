- created: 2026-07-22
- created_by: gh-ingest
- created_during: interactive

## Blockers
- None known yet.

## Questions
- Ingested from GitHub issue #117 — needs triage: type, component,
  urgency, scope.

## Findings
- Filed on GitHub (https://github.com/kaukea/orchids/issues/117); original body preserved below.

#merge #duplicates #supersession #board #tasks #decisions #dedup

Operator ruling (2026-07-21): the two relations get different merge models.

- DUPLICATE (the same thing filed twice — tasks, issues, board entries): the git
  model. The OLDER entry is the home; the newer one is struck as the duplicate and
  its content folds back into the older. Ids, edges and links keep resolving. A
  machine-generated stub with no unique history is deleted outright; a human-authored
  duplicate is cancel-struck on the board ("duplicate of [[x]]") so its trail
  survives. Any gh# badge the newer filing carried re-binds to the home.
- SUPERSESSION (a changed RULING): the newer wins — docs/decisions.md keeps its
  convention of striking the older heading with a "Superseded by" marker.

First execution: GitHub issue #23 folded into [[fleet-sidebar]] (da7cd2d).
