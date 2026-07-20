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

## [2026-07-18 19:10 CEST] Decision-011: Per-session workstream logs replace the handover; promotion is the ingester's
#the-works #workstream-log #handover #session #reset #relay #single-writer #todo #decisions

Supersedes the monolithic `HANDOVER.md` mechanics (the channel location rulings in
Decision-008 stand; this changes what lives there). Rulings:

- **Every session keeps its OWN rolling log** in `.git/the-works/<stream>/`
  (`YYYYMMDD-HHMMSS-<role>.md`): State (rewritten in place), Findings, Dead ends,
  Decisions pending promotion, Pointers — written as work happens, never
  reconstructed at the end. One file per session; a session never edits another's;
  a stream reads oldest→newest. This makes a reset or agent change
  non-destructive: the successor reads the stream and continues.
- **Single-writer on main's docs.** The board (`TODO`) and `docs/decisions.md` are
  written only by the orchestrator / top-level session. Children stage rulings in
  their log's "Decisions (pending promotion)"; the ingester promotes them. A
  top-level session (no parent) self-promotes at its own close.
- **Ingest = promote → archive.** A `_closed` stream (marker file, announced by
  the shared hook) is read, promoted, then MOVED to `.git/the-works/_ingested/` —
  PROVISIONALLY retained, not deleted: commit messages and the changelog already
  carry the positive record, but dead ends and failures have no committed home;
  a few weeks of use decide whether that archive earns its keep (follow-up task
  `ingested-retention`).

## [2026-07-18 20:28 CEST] Decision-012: orchids publishes at the renamed aihelp repo; org lands on kaukea
#github #origin #remote #org #kaukea #aihelp #publish

The repo's GitHub home is the former `SafeKeepIt/aihelp`, renamed to
`orchids` — chosen over creating a fresh repo so the dotai-sync era
stays attached. Its history was grafted in via an `ours` merge
(unrelated histories, tree untouched): every aihelp file was a
superseded May–June draft, so nothing was content-merged. Public
visibility retained (kauk clones unauthenticated by default).

Org naming: `kauk.ai` is impossible (GitHub names can't contain dots,
one case-insensitive namespace) and `kaukai` — settled on kauk's board
— turned out to be held by a dormant 2022 user account, as is `kauk`
(release ticket filed). Ruling: the org name is **kaukea** (6 letters,
kauk-kin), picked from a 409-name availability sweep. The operator
creates the org in the web UI (no API exists); the repo then transfers
`SafeKeepIt` → `kaukea`, with GitHub redirects covering both the
rename and the transfer. Dormant-release requests for `kauk`/`kaukai`
may still upgrade the name later; a rename from `kaukea` redirects.

## [2026-07-18 22:55 CEST] Decision-013: Private until scrubbed — the publish gate is real
#github #visibility #publication #scrub #leak #kaukea #board

Amends the visibility clause of Decision-012 (its repo-home and org rulings
stand): kaukea/orchids and serialseb/kauk are PRIVATE, effective immediately.
Tonight's public window (~2.5h, full history, forensic skills included) is
treated as a leak per the operator. Re-publicizing anything requires, in
order: the pre-publication-cleanup public/private split, a history scrub of
whatever surface goes public, and an explicit operator go. The
pre-publication-cleanup push gate applies to visibility changes exactly as to
pushes; no future session flips a repo public as a side effect of another
task.

## [2026-07-19 20:15 CEST] Decision-014: An agent's address is its session id
#message-bus #identity #session-id #agents #bus

Agent identity is `CLAUDE_CODE_SESSION_ID`, read from the environment. The first
draft derived it from the working directory — a linked worktree became its feature
id, the main checkout became `orch`. That ignored the environment, which already
publishes the answer, and collided for any two sessions sharing a location: the
orchestrator and a groomer both resolved to `orch` and would have drained each
other's mail.

Role (`CLAUDE_CODE_AGENT`) and worktree stay SEPARATE fields rather than being
folded into the address. A session id is unique but not guessable; a role name is
guessable but not unique. Conflating them yields something that is neither, and a
session-derived suffix on a name destroys the very property that makes an address
an address.

The creator learns the created agent's address because the created agent announces
it, naming its parent — flow is one-way, creator to created, so every edge of the
tree is known without a lookup service. `--session-id` can also mint one at launch
if a creator needs to know before first contact.

A subagent inherits its parent's environment verbatim (session id, role, PID —
verified). That is load-bearing, not a defect: it is what lets a bus sidecar
resolve to its PARENT's mailbox without being told who its parent is.

## [2026-07-19 20:15 CEST] Decision-015: Only top-level sessions sit on the bus
#message-bus #agents #subagents #scope

Bus membership is top-level sessions only. Subagents are the responsibility of the
agent that spawned them and already have `SendMessage` for talking to their owner;
they get no inbox and no address.

This dissolves the identity problem for sessions that have no stable name of their
own — several concurrent builders under one architect share no distinguishing role,
so naming them needed either a session-derived suffix (unguessable, therefore not an
address) or a per-task name (bookkeeping for a case nobody needs). Neither is built.

