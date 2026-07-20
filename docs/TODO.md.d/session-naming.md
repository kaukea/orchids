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
- Given the inventory shows the SessionStart identity/titling hook, the `orch` wrapper,
  and the TODO-parent-chain worktree titling are all UNBUILT (only the one-shot
  `tmux select-pane -T "arch:<id>"` at spawn is real code) — does this task's scope
  cover building those three mechanisms from scratch, or is it narrower (e.g. only
  fixing the one real titling call, with the rest split into a follow-up task once
  `fleet-sidebar` defines what the sidebar actually needs)?
- Should titles update on every relevant state change (spawn, return, close), which
  requires a hook at each of those points, or is spawn-time-only naming acceptable for
  a first cut given `fleet-sidebar` is the actual consumer and not yet built either?

## Findings

- Operator (2026-07-20): session/feature naming is buggy today, and short, descriptive,
  always-visible names are the PREREQUISITE for the whole Orchard UX — the sidebar
  ([[fleet-sidebar]]) is unusable without them. Typing/selecting a repository name must
  reliably reach that repo's orchestrator window.
- Inventory (confidence: high — read-only discovery this session, main checkout only,
  did not touch `.claude/worktrees/*`):
  - **`bin/orch` does not exist.** There is no `bin/` directory in this repo at all. The
    `orchestrator` skill (`skills/orchestrator/SKILL.md` "Renewal & summon") documents a
    wrapper doing `claude --resume "<project> Orchestrator" || claude --name "<project>
    Orchestrator"` — this is aspirational prose, not a shipped script. No naming bug can
    be fixed here because the mechanism isn't built yet.
  - **No SessionStart identity/titling hook exists.** `.claude/settings.json`'s only
    `SessionStart` hook is `.claude/hooks/bus-init.sh`, which does exactly one thing:
    `bus.py init` + prompt the model to load its bus sidecar. It sets no title, reads no
    TODO parent chain, and does not distinguish orchestrator vs worktree vs mainline
    sub-job. The "SessionStart role hook injects identity" and "titles it with the
    hierarchical TODO `parent` chain + a type emoji (e.g. `♻️ harden-modularize >
    harden-role-profiles > conn-noise`)" described in `skills/orchestrator/SKILL.md`
    ("Identity — am I the orchestrator?") is likewise undocumented-as-built: no hook
    script implementing it exists anywhere in the repo (only `bus-init.sh`,
    `architect-close.sh`, `bus-end.sh` are registered). **The parent-chain worktree
    titling the task description asks me to inventory does not exist in code** — it is a
    design description only.
  - **`.claude/.pending-subjob.local` has no consumer.** The mainline `/branch` fork
    identity dance (`agents/orchestrator.md` and `skills/orchestrator/SKILL.md` both
    describe it: write the feature id to `.claude/.pending-subjob.local` before telling
    the operator to `/branch`, then "the fork's `SessionStart` consumes that token,
    records its own `.claude/.subjob-<session_id>.local`, and titles itself via the TODO
    `parent` chain") has no implementing script in this repo. The file is gitignored
    (`.gitignore` lines 3-5: `orchestrator-mode.local`, `.pending-subjob.local`,
    `.subjob-*.local`) so its shape is reserved, but nothing reads or writes it today
    except the orchestrator's own prose instructions to itself.
  - **The one titling call that IS real is single-shot, at spawn only.**
    `agents/orchestrator.md` step 2 (worktree architect spawn) runs
    `tmux select-pane -T "arch:<id>"` right after `tmux split-window`. This is a real,
    working tmux call — but it fires once at spawn and nothing updates it afterward
    (no state-change hook, no rename on architect close/return). `hooks/architect-close.sh`
    on return does `tmux select-window`/`select-pane`/`switch-client` to navigate back to
    the orchestrator's pane, but never renames/retitles anything — it moves focus, it
    doesn't relabel.
  - No other `tmux rename-window`/`set -g pane-border-format`/`-T` calls exist outside
    `agents/orchestrator.md` and `hooks/architect-close.sh` (grepped root-level `.md`/
    `.sh` files, worktrees excluded).
  - Net picture: of the four paths named in the task, only ONE (`arch:<id>` pane title
    at spawn) is actually implemented code; the SessionStart identity/titling hook, the
    `orch` wrapper, and the TODO-parent-chain worktree titling are all documented
    *intentions* in the two orchestrator docs with no corresponding script. This
    reframes "a number of naming bugs" — most of the surface isn't buggy, it's
    unbuilt. (Confidence: high for "no such file exists in this checkout"; cannot
    speak to whether it exists in a currently-open worktree, which I did not touch.)

## Proposal

Discovery inventory is done (see Findings) — the naming surface described in
`agents/orchestrator.md`/`skills/orchestrator/SKILL.md` is mostly undocumented-as-built
rather than merely buggy, which changes the shape of this task from "fix N bugs" to
"decide the contract, then build the SessionStart identity hook, the `orch` wrapper, and
retitle-on-state-change, plus keep the one real spawn-time `tmux select-pane -T` call
consistent with whatever contract is chosen." Left open pending the operator's answers
below — do not propose a build plan until the naming contract and canonical short-name
source are settled.

## Testing

Spawn orchestrator + architect + coder across two repos: every session, window, and pane
carries its contract name; `tmux list-*` output is unambiguous; the names fit the sidebar
width budget.
