- created: 2026-07-20
- created_by: Sebastien Lambla

## Blockers

- None.

## Questions

- Replacement word for the family (skill `groom`, agent `groomer`, the verb across
  defs/skills/sidecars): prep/prepper, refine/refiner, tend/tender, ripen — operator picks.

## Findings

- Operator (2026-07-20): the word family is FORBIDDEN — it relates to bad people in other
  contexts. Applies to all output, not only these two artifacts.
- Footprint: `skills/groom/` (skill name + content), `agents/groomer.md` (+ its
  `.claude/agents/` link), `agents/orchestrator.md` (a whole section uses the verb),
  the `groom` references in `skills/orchestrator/SKILL.md`, board/sidecar prose, and
  `board_stale.py`'s references if any. Skill and agent are MANAGED ARTIFACTS — renames
  ship with a dated migration in the same branch (§Migrations), like the
  doing-skills→authoring-skills precedent.

## Proposal

Pick the replacement word, rename the skill directory and agent definition, sweep the
verb across the corpus, update manifest/README references, ship the migration. One
sweep, one branch.

## Testing

Corpus grep for the old family returns only the migration file and history; a consuming
repo syncs cleanly with the renamed artifacts; the readiness pipeline prose reads
naturally with the new word.
