- created: 2026-07-22
- created_by: gh-ingest
- created_during: interactive

## Blockers
- None known yet.

## Questions
- Ingested from GitHub issue #121 — needs triage: type, component,
  urgency, scope.

## Findings
- Filed on GitHub (https://github.com/kaukea/orchids/issues/121); original body preserved below.

#push #github #workflows #tokens #batching #cloud #comments

Operator MUST (2026-07-21): while discussing or refining anything, do NOT push on
every change. origin is wired to workflows (cloud hops, watchers) — every push
triggers workloads and spends tokens downstream. Commit locally as work lands; push
ONCE when the refinement round settles, or when the push itself is the intended
signal (a watcher waiting on state). Issue/PR comments are the same trigger class:
consolidate a round into one comment rather than dribbling triggers.
