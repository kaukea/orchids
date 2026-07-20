- created: 2026-07-20
- created_by: Sebastien Lambla

## Blockers

- None.

## Questions

- Inventory first: WHICH naming bugs? Known candidates: mainline `/branch` forks
  mistitled as `<project> Orchestrator` (the `.pending-subjob.local` dance exists to
  patch it), worktree titles from the TODO parent chain, pane titles set at spawn but
  not maintained. Operator says "a number of bugs" — collect them before fixing.
- Naming contract: what is the canonical short name for a job — the feature id, the
  sidecar short title, or a new display-name field? Length budget for the sidebar?

## Findings

- Operator (2026-07-20): session/feature naming is buggy today, and short, descriptive,
  always-visible names are the PREREQUISITE for the whole Orchard UX — the sidebar
  ([[fleet-sidebar]]) is unusable without them. Typing/selecting a repository name must
  reliably reach that repo's orchestrator window.

## Proposal

Inventory the current naming paths (SessionStart hooks, `orch` wrapper, spawn commands,
pane/window titles), define one naming contract (repo, orchestrator, architect job,
coder pane), and fix each path to honour it. Titles update on state change, not only at
spawn.

## Testing

Spawn orchestrator + architect + coder across two repos: every session, window, and pane
carries its contract name; `tmux list-*` output is unambiguous; the names fit the sidebar
width budget.
