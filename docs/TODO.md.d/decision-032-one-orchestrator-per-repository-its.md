- created: 2026-07-22
- created_by: gh-ingest
- created_during: interactive

## Blockers
- None known yet.

## Questions
- Ingested from GitHub issue #120 — needs triage: type, component,
  urgency, scope.

## Findings
- Filed on GitHub (https://github.com/kaukea/orchids/issues/120); original body preserved below.

#orchestrator #sessions #naming #singleton #resume #zombie

Operator ruling (2026-07-21), amending the session-naming contract mid-plan: session
names name SESSIONS, and the orchestrator is not a workstream — it orchestrates them.
Exactly ONE orchestrator session exists per repository; its claude session name is the
repository name alone (`orchids`), never the `<repo> / <human name>` slash-form,
which belongs to workstream sessions (architects, ripeners). Summoning is resuming:
`claude --resume` by the bare repo name reaches THE orchestrator — a second one is
never started (the [[zombie-revival]] path revives the same single session). Typing a
repository's name therefore always lands on its orchestrator.
