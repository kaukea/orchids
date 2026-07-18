# orchids — decisions

Append-only. Grep by `#keyword`; read the TAIL, never the whole file.

## [2026-07-16] Decision-001: History migration is an orchestrator charter, gated by the AGENTS.md `repository:` field
#history-rewrite #orchestrator #repository #orchids #gitflow #migration #subagent #parallel

**Context:** No role owned the `history-rewrite` skill — the orchestrator's
direct-on-main carve-out covered only the workflow component, and the architect's
scope is one feature sidecar, not every ref. Operator ruling (2026-07-16).

**Decision:**
- The orchestrator charters history migration — the one repo-wide surgery in its
  domain. No architect: the scope is the whole ref graph, not a feature.
- **Applicability gate:** the project `AGENTS.md` declares `repository:`. Only
  `orchids` (the canonical workflow shape; missing/empty counts as `orchids`) is
  eligible. Any other value (e.g. `repository: gitflow`) means the repo keeps its
  own branching model — agents never restructure its history.
- **Parallel prep, gated writes:** the skill's §0–§1 (sensitive sweep + partition
  proposal) are read-only and run as a background subagent while the orchestrator
  keeps working the board. All writes (§2+) wait behind operator gate #1; the
  partition, QES, and swap gates remain operator-only.

**Touched:** `agents/orchestrator.md` (new History-migration section),
`skills/history-rewrite/SKILL.md` (applicability gate + dispatch note),
`templates/AGENTS.md` (`repository:` convention).

## [2026-07-17 11:02 CEST] Decision-002: Delivery is driven by a task-oriented role DAG declared in the definitions
#roles #taxonomy #delivery #frontmatter #manifest #kauk #sync #context-economy #install

**Context:** Every session in every repo loads all 26 skill descriptions (~10.2 KB)
whether or not the work is relevant. `manifest.conf` already carries a `role` field
(`dev|infra|org|all`), but it is **inert**: kauk's `resolve_mode` (`bin/kauk:41-56`)
reads it only as a section name to look up in `.ai.toml`, never as a filter, and no
`.ai.toml` in the fleet defines a role section — so all 26 skills link everywhere.
Agents are worse: plain `link` lines, installed unconditionally with no identity.
Operator ruling (2026-07-17).

**Decision:**
- **Roles are task-oriented, never job titles** — `development`, not `developer`.
  Follows SFIA 9 (activity-noun categories) and NICE/NIST SP 800-181, which renamed
  its whole vocabulary in 2023 explicitly "to avoid being mistaken for job titles".
- **Authors declare the role, in the skill/agent definition's frontmatter** — not in a
  central table. The author of a skill knows what it is for; `manifest.conf`'s role
  field is retired as the home for this.
- **Roles form a DAG, not a flat list.** Nodes nest (`security` → `forensics`); a
  definition may declare several paths (`coding-tofu` is genuinely both
  `development/tofu` and `infrastructure/tofu`). A flat list forces false choices and
  presents one specific process as universal.
- **Selection installs the chosen node's subtree**, plus its ancestors' own skills.
  A node with children is selectable as the coarse pick.
- **Agents become first-class and may declare required skills** — a dependency the
  package can state, rather than an assumption (e.g. the workflow needs the groomer).
- **The HOW is kauk's, not orchids'.** orchids ships the vocabulary, the declarations
  and the dependency edges; the reader, the install-time picker, and the filter are
  kauk's. orchids is data-only, so this work lands as data even while kauk ignores it.
- **The vocabulary must not preclude unbuilt siblings** (e.g. a `process/kanban` beside
  `process/workflow`). Not built now; not designed out either.

## [2026-07-17 11:02 CEST] Decision-003: The orchids role vocabulary
#roles #taxonomy #vocabulary #sync #forensics #workflow #general #process #security

**Context:** The concrete node list implementing Decision-002, decided against the
existing 26 skills. Supersedes nothing — `dev|infra|org|all` was never a decision,
just an artifact (kauk's auto-adoption stamps every adopted skill `dev`,
`bin/kauk:272`). Operator ruling (2026-07-17).

**Decision:** the node list is

```
general            read-agents · agent-behaviour · authoring-skills ·
                   git (generic half)
process
  └ workflow       workflow · workflow-complete · handover · groom ·
                   orchestrator · history-rewrite · readme-sync ·
                   git (workflow-specific half)
  └ (kanban)       reserved sibling slot — unbuilt, must stay expressible
development        clean-code · diagnostics
  └ dotnet         coding-dotnet
  └ tofu *         coding-tofu
  └ lmstudio       coding-lmstudio
  └ file-formats   shortcut-file · reverse-engineering-files *
infrastructure     software-catalog
  └ tofu *         coding-tofu
security           digital-signature
  └ forensics      chain-of-custody · forensic-acquisition · read-apfs ·
                   machine-access · icloud · reverse-engineering-files *
```

`*` = multi-parent (the DAG rule, Decision-002).

Rulings embedded in the above, each a choice among live alternatives:
- **`general` is not `core`.** "Core" implies mandatory, which is what smuggled one
  specific process into every repo. What is actually universal is ~700 bytes.
