# orchids — architecture

The **how** behind [README.md](README.md)'s why and what. Designed as
Decision-075/076 in the originating fleet's decision log; this page is the
package-resident summary.

## The operating model — one pipeline, walked by real agents

```
groom → [Questions] → select → [pick-HOW] → build·test loop
      → [sudo/on-box] [manual-test] → [MAKE IT SO] → close
```

A **gate** (bracketed) is a decision or capability point. The pipeline advances
as far as policy allows, then **parks** in the task's sidecar, recording what
it needs. Operator present = parks cleared in seconds; operator away = the run
stops at the first gate it cannot pass. Same machine either way — presence only
changes latency. `manual-test` and `MAKE IT SO` never auto-pass: testing and
build approval are human-only, always.

## Roles and dispatch

| Role | Model | Dispatch | Scope & boundary |
|---|---|---|---|
| orchestrator | opus | top-level session (`claude --agent orchestrator`) | Knows the board, prioritises, holds MOOD, hands ONE feature to an architect on explicit operator go. Never codes; never opens a sidecar in steady state. Authors only the workflow component, directly on `main`. |
| groomer | sonnet | dispatched per parked task | Prep only: advances one task's readiness, fleshes its sidecar, commits. Never builds, branches, or opens PRs; build-ready parks at `plan-ready`. |
| architect | opus | worktree session (`.claude/worktrees/<id>`, branch `f/<id>`) | One feature; its sidecar is the whole scope. Read-only discovery (parallel explorers) → plan agreed with the operator → **no file edit before MAKE IT SO** → builds/tests → signals `THAT IS ALL`. Never reads the board or prior conversation. |
| builder | sonnet | headless subagent from the architect | Exactly one step-spec; returns typed diff + self-test. |
| housekeeper | sonnet | headless, in the MAIN repo, after operator says "close it" | The deterministic close: verify docs, tag, squash-merge, push, remove worktree + branch. Verifies documentation, never authors it. |

Isolation is per-dispatch (native worktrees), not a per-repo mode. One writer
per task, always.

## The sidecar contract

Durable state lives in files; no role depends on chat history.

- `docs/TODO.md` — the slim board index, one badge line per task.
- `docs/TODO.md.d/<id>.md` — the task's **sidecar**, the single spine every
  role reads-and-advances: `Blockers / Questions / Findings / Proposal /
  Testing`. Formats in `AGENTS.files.md`.
- `docs/decisions.md` — rulings, greppable by `#keyword`.
- workstream logs (per-session, rolling) / `MOOD.md` — uncommittable by
  construction, kept in `$(git rev-parse --git-common-dir)/the-works/`.

Converting a live conversation into this model is a one-time distillation:
scope → `Proposal`, test method → `Testing`, open items → `Questions` /
`Blockers`, learnings → `Findings`, rulings → `decisions.md`, in-flight code →
committed on `f/<id>`. Then the session ends and the agents boot cold.

## Distribution (kauk)

orchids is a passive package; [kauk](https://github.com/serialseb/kauk)
installs and syncs it. An operator says **"install kauk/orchids"**; the agent
resolves the repo on GitHub and follows `Agent-installation.md`. In short:

1. kauk is vendored at `.ai/repositories/serialseb/kauk`.
2. `kauk init` writes `.ai.toml` and lays kauk's own skill.
3. `kauk install serialseb/orchids <origin>` clones the package, migrates
   existing files (byte-identical → symlink; project-only → adopted; diverged
   → preserved in history), and lays entries per `manifest.conf`.
4. `kauk sync` runs at workflow start and end.

`manifest.conf` line types: `skill <name> <role>` (delivery tuned per-repo in
`.ai.toml` by role section: `exclude|copy|link|local`), `link` (absolute
symlink, everyone), `template` (install-time copy, then project-owned),
`prefix` (block kept at the head of a project file).

## Repo layout

```
agents/            five role definitions (→ .claude/agents/)
skills/<name>/     SKILL.md packages (→ .claude/skills/, per role)
hooks/             architect-close.sh
tools/             board_lint.py · board_stale.py (→ .claude/tools/)
templates/         AGENTS.md (template) · CLAUDE.md (prefix block)
migrations/        dated structural-upgrade instructions (YYYY-MM-DD-<slug>.md); applied
                   per clone against the .git/the-works/migrated watermark
AGENTS.shared.md   fleet-wide non-negotiable rules (linked)
AGENTS.files.md    file-format contracts: board, sidecars (linked)
settings.json      shared Claude Code settings (linked)
manifest.conf      what this package exposes, one typed line per entry
Agent-installation.md  the agent-facing install procedure
docs/              orchids' own board (TODO.md + sidecars)
```
