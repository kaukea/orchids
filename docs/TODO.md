# TODO — the orchids board

Slim index; prose in sidecars (`TODO.md.d/<id>.md`). orchids is the fleet's data
package (skills, agents, rule files); the distribution code is the `kauk-sync`
stopgap in serialseb/kauk — it dies when the real kauk CLI ships. Weigh process
items against that.

Badge: `type · status · urgency · readiness · component · gh#`.

## Publication

- `housekeeping · todo · urgent · queued · publication ·` [Pre-publication cleanup & public/private split](TODO.md.d/pre-publication-cleanup.md)

## Process machinery

- `feature · done · · complete · process ·` [Tool split: package manager moved to kauk; orchids data-only](TODO.md.d/tool-split-to-kauk.md)
- `feature · todo · · blocked-on-answers · process ·` [Architect close choreography without fragile hooks](TODO.md.d/hook-choreography.md)
- `feature · todo · low · queued · process ·` [Decide the SessionStart self-heal hook](TODO.md.d/session-start-hook.md)
- `housekeeping · done · · complete · process ·` [Registry file set for orchids itself](TODO.md.d/registry-file-set.md)
- `bug · cancelled · low · complete · process ·` [~~Self-install: root link entries collide (src == dst)~~](TODO.md.d/self-install-link-collision.md)
- `bug · todo · · blocked-on-answers · process ·` [ARCHITECTURE.md has no Taxonomy table — board lint fails 13/13](TODO.md.d/architecture-taxonomy-missing.md)
- `feature · todo · · blocked-on-answers · process ·` [Cross-repo inbox: agents deliver requirements and knowledge between projects](TODO.md.d/cross-repo-inbox.md) ~role-delivery ~external-blockers
- `feature · todo · · blocked-on-answers · process ·` [Orchestrator resolves external blockers when loading its tasks](TODO.md.d/external-blockers.md) ~cross-repo-inbox
- `housekeeping · todo · low · queued · process ·` [Kauk skill: symlink-write guidance is unexecutable under the harness](TODO.md.d/kauk-skill-symlink-write.md)

## Role delivery

- `feature · todo · · blocked-on-answers · ·` [Role-based delivery of skills and agents](TODO.md.d/role-delivery.md) ~dynamic-skill-delivery
  - `feature · todo · · plan-ready · sync ·` [Declare the role DAG in skill and agent frontmatter](TODO.md.d/role-dag-frontmatter.md)
  - `feature · todo · · plan-ready · sync ·` [Make agents first-class, with skill dependencies](TODO.md.d/agents-first-class.md) ⊘role-dag-frontmatter
  - `refactor · todo · · blocked-on-answers · process ·` [Rename and split skills to fit the role DAG](TODO.md.d/skill-renames-and-splits.md)
  - `refactor · todo · · blocked-on-answers · process ·` [Terseness and conflicting-advice pass over all skills](TODO.md.d/skill-terseness-pass.md) ⊘role-dag-frontmatter ⊘skill-renames-and-splits

## Skills

- `feature · todo · · blocked-on-answers · skills ·` [Web account signup: create account, store password + OTP in Bitwarden](TODO.md.d/web-account-signup-skill.md) ~role-delivery

## Future (dot.ai features, design only)

- `feature · todo · idea · queued · sync ·` [Dynamic skill delivery per role](TODO.md.d/dynamic-skill-delivery.md)
- `feature · todo · idea · queued · sync ·` [Multi-source namespacing](TODO.md.d/multi-source-namespacing.md)
- `feature · todo · idea · blocked-on-answers · sync ·` [Agents: external dependencies beyond in-package skills](TODO.md.d/agent-external-deps.md) ~agents-first-class ~multi-source-namespacing