- **The workflow is a child of `process`, not a universal.** `handover`, `readme-sync`,
  `workflow-complete` and the `Branch:`/main-immutable git rules are *our* process, and
  a repo running a different one must be able to decline them.
- **`security` is the node; `forensics` is its child.** Matches SFIA, which files
  `Digital forensics (DGFS)` under Security services. We do not promote a leaf to a
  root. `digital-signature` sits at `security` — signing is not forensics-only.
- **`infrastructure`, not `operations`.** The corpus is IaC/provisioning and contains
  zero run-it-in-production skills. The two names overlap badly; pick one. (Noted:
  `infrastructure` is industry vernacular — Spotify, GitLab — not SFIA/NICE vocabulary.)
- **`git` splits** — generic hygiene (gitmoji, subject/body limits, scope discipline)
  is `general`; the `Branch:` trailer, main-immutable, and the MAKE IT SO gates are
  `process/workflow`.
- **`doing-skills` is renamed `authoring-skills` and sits in `general`.**

**Open, deliberately not ruled here:** `write-to-s3`'s placement. Provisionally
`security/forensics`, but the operator flagged it as likely carrying private
information that must not be published — a publication question, not a taxonomy one.
See TODO `pre-publication-cleanup`.

**Gap noted, not fixed:** `ARCHITECTURE.md` has no Taxonomy table, though
`AGENTS.files.md` §TODO requires `functionality`/`component` to draw from it and
`board_lint.py` lints `value ∈ glossary`. The board's `publication` / `process` /
`sync` values are de facto only.

## [2026-07-17 14:36 CEST] Decision-004: Agent dependencies — agent→agent edges are declared, in a `requirements:` map
#agents #dependencies #frontmatter #role-delivery #install-flow #kauk

Two rulings, closing `agents-first-class`'s last open questions:

- **Agents declare dependencies on other agents**, not just on skills. The real graph
  has these edges (the orchestrator hands to architect/housekeeper/groomer; the
  architect dispatches builder), and an undeclared edge deploys a broken agent.
  Consequence for the two-page install flow: page 1 greys out agents required by a
  chosen agent, exactly as page 2 greys out required skills — the pull-in is legible,
  never silent.
- **The declaration is a `requirements:` frontmatter map with two sub-lists**, kinds
  explicit:

      requirements:
        agents: [builder]
        skills: [workflow, workflow-complete, handover]

  Chosen over a flat mixed list (would need a cross-folder uniqueness rule) and over
  typed ids (`agent:builder` — noisier). The map form takes a third sub-list later
  without disturbing these two — how `agent-external-deps` stays unprecluded while
  deferred.

Context, not ruling: the `roles:` key remains `role-dag-frontmatter`'s to settle; the
dependency contract no longer waits on it. The resolution/greying engine is kauk's
`agent-deployment`.

## [2026-07-17 14:49 CEST] Decision-005: Roles declare as slash-path placements; `general` is explicit
#roles #frontmatter #role-delivery #skills #agents #kauk #taxonomy

Three rulings, closing `role-dag-frontmatter`'s questions:

- **Key + syntax:** `roles:` is a list of slash-separated full paths —
  `roles: [development/tofu, infrastructure/tofu]`. Rejected: bare node ids
  (ancestry invisible at the declaration site), nested YAML and `role:` + `parent:`
  pairs (tree edges copied into every declarer).
- **Paths are placements.** A declared path is a deliberate placement, and a
  multi-parent node may be placed under a subset of its parents —
  `roles: [development/tofu]` alone is valid, making per-route delivery expressible.
  Lint verifies each declared path exists in the vocabulary; an incomplete set is
  intent, not an error class.
- **`general` is explicit** (`roles: [general]`). A missing `roles:` key is a lint
  error — "forgot to declare" is never readable as "deliberately general".

Context, not ruling: the vocabulary stays declared in exactly one place
(Decision-002/003). The sidecar's "one round with kauk before committing" was waived
by ruling directly; kauk's reader implements this contract as written.

## [2026-07-17 15:08 CEST] Decision-006: Architect sessions live in panes; the close returns to a pane
#tmux #workflow #architect #handoff #orchestrator #panes

Three rulings on the dispatch machinery, after the first live dispatch landed on a
window when the operator had asked for pane-level behaviour:

- **Agent sessions spawn as PANES, not windows** — the architect splits from the
  orchestrator's own pane, so the build runs next to the conversation that dispatched
  it.
- **The close handshake is pane-scoped.** `.return-window` line 1 carries a pane id
  (`%N`); the Stop hook lands the operator on exactly that pane, then kills the
  architect's pane. Legacy window ids (`@N`) remain honoured. Window-scoped return
  was insufficient the moment a window held more than one pane.
- **The spawn carries the initial prompt.** A fresh `claude` session waits silently
  for its first message; a trigger the operator must remember to type is a trigger
  forgotten. The spawn line is `claude --agent architect 'Boot: …'`.

