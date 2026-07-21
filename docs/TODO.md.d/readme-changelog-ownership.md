- created: 2026-07-19
- created_by: fable-5

## Blockers

_None._

## Questions

- ~~Does the orchestrator write these at close, or the housekeeper under
  instruction?~~ Settled (Decision-034, 2026-07-21): NEITHER re-derives. The
  architect stages the CONTENT verbatim in its sidecar result while context is
  hot; the orchestrator writes the FILE at ingest — placement, format, merge and
  operator gate only, never rewriting. Housekeeper stays verify-only.

## Findings

- The single-writer rule today names only the board and `docs/decisions.md` as orchestrator
  owned — "child sessions do not write those directly." README and CHANGELOG are left to the
  feature branch, with the architect authoring and the housekeeper verifying.
- **That does not work, evidenced 2026-07-19.** The message-bus architect wrote CHANGELOG
  entries by imitating existing ones without ever opening `AGENTS.files.md`, and edited the
  README without loading `readme-sync` — the skill its own close gate names. Both were
  specified; both were skipped; the output looked plausible.
- These are repo-level integration artifacts, the same category as the board and decisions: a
  feature-scoped agent sees one feature and writes them from that vantage, which is exactly
  why the board was made orchestrator-owned in the first place.

## Proposal

Per Decision-034: architects stop editing CHANGELOG.md and README.md. Their close
gate instead STAGES the content — the changelog entry in their own words, the
user-facing README delta — as blocks in the sidecar result. The orchestrator
promotes both intact at ingest (canonical format, parallel-feature merge,
readme-sync judgement, operator gate). Implementation is workflow-component
(architect def close gate, AGENTS.shared Close gate, workflow-complete presence
checks, handover ingest steps) — orchestrator builds directly on an operator go.

## Testing

A feature closes without its architect having edited either file, and both are correct
afterwards.
