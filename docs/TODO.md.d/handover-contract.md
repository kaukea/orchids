- created: 2026-07-20
- created_by: Sebastien Lambla

## Blockers

- None — this is the gating work the rest of the programme waits on.

## Questions

- ~~Does [[architect-delegation]] fold into this contract rewrite or stay its own task?~~
  FOLDED IN (operator, 2026-07-20) — that entry is cancelled-as-absorbed; its content
  lives here now.
- ~~What is the completeness BAR for a build-ready sidecar?~~ RULED (Decision-025): the
  bar is the complete WHAT — definition, scope, constraints, scope answers; the HOW is
  the architect's own plan-phase output, never required at handoff. Architect discovers,
  plan-gated.
- ~~How are the operator's questions collected and asked?~~ RULED (Decision-025): two
  rounds — scope while parked, launch decisions at spawn; one scope round spans a
  cluster of RELATED features before any architect (cloud or local) launches.
- ~~(absorbed) What restores delegation trust?~~ RULED (Decision-025): builder dispatch
  mandatory above s-size, zero-builder builds fail the close gate; inline s-size builds
  are stated and justified in the close report.

## Findings

- Absorbed from [[architect-delegation]] (2026-07-20): the operator does not currently
  trust the architect — the 2026-07-20 role-dag build dispatched 4 Haiku explorers in
  discovery but built every step single-handed. The architect definition PERMITTED that
  ("directly or via parallel builders"), so the contract, not just the behaviour, was
  the bug. Decision-023's deferred header-fill move re-evaluates when delegation trust
  is restored — the trigger lives here.
- Operator (2026-07-20): the lines between orchestrator and architect are VERY BLURRED.
  The split, now ruled: the ORCHESTRATOR owns task relationships (priorities, relative
  importance, functional relevance) and the complete WHAT; the ARCHITECT owns the HOW —
  discovery + technical design IS the role — then dispatches coders.
- Hard consequence: [[cloud-architect]] cannot work without this contract — a cloud
  agent cannot ping-pong questions mid-flight, so both rounds must be complete at
  dispatch. Delivered together, with strong gating (operator).

## Proposal

Encode the contract in the definitions — DONE 2026-07-20, directly on main
(orchestrator domain, Decision-065):

- `agents/architect.md`: sidecar = WHAT, HOW is the architect's; open scope question at
  launch = broken handoff (park, don't ask mid-build); builder dispatch mandatory above
  s-size, zero-builder builds fail the close gate; frontmatter description updated.
- `agents/orchestrator.md`: the WHAT-bar walked before every spawn; one scope round
  across related features before any launch; spawn carries only the launch round
  (model/effort scaling + parallel-launch offer).
- `AGENTS.files.md` §Sidecar: `## Proposal` redefined as the WHAT; the architect records
  the frozen plan there post-gate.
- `docs/decisions.md`: Decision-025.

## Testing

Live-fire on the next architect launch: the spawn is preceded by a walked WHAT-bar and
carries only the launch round; no scope question reaches the operator mid-build; the
close report lists builder dispatches (or the justified s-size inline note). Method
pending operator agreement; the task stays open until that run passes.