Context, not ruling: the workflow machinery (agent defs, hooks, this contract) is
authored only by the orchestrator, directly on `main` — Decision-065's existing
ownership rule, restated at the operator's request after the pane requirement failed
to survive as conversation memory. Requirements about the machinery belong in the
agent def and this file, nowhere else.

## [2026-07-17 16:02 CEST] Decision-007: Agents hold a standing write-right over linked package files
#kauk #symlinks #permissions #skills #settings #workflow

The harness refuses Edit/Write through a symlink ("Refusing to write through
symlink"), and no setting exists to change that (verified against current Claude
Code documentation, 2026-07-17). The kauk skill's "edit at the path you loaded it
from, never chase the target" is therefore unexecutable as written. Operator ruling:

- **Agents are authorised — and required — to write linked package files by
  resolving the symlink and writing the target** in
  `.ai/repositories/<owner>/<repo>/`. That is kauk's local-edit surface; `kauk sync`
  reconciles (commit → rebase → push back). In the package's OWN repo, mirror the
  change to the real source files (repo root) in the same turn, or run `kauk sync`
  so checkout and source converge — never leave the two divergent.
- **The refusal is a harness limitation, not a policy signal.** It is not a "no";
  agents do not stop or re-ask on it. The operator's permission here is standing.
- **The fleet `settings.json` ships allow rules** — `Edit(.ai/repositories/**)` and
  `Write(.ai/repositories/**)` — so the resolved-path write is neither denied nor
  prompted, and (via permission-rule merge into the sandbox writable paths) not
  sandbox-blocked either.

Follow-up owed upstream: amend the kauk skill text (pull-only, lives in
serialseb/kauk) — see TODO `kauk-skill-symlink-write`.

## [2026-07-18 18:34 CEST] Decision-008: Transients live in .git/the-works/; structural changes ship dated migrations
#the-works #handover #mood #migrations #watermark #git #hooks

Two rulings from the-works workstream:

- **The uncommittable channel is namespaced.** `HANDOVER.md`, `MOOD.md`, and the
  migration watermark live in `$(git rev-parse --git-common-dir)/the-works/` — same
  guarantees as the former flat `.git/` placement (physically uncommittable,
  worktree-shared), plus an identity that cannot collide with git's own files or
  other tooling. Writers `mkdir -p` the directory.
- **Every structural change to a managed artifact ships a migration.** One dated,
  state-guarded file in the package's `migrations/` (format:
  `AGENTS.files.md` §Migrations), in the same branch as the change. The package
  version IS the highest migration filename; a per-clone watermark
  (`.git/the-works/migrated`) plus a `settings.json` hook announce pending entries;
  the agent merges all pending migrations and applies the net effect once.
  Historical entries may be backdated to the change they describe — a repo that
  never had the package converges by running the whole series, no fresh-install
  special case.

Context, not ruling: skills describe only the current world; legacy-conversion
clauses belong in migrations, never in skill text.

## [2026-07-18 18:36 CEST] Decision-009: Cross-repo writes are gated, surface-bound, and never the suggested route
#kauk #permissions #settings #cross-repo #skills #agents #symlinks

Narrows Decision-007's third ruling (the blanket `Edit/Write(.ai/repositories/**)`
allow rules). Decision-007's other rulings stand: the resolve-the-symlink write
procedure remains the sanctioned mechanism, and the harness symlink refusal remains
a limitation, not a policy signal. Three rules, by strength:

- **Hard gate.** No standing write-right over `.ai/repositories/**` as a whole.
  Because `kauk sync` pushes package edits back upstream, a clone write is a
  cross-repository change propagating fleet-wide — the harness permission prompt is
  the authorization gate, per occasion, not standing.
- **Surface boundary.** The fleet `settings.json` allows frictionless writes only
  inside a package's content surfaces: `agents/`, `skills/`, `files/` (the
  direct-into-repo symlink folder — the rule attaches to the folder, whatever it
  holds). Machinery (`manifest.conf`, `settings.json`, `hooks/`, `tools/`, `bin/`)
  is never writable from a consuming repo; machinery changes happen only in the
  package's own repo, through its own workflow.
- **Reasoning norm.** An agent avoids even SUGGESTING edits to a repository it is
  not working from: capture the issue (TODO naming the source repo, or report to
  the operator) and let the fix ride the source repo's workflow (`agent-behaviour`
  skill). Decision-007's write-through path is used only on explicit operator
  direction.

## [2026-07-18 18:39 CEST] Decision-010: Micro-tasks may ride main, offered by the agent, gated by the operator
#workflow #micro-task #main #commits #branching

A one-commit triviality (typo, prose fix, one-line config value) does not earn the
full workflow machinery. The agent, judging a task micro — single commit, no design
choice, no meaningful testing question — OFFERS a direct commit on `main` up front;
the operator's acceptance IS the existing direct-commit override. The agent never
self-selects the path, and promotes to a full workflow the moment scope grows (a
landed micro-commit stays on `main`; the grown scope starts fresh). Such commits
carry `Branch: main` — the sole exception to the git-commit trailer rule.