## [2026-07-19 20:15 CEST] Decision-016: No delivery guarantee, by design
#message-bus #delivery #reliability #bus

The bus offers no acknowledgement, no retry, no timeout and no redelivery. Messages
are deleted on consumption; a session's inbox is destroyed at SessionEnd along with
anything still unread.

A sending agent must expect never to receive an answer and decide for itself whether
to retry, abandon, or error. This is deliberate and pre-existing: building acks would
mean claim-then-delete, in-flight state, and a scheduler for timeouts — a broker,
which is exactly what the filesystem is being used to avoid.

Consequence accepted: a sidecar that dies between draining and handing up loses those
messages silently. The mitigation is not redelivery, it is that a requester notices
its own silence.

## [2026-07-19 20:15 CEST] Decision-017: The hook is the mechanism, not secrecy
#message-bus #hooks #sessionstart #sessionend #gate

Bus membership is established by SessionStart and SessionEnd hooks rather than by
instructions in agent prompts. Code does not drift; models do, and AGENTS.md and
CLAUDE.md get bypassed regularly. A hook applies to every agent in every flow,
including ones that never read their briefing.

The first draft claimed the session id was "withheld and returned by the bus — a gate
rather than a nudge", so an agent skipping its bus could not address anything. That
claim is false and has been removed: the id is an environment variable any agent can
read. What the design actually provides is DETECTION, not prevention — an agent that
never announces is visibly absent to every peer, so a skipped bus is discoverable
rather than silently deaf.

Loading the sidecar remains a model action, because a hook cannot spawn a subagent.
That is the acknowledged soft spot, accepted until the broader injection-integrity
problem is addressed.

## [2026-07-19 20:15 CEST] Decision-018: Identity is broadcast, status is asked for
#message-bus #identity #status #tokens #orchid #request-response

Immutable facts are broadcast once at load (`orchid:identity`): session id, agent
type, worktree, feature id, parent session. Mutable state is pulled on demand
(`orchid:status`): state, context occupancy, token spend.

Both logical requests are answered BY THE SIDECAR, off the parent's transcript, which
it can read because it shares the parent's session id. The parent is never woken, so
the exchange costs it no context — and status keeps answering while the parent is
busy, wedged, or mid-compaction. A parent that has never reported yields `unknown`
rather than silence, so a stalled agent stays distinguishable from a deaf one.

Token counts serve two consumers with near-identical payloads: an agent watching
context occupancy (its own death condition — context exhaustion degrades quietly
rather than failing loudly) and an operator watching spend. The four token classes
are carried broken out, never summed, because they bill at different rates and a
single total cannot yield cost.

Model and effort are deliberately NOT in identity: they can change mid-session (a
model disengaging, tokens running out), so identity-at-birth and status-at-time
would disagree. Adding them needs a rule for which wins, so they are parked rather
than half-built. Without a model there is no denominator, so counts ship raw and the
reader interprets.

`--visible` marks a payload the SENDING agent intends the user to see. It is about
agent-to-user surfacing through an agent-to-agent channel, and is unrelated to
whether operators address agents by name (they do not).

## [2026-07-20 01:44 CEST] Decision-019: Per-role model and effort are pinned in agent-def frontmatter; the orchestrator scales the architect by complexity
#workflow #agents #model #effort #frontmatter #orchestrator #tiering

Every agent def carries a `model:` and `effort:` YAML default, replacing the stale
generic tier names (`opus`/`sonnet`/`haiku`) with concrete current IDs. Registered
(operator, 2026-07-20):

- orchestrator — `claude-fable-5`, effort `high`
- architect — `claude-opus-4-8`, effort `xhigh` (the pegged default)
- builder — `claude-sonnet-5`, effort `high`; jobs are short-lived by design
- groomer — `claude-sonnet-5`, effort `low`
- housekeeper — `claude-haiku-4-5`, effort `low`
- bus (and the other pure-mechanism subagents) — `claude-haiku-4-5`, effort `low`

The architect's model is NOT fixed: the orchestrator scales it from the sized
complexity at handoff — up to `claude-fable-5` for the hardest long-horizon builds
(Fable pricing exceeds Opus-tier, so it is a per-task escalation, never the default),
the `claude-opus-4-8` peg for ordinary features, or down to `claude-sonnet-5` for
genuinely simple mechanical work. Effort scales on the same read. The frontmatter
value is the floor the override starts from; the orchestrator states any deviation
and gets operator agreement before launching. This heuristic lives in the
orchestrator definition. Sibling of Decision-018 / [[agent-metadata]], which surfaces
model+effort on the BUS at runtime — this pins the role DEFAULTS in the definition, a
different layer.

## [2026-07-20 19:45 CEST] Decision-020: Roles validation belongs to kauk; vocabulary referenced, never restated
#roles #frontmatter #lint #validation #kauk #taxonomy #authoring-skills

