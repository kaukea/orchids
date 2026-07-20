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
| bus | haiku | one per session, loaded at session start | Not on the pipeline — the sidecar that connects a session to the message bus. Announces its parent, watches its inbox, relays messages up, sends on request. Owns the mechanism so no other role learns it. Does nothing else. |

Isolation is per-dispatch (native worktrees), not a per-repo mode. One writer
per task, always.

## The cloud path

The same pipeline ridden on GitHub events instead of a local session
(Decision-027): the feature is an issue, the gates are operator comments, the
close is a squash-merged PR.

`.github/workflows/cloud-path.yml` stays dumb — detect, gate, invoke. Every hop
cold-starts a headless role (`claude -p --agent <role>`) on a runner; state
lives only in the issue thread and the sidecar on `f/<id>`, so no hop ever
waits. Comments are actor-gated to the operator. Gate vocabulary: `ENGAGE`/⚙
kicks off, `MAKE IT SO`/🖖 builds, `THAT IS ALL`/🚪 closes; any other operator
PR comment revises.

| Cloud role | Model | Hop | Scope & boundary |
|---|---|---|---|
| orchestrator-cloud | haiku | `ENGAGE` → prologue | Resolves issue → task id (board `gh#` badge), checks the sidecar is ripe, flips the board to `doing` (its only `main` write, `docs/TODO.md` alone), creates `f/<id>`. Never plans or builds. |
| architect-cloud | opus | PLAN · BUILD · REVISE | Authors the tech plan and plan comment; on `MAKE IT SO` builds, tests, authors close docs, opens the PR (`Fixes #n`); revises on review comments. Never merges, never writes the board, never self-emits a gate. |
| housekeeper-cloud | haiku | `THAT IS ALL` → close | Verifies the close-docs gate, amends, tags `archive/<id>`, `gh pr merge --squash`, commit-count note. The only role merging feature work into `main`; engages once, post-approval. |

Runners have no kauk: each job overlays `agents/` and `skills/` into `.claude/`
(the committed symlinks point into the untracked `.ai/` clone). Auth is the
operator's subscription OAuth token (`CLAUDE_CODE_OAUTH_TOKEN` secret).
`issue_comment` fires only from the default branch — pre-merge, hops are
exercised via `workflow_dispatch` (inputs: hop, issue). Intake and ripening run
as manual issue comments until the ripener charter lands; operator-less
statistical kick-off is deferred with it.

## The message bus

A cross-cutting channel between top-level sessions, orthogonal to the pipeline —
no role depends on it to do its own job, and it belongs to no single agent type.

```
session ──spawns──> bus sidecar ──announce──> every peer's inbox
                          │
   inbox events ──────────┘──SendMessage──> its own parent
```

- **Address** = the session id (`CLAUDE_CODE_SESSION_ID`), never derived from
  location. Role and worktree are separate facts, not folded into the address.
- **Transport** = one JSON file per message under
  `$(git rev-parse --git-common-dir)/the-works/bus/<session-id>/`, so every
  worktree of a repo shares one bus and nothing is committed. The set of folders
  IS the registry; there is no broker.
- **Membership** is established by hooks, not prompts: `SessionStart` creates the
  inbox, `SessionEnd` broadcasts a departure and removes it — so a send to a
  finished agent fails immediately instead of vanishing into an unwatched folder.
- **Only top-level sessions** are members. Subagents belong to their spawner and
  already have `SendMessage`.
- **No delivery guarantee.** Messages are ephemeral, unacknowledged, and die with
  the inbox. A sender expects no answer and chooses to retry, abandon, or error.
- `orchid:identity` (broadcast once, immutable) and `orchid:status` (pulled,
  mutable — context occupancy and token spend) are answered by the sidecar off the
  parent's transcript, so they cost the parent no context and keep answering while
  it is busy or wedged.

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
agents/            five pipeline roles + bus sidecar (→ .claude/agents/)
skills/<name>/     SKILL.md packages (→ .claude/skills/, per role)
hooks/             architect-close.sh · bus-init.sh · bus-end.sh (→ .claude/hooks/)
tools/             board_lint.py · board_stale.py · bus.py (→ .claude/tools/)
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
