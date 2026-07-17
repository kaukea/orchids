# orchids — project rules

Project-specific agent rules. Shared rules: `AGENTS.shared.md` (immutable). File formats:
`AGENTS.files.md`. Taxonomy: `ARCHITECTURE.md`.

## What this is

orchids is the fleet's **data package**: the agents, skills, and rule files that give
every repository one operating model. It ships data, not code — distribution is the
`kauk` CLI's job (`serialseb/kauk`, currently the `kauk-sync` stopgap). Read `README.md`
for the operating model and `ARCHITECTURE.md` for how the package is laid out.

## Hard constraints

- **`AGENTS.shared.md` is immutable** — never modified, deleted, moved, or renamed
  unless the operator explicitly asks.
- **orchids is data-only.** No package-manager or distribution code lands here; that
  belongs in `serialseb/kauk`. Weigh process work against the stopgap's short life.
- **This repo's own artifacts are dogfood.** A change to a skill, agent, or rule file
  takes effect on the next session in every consuming repo — treat edits as fleet-wide.

## Conventions

- `repository: orchids` — the branching model this repo follows. `orchids` (the
  default; missing or empty counts as it) is the canonical workflow shape and makes
  the repo eligible for `history-rewrite` migration. Any other value (e.g.
  `repository: gitflow`) means the repo keeps its own model — agents must not
  restructure its history.
- Follow the file registry in `AGENTS.shared.md` (docs/TODO.md + sidecars,
  docs/decisions.md, CHANGELOG.md, ARCHITECTURE.md). `main` is immutable; work on
  `f/<id>` branches; close per the `workflow-complete` skill.
- Orchestrator board commits on `main` carry `Branch: main` — the `git-commit`
  never-`main` trailer rule is overridden by the procedural-on-main carve-out.
