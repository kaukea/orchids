- created: 2026-07-19
- created_by: fable-5
- created_during: f/status-channel

## Blockers

- Lands after [[message-bus]] merges.

## Questions

- What is the cheapest evidence that a sidecar is still listening — and who checks it?

## Findings

- The identity announcement proves a sidecar loaded **at birth**. Nothing catches a sidecar
  that dies mid-session: peers keep addressing it, messages land in a folder nobody drains,
  and from the sender's side that is indistinguishable from an agent choosing not to reply.
- Observed live during the build: without `persistent: true` a Monitor stops after five
  minutes while the sidecar still reports itself as listening. So "deaf but claiming to hear"
  is a real, reachable state, not a theoretical one.
- This is the same failure shape the whole design keeps guarding against: silence that looks
  like everything is fine.

## Proposal

Decide how an agent's continued reachability is evidenced after load, and what — if anything —
acts on its absence. Deliberately unscoped: the design bans schedulers, so this must not
become a heartbeat cron by the back door.

## Testing

To agree when ripened — expected shape: a sidecar is killed mid-session and the condition is
detected without polling infrastructure.
