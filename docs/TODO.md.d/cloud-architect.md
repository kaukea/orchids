- created: 2026-07-20
- created_by: Sebastien Lambla

## Blockers

- ⊘[[handover-contract]] — operator: without a better-defined orchestrator→architect
  handover, "cloud agents will not work". To be delivered together, with strong gating.

## Questions

- Where does the existing close-to-complete design live? Operator referenced it
  (2026-07-20); not found in orchids or kauk docs — locate or re-capture before grooming.
- Which slice of the architect's job goes to the cloud first: analysis + question
  drafting only, or through to implementation of gated MAKE-IT-SO features?
- Relationship to the cloud orchestrator lane in [[github-board-sync]] (board-event
  triage on Actions): same runner infrastructure, or a separate cloud-agent mechanism?

## Findings

- Operator (2026-07-20): a close-to-complete design exists for using cloud agents to
  automate part of the architect's job — features that can be analyzed, questions asked,
  technical details sorted, then implementation done. Wanted SOON, and explicitly paired
  with [[handover-contract]] because the handover completeness is what makes an
  un-interactive agent viable.

## Proposal

To be written once the existing design is located ([[handover-contract]] defines the
interface it plugs into).

## Testing

To agree at grooming; must include one real feature taken through the cloud path with
every gate honoured (no self-approved MAKE IT SO, no self-approved close).
