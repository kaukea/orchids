# Merge queue investigating: does GitHub's native queue serve the fleet?

- created: 2026-07-22
- created_by: Sebastien Lambla

## Blockers

- None.

## Questions

- (shaped at bloom) Whether GitHub's merge queue fits the fleet's close
  model — squash composition on staging refs (Decision-054), operator
  approval to merge (branch-protecting), callabloom authorship, changelog
  ordering (merge-ordering / "Mr. Rabbit") — or fights it.

## Findings

- Operator intake (2026-07-22): "investigate merge queues." The obvious
  neighbours: [[merge-ordering]] wants serialized merge ordering to own
  changelog order; [[branch-protecting]] wants operator approval encoded;
  Decision-054 just moved squash composition onto staging refs. A native
  queue could implement the first, must not break the second, and needs
  reconciling with the third.

## Proposal

An investigation, not a build: what GitHub merge queues do (grouping,
required checks, squash behaviour, actor identity), what they would replace
or break in the fleet's close machinery, and a recommendation — adopt,
adapt, or stay custom. Findings land here; any adoption becomes its own
task.

## Testing

Not applicable beyond the deliverable: a findings-backed recommendation the
operator can rule on.
