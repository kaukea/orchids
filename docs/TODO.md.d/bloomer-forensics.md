- created: 2026-07-24
- created_by: Sebastien Lambla

## Blockers

None — evidence is all in git history, archived branches, telemetry notes, and ingested
workstream logs.

## Questions

- Verdict pending from the investigation (launched 2026-07-24, background): was the
  authoring agent's sidecar read directly or received as subagent summaries?

## Findings

- The divergence being investigated: the bloomer's charter (Decision-027, promoted from
  the psychometric-discovery task) specifies a measurement instrument — adaptive
  questioning, consistency checks, a statistical convergence criterion, auto-kick. The
  built agent is a sidecar-fleshing clerk whose effective convergence criterion is
  "sections present", with triggers that depend on the orchestrator noticing a change
  signal.
- Operator hypothesis (stated 2026-07-24, ~90% prior, to be tested not assumed): the
  authoring architect never read its sidecar directly — instructions arrived as
  subagent summaries and attenuated. If confirmed, this is a live instance of the
  injection-integrity defect class ([[injection-integrity]], gh#28: instructions must
  arrive intact, not summarised).

## Proposal

Forensic reconstruction of how the bloomer got its shape: full git timeline of the
agent definition (including its pre-rename history), the charter and sidecar content as
they stood at each authoring commit, the architect definition's read-vs-summarize
protocol at the time, telemetry notes and surviving workstream logs from the authoring
feature. Deliverable: a timeline, an instructions-vs-built comparison, a verdict on the
summarization hypothesis with confidence and ranked alternatives, and implications
routed to [[injection-integrity]]. Read-only; findings land here, remediation is
scoped as follow-up tasks (likely: the bloomer rebuild chartered in the 2026-07-24
blueprint, plus injection-integrity hardening).

## Testing

Investigation task — the gate is evidential: every timeline claim carries a commit SHA
or file reference; the verdict states its confidence and what evidence would overturn
it.
