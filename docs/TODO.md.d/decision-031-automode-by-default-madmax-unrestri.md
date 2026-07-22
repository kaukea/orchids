- created: 2026-07-22
- created_by: gh-ingest
- created_during: interactive

## Blockers
- None known yet.

## Questions
- Ingested from GitHub issue #119 — needs triage: type, component,
  urgency, scope.

## Findings
- Filed on GitHub (https://github.com/kaukea/orchids/issues/119); original body preserved below.

#permissions #automode #classifier #madmax #launch #spawn #settings #housekeeper

Operator rulings (2026-07-21), after a close was repeatedly stalled by permission-
classifier denials (housekeeper dispatch, pushes, even a read-only grep):

- Sessions in these repos default to AUTO permission mode: `permissions.defaultMode`
  = "auto" in the shared settings.json — spawned agents (architects, housekeepers,
  headless sub-jobs) included. Friction is the exception, not the baseline.
- `#madmax` is a BOARD TAG (trailing the task line, like an edge): a tagged task runs
  unrestricted — every `claude` launch for that feature appends
  `--dangerously-skip-permissions`. Operator-set ONLY — and because anything published
  where an agent can read it will eventually be used (operator, same night), the
  prohibition is STRUCTURAL, not prose: before honouring the tag, the launcher
  verifies it reached the board in an operator-authored commit (git provenance), not
  merely that it is present. Definition: AGENTS.files.md §TODO; spawn wiring:
  agents/orchestrator.md.
- The housekeeper's effort rises low → high and its charter gains a concurrent-streams
  briefing (main moves mid-close; stale branch context ≠ reverts) after a live misread.
