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
