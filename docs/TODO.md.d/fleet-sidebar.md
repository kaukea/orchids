- created: 2026-07-20
- created_by: Sebastien Lambla

## Blockers

- ~~⊘[[session-naming]] — operator: without short, descriptive, visible names "none of it
  will work".~~ RESOLVED: session-naming is done (squash cfc7f28, archive/session-naming,
  2026-07-21) — the naming contract is in force for new launches.

## Questions

- ~~Data source for live state: bus consumer, or cheaper on-disk state?~~ Answered by the
  operator's issue #23 spec: the BUS — agents broadcast their current activity; subagents
  appear by name as they are called and return.
- ~~One global sidebar per client, or one per session?~~ Answered: mounted in every
  session, always visible by default, always showing the SAME global content (one
  renderer, n mounts).
- ~~Implementation: a TUI in a pinned pane — anything better?~~ Answered: a pinned LEFT
  pane sized to 1/6th of the width (to be refined from actual usage); the
  TUI-in-a-pane shape stands.

## Findings

- Operator (2026-07-20), verbatim requirements: at any new session, a SMALL LEFT PANE,
  ALWAYS VISIBLE, shows each repository and each architect job with its current state —
  waiting-for-input / actively-working / completed — with nice emojis. The pane is
  focusable and navigable: selecting an entry jumps to that session/task. Tasks also show
  their PHASE: in design (with the orchestrator) vs in active development (with the
  architect). Bonus, addable later: the cleanup/close state.
- Explicitly the mitigation for the UX overload of session-per-repo × window-per-task ×
  pane-per-coder ([[tmux-topology]]).
- GitHub issue #23 ("Navigate work in progress across repositories and agents",
  operator-filed) duplicated this task; merged 2026-07-21 — stub entry and sidecar
  removed, the `gh#23` badge binds here. Spec details from the issue body:
  - Status vocabulary, one emoji each: Waiting on user · Running (actively doing
    something) · Standby (work complete, not closed) · Completed · Failed.
  - An entry waiting on the operator (question asked / operator-blocked) FLASHES.
  - Navigation maps the tmux topology: session = repo, window = feature, pane =
    activity (an orchestrator may have several activities).
  - Agents broadcast their current activity to the bus (Questioning, Analyzing,
    Thinking, …) — that text is the row's activity label; subagents are displayed by
    NAME only, as they get called and come back, to give a sense of what is going on.
  - Emoji and animated / full colours welcome.
