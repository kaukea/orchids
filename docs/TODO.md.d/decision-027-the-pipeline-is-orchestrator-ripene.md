- created: 2026-07-22
- created_by: gh-ingest
- created_during: interactive

## Blockers
- None known yet.

## Questions
- Ingested from GitHub issue #115 — needs triage: type, component,
  urgency, scope.

## Findings
- Filed on GitHub (https://github.com/kaukea/orchids/issues/115); original body preserved below.

#pipeline #ripener #architect #orchestrator #cloud #scope #questions #deviance #handover

Refines Decision-025 (operator, 2026-07-20):

- The ORCHESTRATOR holds the high-level WHAT: what a feature does, what it
  replaces, what it allows, why it exists at all. Intake questions are asked
  before a task reaches the board proper.
- The RIPENER is a specific agent BETWEEN orchestrator and architect. It
  CLOSES the functionality scope with targeted questions on functional
  completeness; loose ends are left as explicit VOLUNTARY deferrals, never
  silent gaps. It decides by a statistical-probability criterion (see
  [[psychometric-discovery]]) that the scope is well enough defined for the
  architect to do its job, then KICKS THE ARCHITECT OFF AUTOMATICALLY.
- The ARCHITECT formulates the TECH plan: if it has real questions it asks
  them; if not it presents the architectural plan. File- and class-level
  changes are NOT pre-decided — that is what git and refactoring are for.
  The last question is a SUMMARY of the work → MAKE IT SO → build (local) /
  pull request (cloud).
- Question economy is the design direction: as the system refines, better
  questions upstream, fewer or none downstream. Today's gates exist because
  of existing behaviour (the error rate), not as permanent shape — they
  shrink as upstream improves.
- CLOUD HAS NO BLOCKER and does not wait: a new feature is a GitHub issue;
  the orchestrator's and ripener's rounds run as comments on the issue (or a
  discussion — either); MAKE IT SO → pull request; THAT IS ALL → housekeeper
  (worktrees locally; PR amends + merge in cloud). Waiting delays discovering
  the deviance in the system — start now. Amends this afternoon's "parked"
  note on [[cloud-architect]].
