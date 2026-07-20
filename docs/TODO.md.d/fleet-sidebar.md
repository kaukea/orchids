- created: 2026-07-20
- created_by: Sebastien Lambla

## Blockers

- ⊘[[session-naming]] — operator: without short, descriptive, visible names "none of it
  will work".

## Questions

- Data source for live state: the message bus already carries identity/status
  ([[bus-liveness]], [[agent-metadata]]) — is the sidebar a bus consumer, or does it read
  cheaper on-disk state? (A dead sidecar goes silent either way — liveness matters.)
- One global sidebar per client, or one per session? It lists EVERY repo and job, but tmux
  panes belong to a session — a global view in every session means one renderer, n mounts.
- Implementation: a TUI in a pinned pane (watch-style refresh) is the obvious shape —
  anything better?

## Findings

- Operator (2026-07-20), verbatim requirements: at any new session, a SMALL LEFT PANE,
  ALWAYS VISIBLE, shows each repository and each architect job with its current state —
  waiting-for-input / actively-working / completed — with nice emojis. The pane is
  focusable and navigable: selecting an entry jumps to that session/task. Tasks also show
  their PHASE: in design (with the orchestrator) vs in active development (with the
  architect). Bonus, addable later: the cleanup/close state.
- Explicitly the mitigation for the UX overload of session-per-repo × window-per-task ×
  pane-per-coder ([[tmux-topology]]).

## Proposal

A pinned narrow pane running the fleet-status renderer: rows = repo → job, columns =
phase + state emoji; arrow-key navigation, Enter switches client to the target
session/window. State sourced per the data-source Question; names per
[[session-naming]].

## Testing

Two repos, three jobs in mixed states: sidebar shows all three correctly (including one
waiting-for-input surfaced within seconds), navigation lands on the right window, and a
completed job's row updates when its window closes.
