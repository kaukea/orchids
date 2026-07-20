# TODO — the orchids board

Slim index; prose in sidecars (`TODO.md.d/<id>.md`). orchids is the fleet's data
package (skills, agents, rule files); the distribution code is the `kauk-sync`
stopgap in serialseb/kauk — it dies when the real kauk CLI ships. Weigh process
items against that.

Badge: `type · status · urgency · readiness · component · gh#`.

## Publication

- `housekeeping · todo · urgent · queued · publication · gh#1` [Pre-publication cleanup & public/private split](TODO.md.d/pre-publication-cleanup.md)

## Process machinery

- `feature · done · · complete · process ·` [Tool split: package manager moved to kauk; orchids data-only](TODO.md.d/tool-split-to-kauk.md)
- `feature · todo · · blocked-on-answers · process · gh#2` [Architect close choreography without fragile hooks](TODO.md.d/hook-choreography.md)
- `feature · todo · low · queued · process · gh#3` [Decide the SessionStart self-heal hook](TODO.md.d/session-start-hook.md)
- `housekeeping · done · · complete · process ·` [Registry file set for orchids itself](TODO.md.d/registry-file-set.md)
- `bug · cancelled · low · complete · process ·` [~~Self-install: root link entries collide (src == dst)~~](TODO.md.d/self-install-link-collision.md)
- `bug · todo · · blocked-on-answers · process · gh#4` [ARCHITECTURE.md has no Taxonomy table — board lint fails 13/13](TODO.md.d/architecture-taxonomy-missing.md)
- `feature · todo · · blocked-on-answers · process · gh#5` [Cross-repo inbox: agents deliver requirements and knowledge between projects](TODO.md.d/cross-repo-inbox.md) ~role-delivery ~external-blockers
- `feature · todo · · blocked-on-answers · process · gh#6` [Orchestrator resolves external blockers when loading its tasks](TODO.md.d/external-blockers.md) ~cross-repo-inbox
- `housekeeping · todo · low · queued · process · gh#7` [Kauk skill: symlink-write guidance is unexecutable under the harness](TODO.md.d/kauk-skill-symlink-write.md)
- `feature · done · · complete/interactive · process ·` [The works: .git/the-works/ transients, dated migrations, write gates, micro-tasks](TODO.md.d/the-works-channel.md) ~kauk-skill-symlink-write
- `feature · done · · complete/interactive · process ·` [Workstream logs: per-session rolling records replace the handover](TODO.md.d/workstream-log.md) ~the-works-channel
- `housekeeping · todo · low · queued · process · gh#8` [Decide retention for ingested workstream logs](TODO.md.d/ingested-retention.md) ~workstream-log
- `housekeeping · done · · complete/interactive · process ·` [Configure origin remote; push pending closes](TODO.md.d/origin-remote-missing.md)
- `feature · todo · · queued · process · gh#9` [Hide machinery skills from the slash list (user-invocable pass)](TODO.md.d/skill-slash-visibility.md)
- `feature · todo · · queued · process · gh#10` [Manifest entry attributes copy/ro (upstream kauk)](TODO.md.d/manifest-copy-ro.md) ~github-board-sync
- `feature · todo · · queued · process · gh#11` [Standard tree display+selection for package installs (upstream kauk)](TODO.md.d/package-select-tree.md) ~kauk-skill-symlink-write
- `feature · todo · · queued · process · gh#12` [Sync suggests a reset when the package changed (upstream kauk)](TODO.md.d/sync-suggest-reset.md) ~package-select-tree ~kauk-skill-symlink-write
- `feature · todo · · queued · process ·` [kauk validates role declarations: validate stub now, taxonomy check later (upstream kauk)](TODO.md.d/kauk-validate-roles.md) ~role-dag-frontmatter
- `feature · functional · high · complete/interactive · process · gh#13` [Cross-repo board view: GitHub issues + user-level Project, orchestrator-synced](TODO.md.d/github-board-sync.md) ~cross-repo-inbox ~external-blockers
- `housekeeping · paused · low · blocked-on-answers · process · gh#14` [Install-id migration to the kaukea org — parked until the org name is final](TODO.md.d/install-id-kaukea.md)
- `feature · todo · · queued · ·` [Orchard: the fleet workbench — global view, selection, dispatch](TODO.md.d/orchard.md) ~github-board-sync ~cross-repo-inbox
  - `feature · todo · · queued · process ·` [Orchestrator emits the orchard summary file, parseable from outside](TODO.md.d/orchard-summary.md)
  - `feature · todo · · queued · process ·` [Orchard view: consolidate the fleet, show priorities and cross-repo edges](TODO.md.d/orchard-view.md) ⊘orchard-summary
  - `feature · todo · · queued · process ·` [Orchard launch: session per repo, orchestrator told the pick and double-checks](TODO.md.d/orchard-launch.md) ⊘orchard-view
  - `feature · todo · · queued · process ·` [Tmux topology: window per architect, stacked pane per coder, focus returns on close](TODO.md.d/tmux-topology.md) ~hook-choreography ~fleet-sidebar
  - `feature · todo · · queued · process ·` [Fleet sidebar: always-visible navigable job states with phase emojis](TODO.md.d/fleet-sidebar.md) ⊘session-naming ~bus-liveness ~agent-metadata
  - `bug · todo · urgent · queued · process ·` [Session and feature naming: short, descriptive, visible — sidebar prerequisite](TODO.md.d/session-naming.md)
  - `feature · todo · urgent · queued · process ·` [Handover contract: build-ready sidecars, questions front-loaded before launch](TODO.md.d/handover-contract.md) ~architect-delegation ~injection-integrity
  - `feature · todo · urgent · queued · process ·` [Cloud architect: automate the analyzable share of the architect's job](TODO.md.d/cloud-architect.md) ⊘handover-contract
  - `feature · todo · · queued · process ·` [Cross-repo bus: live messaging across repository boundaries](TODO.md.d/cross-repo-bus.md) ~status-channel ~cross-repo-inbox
- `housekeeping · todo · low · queued · process ·` [Rename the TODO vocabulary to task list](TODO.md.d/todo-to-task-list.md)
- `feature · todo · critical · queued · process ·` [Injection integrity: make instructions arrive intact, not summarised](TODO.md.d/injection-integrity.md) ⊘readme-changelog-ownership ~session-start-hook
- `feature · todo · · queued · process ·` [Sidecar liveness: prove an agent is still listening after load](TODO.md.d/bus-liveness.md) ~message-bus
- `feature · todo · · queued · process ·` [Agent metadata: model, effort and token denominators on the bus](TODO.md.d/agent-metadata.md) ~message-bus
- `feature · done · · complete · process ·` [Review model + effort per agent role; make effort frontmatter-pinnable like model](TODO.md.d/role-model-effort.md) ~agent-metadata ~role-dag-frontmatter
- `bug · cancelled · urgent · complete · process ·` [~~Distribution is a hand-typed index: derive it from the tree, and fail loudly meanwhile~~](TODO.md.d/manifest-by-convention.md) ~role-dag-frontmatter
- `feature · todo · critical · queued · process ·` [Move README and CHANGELOG to the orchestrator](TODO.md.d/readme-changelog-ownership.md) ~injection-integrity
- `feature · todo · urgent · queued · process ·` [Deviance detection: surface drift when it happens, not weeks later](TODO.md.d/deviance-detection.md) ⊘injection-integrity
- `bug · todo · urgent · queued · process ·` [Hooks are an unowned pool in one shared file: no per-repo surface, no provenance](TODO.md.d/hook-composition.md) ~manifest-by-convention
- `bug · todo · urgent · queued · process ·` [Architect skips its delegation contract: builds without dispatching builders](TODO.md.d/architect-delegation.md)
- `feature · done · · complete/interactive · process ·` [Message bus: repo-scoped agent-to-agent messaging via a bus sidecar](TODO.md.d/message-bus.md) ~hook-choreography ~cross-repo-inbox
- `feature · todo · idea · queued · · gh#15` [Writing emails — scope to be defined by the operator](TODO.md.d/writing-emails.md)

## Role delivery

- `feature · todo · · blocked-on-answers · · gh#16` [Role-based delivery of skills and agents](TODO.md.d/role-delivery.md) ~dynamic-skill-delivery
  - `feature · done · · complete/interactive · sync ·` [Declare the role DAG in skill and agent frontmatter](TODO.md.d/role-dag-frontmatter.md)
  - `feature · todo · · plan-ready · sync ·` [Make agents first-class, with skill dependencies](TODO.md.d/agents-first-class.md) ⊘role-dag-frontmatter
  - `refactor · todo · · blocked-on-answers · process ·` [Rename and split skills to fit the role DAG](TODO.md.d/skill-renames-and-splits.md)
  - `refactor · todo · · blocked-on-answers · process ·` [Terseness and conflicting-advice pass over all skills](TODO.md.d/skill-terseness-pass.md) ⊘role-dag-frontmatter ⊘skill-renames-and-splits

## Skills

- `feature · todo · · blocked-on-answers · skills · gh#17` [Web account signup: create account, store password + OTP in Bitwarden](TODO.md.d/web-account-signup-skill.md) ~role-delivery

## Future (dot.ai features, design only)

- `feature · todo · idea · queued · sync · gh#18` [Dynamic skill delivery per role](TODO.md.d/dynamic-skill-delivery.md)
- `feature · todo · idea · queued · sync · gh#19` [Multi-source namespacing](TODO.md.d/multi-source-namespacing.md)
- `feature · todo · idea · blocked-on-answers · sync · gh#20` [Agents: external dependencies beyond in-package skills](TODO.md.d/agent-external-deps.md) ~agents-first-class ~multi-source-namespacing
