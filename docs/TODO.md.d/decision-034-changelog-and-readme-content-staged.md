- created: 2026-07-22
- created_by: gh-ingest
- created_during: interactive

## Blockers
- None known yet.

## Questions
- Ingested from GitHub issue #122 — needs triage: type, component,
  urgency, scope.

## Findings
- Filed on GitHub (https://github.com/kaukea/orchids/issues/122); original body preserved below.

#changelog #readme #close #ownership #architect #orchestrator #injection-integrity #staging

Operator ruling (2026-07-21), settling [[readme-changelog-ownership]] (gh#31): the
objection to hub authorship is information loss — the finesse of WHY a change was
made the way it was lives in the architect's context and dies in a retelling, the
same loss injection-integrity names. The settlement extends the pattern that
already works for decisions: STAGE at the source, PROMOTE intact at the hub.

- The ARCHITECT authors the CONTENT while context is hot — the changelog entry in
  its own words and the user-facing README delta — as staged blocks in its sidecar
  result. It no longer edits CHANGELOG.md or README.md.
- The ORCHESTRATOR authors the FILE at ingest — places the staged entry under the
  canonical format, merges parallel features without collision (post-squash, on
  main), applies readme-sync judgement, holds the operator gate on the entry.
  Placement and format only: the entry lands in the architect's words or not at
  all.
- The HOUSEKEEPER stays verify-only (Decision-023's clause stands; its presence
  checks move to the staged blocks). ARCHITECTURE.md stays architect-authored
  on-branch for now — structural content is feature-scoped; revisit if its
  collision rate says otherwise.
