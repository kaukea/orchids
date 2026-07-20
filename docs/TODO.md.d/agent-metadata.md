- created: 2026-07-19
- created_by: fable-5
- created_during: f/status-channel

## Blockers

- Lands after [[message-bus]] merges.

## Questions

- **Which wins when identity-at-birth and status-at-time disagree?** An agent announces its
  model and effort at load, but both can change mid-session (fable disengages, tokens run
  out). Parked during the bus build precisely because it needs a tiebreak rule, not just a
  field.
- Denominators: token counts are meaningless without the context-window size and the rate
  card. Where do those come from, and do they belong in the announcement or looked up?

## Findings

- Token count has TWO consumers with different needs: the agent (context occupancy — am I
  running out of room?) and the operator (money). They bill differently, so a single sum
  cannot yield cost — the classes have to stay broken out.

## Proposal

Add model, effort and the token denominators to agent metadata on the bus, with an explicit
rule for which source wins when the announcement and the live state disagree.

## Testing

To agree when ripened.
