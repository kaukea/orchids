- created: 2026-07-12
- created_by: fable-5

## Blockers
- none

## Questions
- ~~(a) drop the Stop hook, or (b) architect as orchestrator-dispatched subagent?~~
  RULED (operator, 2026-07-20): neither as posed — **the finishing hooks are replaced by
  MESSAGE BUS choreography.** The close handshake (THAT IS ALL / ALL IT IS → return
  focus, cleanup) and end-of-session signalling ride the repo bus, not
  transcript-grepping Stop hooks. Include the bus fixes needed for reliable usage
  (the liveness gap: announce proves load, nothing catches a mid-session death —
  [[bus-liveness]]; metadata on the bus — [[agent-metadata]]).

## Findings
- architect-close.sh greps transcripts with jq, juggles tmux sockets, fails silently;
  the operator distrusts it. Worktree sessions also ran with broken relative skill
  symlinks pre-orchids (absolute links fixed that) — part of the past pain.
- 2026-07-20 close-miss diagnosed (role-dag-frontmatter close): the hook's
  `jq -s` slurp dies on a partial trailing transcript line — the Stop hook races
  the harness's final append (transcript mtime 19:38:25 vs hook fire 19:37:33) —
  so extraction collapses to `''` and the countersign never matches. Reproduced
  by truncating the transcript tail. A per-line `jq -R 'fromjson?'` parse over
  the same truncated file still extracts `ALL IT IS`; operator ruled to leave the hook
  broken and replace the mechanism (this task).
- The shared settings.json Stop entry fires the hook in EVERY session on the
  box, and on no-match it logs that session's last-message tail to
  /tmp/architect-close.log — cross-session conversation content leaks into a
  /tmp file. The replacement kills this leak.
- [[tmux-topology]] reshapes the same choreography (window-per-architect, focus
  return on close) — co-design so the bus signals drive whatever layout is current.

## Proposal
Close and finishing choreography over the message bus: the architect signals its
lifecycle on the bus; the orchestrator (or its bus sidecar) acts on those signals —
focus return, pane/window cleanup, close dispatch — with no transcript parsing
anywhere. Fix the bus reliability gaps this depends on. HOW — signal set, who
listens, hook retirement order — is the architect's tech plan (Decision-025/027).

## Testing
One full feature cycle (spawn → MAKE IT SO → THAT IS ALL/ALL IT IS → close) driven
end-to-end by bus messages: focus returns, the architect's pane closes, no
architect-close.sh in the path, and /tmp/architect-close.log records nothing. A
deliberately killed architect is detected rather than silently absent.

## Result
Result: done — branch f/hook-choreography @ 3d18aa74de3e51ca08403a43325fdbe1df9f164e (base 380fb54; main advanced to 19d37d3,
housekeeper integrates at squash-merge). 6 commits: bus.py signal+metadata (🎉 anchor) ·
bus-driven close wiring (bus.md/architect.md/orchestrator.md + architect-teardown.sh) ·
retire Stop hook · same-window teardown bugfix · ARCHITECTURE.

Built: architect emits bus lifecycle signals (`done`@gate, `finished`@countersign); orchestrator
acts on `finished` — runs tools/architect-teardown.sh (focus-return + close the arch:<id> pane,
found by TITLE) then dispatches the housekeeper. Operator's THAT IS ALL is the sole close gate;
"close it" removed. Retired hooks/architect-close.sh + its Stop entry + /tmp leak + jq race.
model+effort added to orchid:status (mutable), not identity. parent_session wired at spawn.
Liveness = direct pane check, no scheduler.

Tested (operator-agreed: integration proof accepted; first post-merge close = live confirmation):
- bus.py signal (real isolated bus): directed-to-parent / broadcast-fallback / dead-parent-fallback /
  invalid-state-reject — all pass, envelope {kind:lifecycle,state,feature_id} correct.
- architect-teardown.sh (real tmux, same-window Decision-006 layout): arch pane closed, orch pane
  spared, focus returned, safety-refusal correct, killed pane detectable.
- FULL close ordering chained on real bus+tmux: finished → drain → teardown → orch alive / arch closed / focus back.
- Caught+fixed a guard bug (arch_win==ret_win) that would have refused every real close.
Untested pre-merge (impossible until synced): a live LLM following the new md prose — the first
post-merge feature close is that confirmation.

## Docs determinations (per file)
- decisions.md: NOT written here — technical design decisions staged in the workstream log's
  "Decisions (pending promotion)" for orchestrator promotion at ingestion (avoids number collision
  with advanced main; decisions.md is the orchestrator's per shared rules).
- CHANGELOG.md: EDITED — added the 🎭 "Close choreography on the bus" bullet (operator-gated: approved).
- ARCHITECTURE.md: EDITED — triggers fired (component removed: architect-close.sh; added:
  architect-teardown.sh; wiring changed: close path hook→bus). Updated the role table (architect
  countersign→finished; housekeeper trigger no longer "close it") + repo-layout inventory.
- README.md: SKIP (evidenced) — README describes the close/bus only at narrative altitude
  ("the housekeeper runs the close", "every session loads a bus"); it names no Stop hook, no
  handshake mechanism, no "close it". All those statements remain true, so nothing to align.

## Follow-ups for the orchestrator (cross-task — not edited by me)
- [[agent-metadata]]: FOLDED IN and satisfied here (model+effort on status; which-wins resolved by
  keeping mutable metadata on status). `effort` ships null — no reasoning-effort env source exists
  today; revisit if one appears. Orchestrator can mark agent-metadata done/superseded.
- [[bus-liveness]]: close-scoped liveness delivered (direct pane check); the broad reachability
  framework ("what evidences reachability after load / what acts on absence") remains its own task.
- [[tmux-topology]]: its sidecar's "current mechanics this replaces: .return-window + the
  architect-close Stop hook" is now partly stale — teardown is topology-agnostic (reads .return-window,
  finds pane by arch:<id> title); window-per-architect can swap the teardown action without touching signals.
