# Bus singleton: one message bus per repository, as designed

- created: 2026-07-22
- created_by: Sebastien Lambla

## Blockers

- None.

## Questions

- None on the WHAT — Decision-051 rules it: one bus per repository, agents
  are clients of it. The HOW (how agents share the one bus: a single bus
  process with per-agent subscriptions, or per-agent clients over shared
  state) is the build's to design and present.

## Findings

- Current state (drift): every agent spawns its own `bus` subagent sidecar
  at session start; the operator observed several "buses" in the sidebar
  and ruled the multiplicity a defect (Decision-051). The 2026-07-22
  orchestrator session even ran TWO bus sidecars at once by mistake —
  the per-agent pattern invites exactly this.
- Touches: `agents/bus.md`, `hooks/bus-init.sh`/`bus-end.sh`,
  `tools/bus.py`, the bus-loading instruction every agent receives at
  SessionStart, and the release choreography (Decision-041's wake-driven
  release; Decision-048/049 relay rules) — the singleton must preserve the
  gate-word relay and lifecycle signalling exactly.

## Proposal

Bring the implementation back to the designed architecture: ONE message bus
per repository. Agents connect to (announce on, listen through, send via)
the single bus; no agent spawns a peer bus. Lifecycle: the bus outlives any
one agent's session; agent close releases its subscription, never the bus.
The sidebar consequently shows exactly one bus row (rendering handled by
[[sidebar-polish]] item 5).

## Testing

With several agents live in one repo (orchestrator + an architect + a
bloomer), exactly one bus exists on the box; messages, gate-word relays,
and lifecycle signals all still deliver end-to-end; closing one agent
leaves the bus serving the others; the last agent's close leaves no
orphaned bus process.
