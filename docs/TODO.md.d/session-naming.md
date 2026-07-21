- created: 2026-07-20
- created_by: Sebastien Lambla

## Blockers

- None.

## Questions

- ~~Inventory first: WHICH naming bugs?~~ Inventory done (Findings): the surface is
  mostly UNBUILT, not buggy — the task reframed from "fix N bugs" to "define the
  contract, enforce it forward".
- ~~Naming contract: what is the canonical short name?~~ Answered — operator contract
  (2026-07-21), see Proposal.
- ~~Does scope cover building the SessionStart hook, the orch wrapper, and
  parent-chain titling?~~ Answered: NONE of them. `claude --name` at launch IS the
  mechanism; enforce the rule moving forward; no retroactive rewrites. Epics /
  parent-chain naming explicitly deferred ("we'll ignore epics for now").
- ~~Retitle on every state change or spawn-only?~~ Answered: ride the existing bus
  lifecycle signals — no new hooks; anything else reads state off the bus.

## Findings

- Operator (2026-07-20): session/feature naming is buggy today, and short, descriptive,
  always-visible names are the PREREQUISITE for the whole Orchard UX — the sidebar
  ([[fleet-sidebar]]) is unusable without them. Typing/selecting a repository name must
  reliably reach that repo's orchestrator window.
- Inventory (confidence: high — read-only discovery, main checkout only): of the four
  naming paths described in the orchestrator docs, only the spawn-time
  `tmux select-pane -T "arch:<id>"` is real code. The SessionStart identity/titling
  hook, the `bin/orch` wrapper, the `.pending-subjob.local` consumer, and
  parent-chain worktree titling are documented intentions with no implementing script.
  Most of the surface isn't buggy — it's unbuilt.
- Operator amendment (2026-07-21, plan round): the plan's call-out read the root as
  `orchids / orchestrator` — wrong way round. The slash-form names workstreams; the
  orchestrator, singular per repository, is named by the repository itself.
- Operator scope ruling (2026-07-21): no hook build-out, no wrapper, no rewrites of
  what exists — `claude --name` at launch carries the session name; enforcement is
  forward-only at launch sites. Live state for consumers (sidebar included) comes from
  the BUS: any process — even a bash script — can register by creating an inbox folder
  and reading broadcasts.

## Proposal

The naming contract — strict, fully derivable, enforced at every launch site from now
on:

- **feature id**: kebab-case, all lowercase, the INVERSE of the git-imperative —
  git says "Eat carrots", the feature id is `eating-carrots` (gerund first; settled
  2026-07-21 over the earlier object-first example). Unique on the board; the sidecar
  filename. Forward-only — existing ids stay.
- **human name**: the feature id with hyphens as spaces ("eating carrots") — derived,
  never authored separately, so it cannot drift.
- **claude session name**: for WORKSTREAM sessions (architects, ripeners),
  `<repository> / <human name>` (e.g. `orchids / session naming`), passed with
  `--name` at every `claude` launch — this is what makes the claude UI navigable.
- **the orchestrator is NOT slash-form**: session names name SESSIONS, and there is
  exactly ONE orchestrator per repository — it orchestrates the workstreams. Its
  session name is the repository name alone (`orchids`); summoning or reviving it
  resumes THE one (never a second), and typing the repo name reaches its orchestrator
  (Decision-032).
- **one session per feature — the name never carries the agent**: the feature has ONE
  top-level session, shared context for all its work; everything else in it (builders,
  prep, sidecars) is a SUBAGENT — hidden away, never a named session, visible only in
  the sidebar thanks to the bus (activity broadcasts show them by name as they come
  and go). Which agent is doing what is live state, never name material. Two name
  shapes exist, total: `<repo>` (the orchestrator) and `<repo> / <human name>` (a
  feature workstream, e.g. `orchids / eating carrots`), all lowercase. Nothing else.
- **agent names appear NOWHERE** (operator + orchestrator concur, 2026-07-21): the
  hierarchy carries the role (the repo row IS the orchestrator; a feature session IS
  its one agent — a session can only have one agent), phase/activity words carry the
  state, and subagent rows carry their WORK label (the "messaging" pattern), never a
  role noun.
- **sidebar row**: the human name alone ([[fleet-sidebar]]).
- **tmux**: existing machine titles (`arch:<id>`) stay — tooling matches on them
  (teardown); titles refresh only where bus lifecycle signals already fire; no new
  hooks. Epics / parent chains deferred.

Enforcement is forward-only: launch sites (orchestrator architect spawn, cloud path,
future spawns) adopt `--name`; nothing is retro-renamed.

## Testing

Spawn an orchestrator and an architect: the claude UI lists
`<repo> / <human name>` for each; the id→human-name derivation round-trips for every
board id; the bus identity carries the same name; `tmux list-panes` still matches the
teardown's `arch:<id>` lookup.
