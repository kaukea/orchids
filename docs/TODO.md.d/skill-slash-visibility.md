- created: 2026-07-18
- created_by: operator
- created_during: f/workstream-log

## Blockers
- None.

## Questions
- Which skills stay operator-facing in the slash list? (Judgement pass per skill;
  machinery like workflow-complete/handover/read-agents are clear `user-invocable:
  false` candidates; ripen and the utilities likely stay visible.)

## Findings
- Verified against current Claude Code docs (2026-07-18): `user-invocable: false`
  frontmatter hides a skill from the `/` menu while the model still auto-invokes
  it; `disable-model-invocation: true` is the mirror; `skillOverrides` in
  settings.json gives per-repo `on | name-only | user-invocable-only | off`.

## Proposal
Frontmatter pass over the orchids skills marking process machinery
`user-invocable: false`, so consuming repos' slash lists shrink to genuinely
operator-facing skills. Optionally ship a `skillOverrides` block in the shared
settings.json as the per-repo tuning dial.

## Testing
In a consuming repo after sync: `/` list shows only the operator-facing set;
a hidden skill still auto-triggers on its description.
