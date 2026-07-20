- created: 2026-07-20
- created_by: Sebastien Lambla
- completed: 2026-07-20

### Why cancelled

Folded into [[handover-contract]] (operator, 2026-07-20): the same blurred
orchestrator/architect line, attacked once — the contract rewrite defines both
what the architect receives and what it must delegate. Findings and the open
trust questions moved there; Decision-023's re-evaluation trigger rides along.

## Blockers
- None.

## Questions
- What exactly breaks trust: builders never dispatched during build, explorer
  results ignored, or both? (2026-07-20 role-dag run: 4 Haiku explorers WERE
  dispatched in discovery; the build itself was done single-handed.)
- What restores it: mandatory builder dispatch above a size threshold, evidence
  of delegation in the close-gate report, or a different contract shape?

## Findings
- Operator, 2026-07-20: the architect "cannot be trusted right now, it doesn't
  even call other agents to work." Its definition allows building "directly or
  via parallel builders", so single-handed building is currently contract-legal —
  the contract, not just the behaviour, may be what needs tightening.
- Consequence already applied: the `completed:`/`completed_during:` header fill
  stays with the housekeeper (Decision-023) until this is fixed; re-evaluate then.

## Proposal
- (to be ripened once the Questions are answered)

## Testing
One full feature cycle in which the architect demonstrably delegates per the
tightened contract (builder dispatches visible in its stream log); then
re-evaluate Decision-023's deferred header move.