- Operator refinement (2026-07-21, ruled during [[session-naming]]): hierarchy is
  repo (select → that repo's orchestrator, first window) → each feature underneath →
  what is HAPPENING underneath that → subagents underneath when active. NO agent/role
  names anywhere — structure carries the role, activity carries the state, subagent
  rows carry their work label (e.g. "messaging").

## Proposal

A pinned left pane, 1/6th of the client width (refine from real usage), always visible
by default in every session, every session rendering the same global content: rows =
repository → feature/job → activity, each row carrying its phase and a status emoji
from {Waiting on user, Running, Standby, Completed, Failed}; rows needing the operator
flash. Keyboard up/down navigation; selecting an entry switches the client to the
repo's session, the feature's window, the activity's pane. Live state comes from the
bus: agents broadcast ON EVERY ACTIVITY CHANGE (event-driven — the sidebar never
polls), subagents show by name while in flight; names per [[session-naming]]. The
existing lifecycle signals (Decision-028: started/building/testing/…) are COARSER
than activity (Questioning, Analyzing, Thinking, …) and do not replace this — the
activity broadcast is a new bus surface this feature requires.

## Testing

Two repos, three jobs in mixed states: sidebar shows all three correctly (including
one waiting-for-input surfaced within seconds AND flashing), keyboard navigation lands
on the right session/window/pane, and a completed job's row updates when its window
closes.

## Result

Result: done (pending operator manual visual pass) — built, unit-tested, end-to-end
smoke passing. Awaiting the operator's `THAT IS ALL`.

- Branch: `worktree-fleet-sidebar` @ `711d761`. Base `1a9be79` (anchor `234a9a8`,
  `Base:` trailer). No merge commits; squash-merge is the housekeeper's.
- Commits: `7bdb8bd` activity broadcast wiring · `7d62f20` nav · `5f3a517` bus reader ·
  `c8acc6e` mount · `af8dd5e` renderer · `1560a58` tests · `711d761` architecture.
- Method (operator-agreed): pytest-style unit tests + operator manual visual pass.
  - Unit tests: `python3 -m unittest discover -s tests` → **23/23 OK**, run by the
    architect (not just the builder). pytest is not installed here; tests are stdlib
    `unittest` and pytest-collectible.
  - End-to-end smoke (architect-run, throwaway 2-repo/3-job fixture through the real
    reader→model→renderer): repos aggregated; widget-x running 🟢 + sub-agent spinner,
    report-gen standby 🟡, auth-flow waiting ⏳ that blanks on the flash-off frame →
    **PASS**.
  - OUTSTANDING (operator's part of the agreed method, needs a live TTY): the visual
    flash animation, live keyboard up/down + Enter navigation landing on the right
    window, and a row updating when a job's window closes. The feature stays OPEN
    until the operator confirms this pass.
- What was built: a new bus surface was NOT added (operator ruling) — agents broadcast
  dynamic `orchid:activity:<text>` and `orchid:subagent:start|done:<label>` messages on
  the existing bus (`agents/orchestrator.md`, `architect.md`, `ripener.md`). A Python
  stdlib reader (`tools/sidebar_model.py`) observes every configured repo's bus,
  attributes by sender, accumulates in memory; a curses renderer (`tools/sidebar.py`)
  draws the repo→feature→activity→sub-agent tree with status emoji, flash, and spinner,
  with keyboard nav via `tools/sidebar_nav.py` (matches tmux WINDOW names `arch:<id>` /
  `orch:<repo>`); `tools/sidebar-mount.sh` splits the pinned left pane at
  orchestrator/architect launch (idempotent, strictly best-effort).
- Fan-out: discovery 6 explorers (0 inline); build 6 builders (S1–S6), plus the
  ARCHITECTURE.md edit inline (architect, per Decision-034). Above s-size; builders used
  throughout, none of the six build steps done inline.
- Known limitations (non-blocking): reader dedup is cross-scan by message id (real
  envelopes use uuid4, so same-scan collisions can't occur); a repolist entry with no
  bus activity shows an empty repo row. Cross-repo repo-discovery is an explicit
  repolist by design — the fleet-wide discovery decision is left to Orchard.
- Related tasks: `cloud-event-feed` was blocked on this initial run and is now
  unblockable; `cross-repo-bus` / `orchard-view` carry the deferred repo-discovery
  decision. (Board updates are the orchestrator's.)

## Changelog entry

### Added
- **Fleet sidebar** — a pinned left pane now appears in every orchestrator and
  architect window, showing a live, cross-repository tree of work: each repository,
  the features under it, what each is doing right now, and any in-flight sub-agents,
  sourced entirely from the message bus. Rows carry a status emoji (running, standby,
  completed, failed), flash when an agent is waiting on the operator, and can be
  selected with the arrow keys and Enter to jump straight to that work's tmux window.
  Which repositories it aggregates is listed in `~/.config/orchids/sidebar-repos`
  (one path per line) or the `ORCHIDS_SIDEBAR_REPOS` environment variable; with
  neither, it shows the current repository.

## Readme delta

- Document the fleet sidebar: what it shows (the live repo→feature→activity→sub-agent
  tree from the bus), that it mounts automatically as a pinned left pane in
  orchestrator and architect windows, keyboard up/down + Enter to navigate to a row's
  window, and how to choose which repositories it aggregates
  (`~/.config/orchids/sidebar-repos`, one repo path per line, or `ORCHIDS_SIDEBAR_REPOS`).
- Note the sidebar's data source: agents broadcast `orchid:activity:<text>` (and
  `orchid:subagent:start|done:<label>`) on the message bus; the sidebar renders it. No
  new bus mechanism — ordinary dynamic messages.

## Architecture

Updated `ARCHITECTURE.md` on-branch (commit `711d761`): new "The fleet sidebar" section
(component, data-flow bus→sidebar→tmux, repolist discovery), a bus-section note on the
new dynamic activity/sub-agent messages, and the `tools/` layout listing. Triggers fired
— a component added and a new data-flow — so the edit was required, not skipped.