The role-dag-frontmatter lint (its Proposal item 3) is dropped from scope.
kauk's reader validates `roles:` when it consumes them — an orchids-side lint
over hand-authored declarations is circular, and placing enforcement in the
authoring skill is wrong because that skill is not the vocabulary's source of
truth. The vocabulary stays in Decision-003 and the frontmatter contract
REFERENCES it; no second vocabulary artifact is created in orchids. Follow-up
boarded ([[kauk-validate-roles]]): a `kauk package validate` stub now, real
taxonomy validation in kauk later.

## [2026-07-20 19:45 CEST] Decision-021: The authoring-skills rename rides role-dag-frontmatter
#skills #rename #authoring-skills #doing-skills #sequencing #roles

`doing-skills` -> `authoring-skills` is executed inside the role-dag-frontmatter
workstream at operator direction ("rewrite to the new name at the same time")
instead of waiting for skill-renames-and-splits. That task's rename item is
thereby done; its remaining scope is the splits (git-commit et al.) and any
further renames. Context: lands with the f/role-dag-frontmatter squash-merge.

## [2026-07-20 19:45 CEST] Decision-022: write-to-s3 is placed at security/forensics
#roles #write-to-s3 #taxonomy #forensics #publication

`write-to-s3` declares `roles: [security/forensics]`, adopting Decision-003's
provisional placement as the declared value (the lint-era "needs a value"
question dissolves with Decision-020, but the placement ruling stands). The
publication question (pre-publication-cleanup) is unchanged.

## [2026-07-20 20:10 CEST] Decision-023: The close parallelises and verifies by presence
#close #housekeeper #orchestrator #workflow #performance #delegation

Two speed rulings on the close (operator, 2026-07-20, after a 15-minute close
on a docs-only feature):

1. On "close it" the orchestrator dispatches the housekeeper IN THE BACKGROUND
   and PREPARES the stream ingestion while it runs — but commits nothing to
   `main` until the housekeeper returns: two writers on `main` mid-merge is a
   race, and an uncommitted tree trips the housekeeper's clean-tree step.
2. The housekeeper verifies the close-gate by PRESENCE (named commits, files,
   sections in the branch tip), deep-reading only reported skips or failed
   checks; a failed check is the proven gap it fills and flags.

A third proposal — moving the `completed:`/`completed_during:` header fill to
the architect's close-gate — is REJECTED for now: the operator does not
currently trust the architect (it does not dispatch builders as contracted;
see the architect-delegation task). Re-evaluate when that is fixed.

## [2026-07-20 20:44 CEST] Decision-024: Orchard is the fleet workbench; the cross-repo bus keeps its own name
#orchard #naming #cross-repo #workbench #fleet

The codename **Orchard** now means the fleet workbench: the cross-repository
view, selection and dispatch UX the operator specified 2026-07-20 (global
overview of every repository's prepared work, counts of pressing/broken/
blocked issues, cross-repo dependencies, session-per-repo launch). Orchard
PRESENTS ONLY what each repository's orchestrator has already prepared — it
never derives or re-triages.

The live cross-repository messaging previously carried under the Orchard name
moves to its own task id, [[cross-repo-bus]], scope unchanged. References to
"orchard" in older docs (e.g. the message-bus sidecar) should be read as the
workbench programme from this date.

## [2026-07-20 21:35 CEST] Decision-025: The handover contract — the sidecar is the WHAT, the HOW is the architect's, delegation is mandatory above s
#handover #architect #orchestrator #delegation #sidecar #what-how #questions #cloud

Operator rulings (2026-07-20), the contract behind [[handover-contract]]:

1. **WHAT/HOW split.** The sidecar carries the complete WHAT — feature
   definition, scope, constraints, relationships, and the operator's scope
   answers. The orchestrator owns getting it complete. The HOW — discovery and
   technical design — is the ARCHITECT's job (that is the role), presented at
   the plan gate and frozen by MAKE IT SO; it is never required handoff
   content. (Amends the former §Sidecar wording "Proposal is the HOW the
   architect runs".)
2. **Two question rounds, not a ping-pong.** Scope (WHAT) questions are put to
   the operator while the task is parked in the readiness pipeline; the spawn
   itself carries only the LAUNCH round — model/effort scaling (Decision-019)
   and the parallel-launch offer. When several RELATED features are in play,
   ONE scope round defines the WHAT across all (or the chosen subset) before
   ANY architect launches, cloud or local. An open scope question at launch
   means the handoff broke; a mid-build scope question pauses the build and
   goes through the orchestrator, it is not asked ad hoc.
3. **Delegation is mandatory above s-size.** An architect build above s-size
   MUST dispatch builders; zero builders fails the close gate. An s-sized
   feature may be built inline, stated and justified in the close report. The
   former "directly or via parallel builders" permission was the bug
   (absorbed architect-delegation task). Restores the trust condition behind
   Decision-023's deferred header-fill move.

The cloud consequence: an autonomous/cloud architect has no mid-flight
operator contact, so rounds one and two are its hard precondition —
[[cloud-architect]] builds on this contract.
