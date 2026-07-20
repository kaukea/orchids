- created: 2026-07-20
- created_by: opus-4.8
- completed: 2026-07-20
- completed_during: main (direct workflow-component authoring)

## Result

done. Implemented directly on `main` (workflow component — the orchestrator's own
domain, no architect). Operator registered the choices 2026-07-20; see Decision-019.

- `model:` + `effort:` set in all six agent-def frontmatters with concrete current IDs:
  orchestrator `claude-fable-5`/high, architect `claude-opus-4-8`/xhigh (pegged),
  builder `claude-sonnet-5`/high, ripener `claude-sonnet-5`/low, housekeeper
  `claude-haiku-4-5`/low, bus `claude-haiku-4-5`/low.
- Orchestrator definition gained the model-tier heuristic: it scales the architect's
  model (fable ↔ opus ↔ sonnet) and effort from sized complexity at handoff, floor =
  the frontmatter default, deviations stated + operator-agreed before launch.
- Harness-honours-`effort:` question (see below) resolved pragmatically: the value is
  the declared default the orchestrator reads and applies via `--effort`; if a later
  harness/kauk reader honours it natively, no change is needed.

## Blockers

- None to *review* the assignments. The "pin effort in frontmatter" half leans on
  [[role-dag-frontmatter]] — that task establishes the first machine-read frontmatter key
  and whatever YAML-reading precedent kauk gains; align the `effort:` key with it.

## Questions

- **Is `effort:` honoured from agent-def frontmatter by the harness, the way `model:` is?**
  `model:` in an agent def is read by the `claude --agent` launcher today. Effort is currently
  only settable via `--effort` at launch. If the harness does NOT read an `effort:` frontmatter
  key, "pinnable" means the orchestrator reads it at handoff and passes `--effort` — a launcher
  concern, not a product feature we can assume. Establish which before proposing a field.
- **Default vs. override.** A frontmatter `effort:` is a role DEFAULT; the orchestrator already
  picks effort per-task-complexity at handoff (orchestrator.md "Choose the agent and the effort
  from estimated complexity"). The field sets the floor the override starts from — confirm that
  framing so the two don't fight.

## Findings

- Current pins (agent-def `model:` frontmatter): orchestrator/architect/builder/ripener/
  housekeeper all `opus`- or `sonnet`-generic in prose; the bus sidecar is pinned `model: haiku`.
  None carry an effort default — effort travels only as a launch flag.
- The generic tier names are stale against the current lineup. Grounded starting points
  (from the current model catalogue + Anthropic's effort/tier guidance, NOT measured on our
  workloads — treat as sweep starting points, "start at high, iterate"):
  - **orchestrator** — `claude-opus-4-8`, effort **high** (xhigh for heavy ripening). Board
    reasoning + judgment; medium was ruled too weak here (operator, 2026-07-19).
  - **architect** — `claude-opus-4-8`, effort **xhigh**; escalate to `claude-fable-5` for the
    hardest long-horizon builds (Fable pricing exceeds Opus-tier — per-task escalation, not
    default). Deepest coding/agentic role.
  - **builder** — `claude-sonnet-5`, effort **medium** (high for tricky steps). Sonnet 5 now
    reaches near-Opus quality on coding/agentic at ~3/5 the price and is the first Sonnet with
    `xhigh` — a genuine upgrade from the old sonnet-4-6 assumption.
  - **ripener** — `claude-sonnet-5`, effort **low–medium**. Prep / sidecar fleshing.
  - **housekeeper** — `claude-sonnet-5` (or `claude-haiku-4-5`), effort **low**. Deterministic
    git close, mechanical.
  - **bus / absorber / explorers** — `claude-haiku-4-5`, effort **low**. Pure mechanism.
- Effort is a five-step axis (`low/medium/high/xhigh/max`). Guidance: `xhigh` is the sweet spot
  for coding/agentic on Fable 5 / Opus 4.8 / Sonnet 5; `high` is the floor for
  intelligence-sensitive work; `low` for cheap mechanical subagents. On Opus 4.8 specifically,
  start at `high` and sweep up rather than reflexively maxing.

## Proposal

Two parts:

1. **Review and re-pin each role's model + effort** against the current lineup (above), replacing
   generic tier names with concrete current IDs.
2. **Make effort pinnable in agent-def frontmatter the way `model:` is** — a role-default
   `effort:` key that travels with the definition, so the orchestrator only overrides at handoff
   when task complexity demands. Resolve the harness-honours-it question first (see Questions);
   if the harness ignores it, the orchestrator's launch path reads it and passes `--effort`.

Sibling of [[agent-metadata]] (that surfaces model/effort on the BUS at runtime; this pins the
role DEFAULTS in the definition — different layer).

## Testing

To agree when ripened. Likely: pin the fields, launch each role, confirm the effort default is
honoured (frontmatter or launcher path) and the per-task override still wins.
