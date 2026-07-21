- created: 2026-07-21
- created_by: fable-5
- created_during: orchestrator session (operator report)
- completed: 2026-07-21
- completed_during: f/agent-closing

## Blockers

- None.

## Questions

- ~~Bus lifecycle: what releases a bus sidecar?~~ RULED (operator, 2026-07-21,
  Decision-041): parent release at close PLUS the bus self-exits when its
  parent is gone (the inbox watch doubles as the liveness monitor).
- ~~Who kills panes/sessions at close?~~ RULED (operator, 2026-07-21,
  Decision-041): the CLOSING AGENT kills itself — self-teardown is the last
  charter step; the orchestrator reaps only an agent that died first.
- ~~Charter text or mechanical enforcement?~~ RULED (operator, 2026-07-21,
  Decision-041): charters only — no verification apparatus, no reaper pass.
- ~~Which live-fire defects are in this corrective's scope?~~ RULED (operator,
  2026-07-21, scope round): IN — (1) teardown pane handle: re-key
  `architect-teardown.sh` and reaping off the clobbered `arch:<id>` pane title
  onto a stable handle (e.g. a tmux window user-option) — this task OWNS the
  stable-handle mechanism; the parallel sidebar-fixes corrective consumes it
  for its mount-idempotency defect, so define the handle as a small stable
  contract (name it in your plan); (2) bus wake/monitor
  teardown: the bus never wakes, never tears its monitor down, the monitor
  stays up and the architect never closes — deliver the active-wake mechanics
  (Decision-046) so closes wake the bus and the bus verifiably kills its
  watcher before departing; (3) premature bus release: charter pins release to
  the parent's close only, never an errand's end. OUT (explicit voluntary
  deferral): the `_closed`-marker-ordering tightening.
- ~~How does an operator approval reach the architect at the done gate?~~
  RULED (operator, 2026-07-21, Decision-047): a sanctioned operator relay — an
  operator-origin message class on the bus that gate-waiting agents accept;
  relayed verbatim, flagged operator-origin, never peer traffic. Mechanics are
  in scope for this corrective.

## Findings

- Operator report (2026-07-21): closes get stuck because agents do not clean up
  after themselves and do not close their sub-agents — the flow cannot finish.
- Observed instances, same session: the bus charter guaranteed it never returns
  while the end-of-task guard required no sub-agent in flight (structural
  contradiction); an architect's bus still announcing after its `finished`
  signal; two live orchestrator-role sessions with nobody retiring one.
- Delivered (2026-07-21, orchestrator on main): Decision-041 recorded; bus
  charter gains the Release section (released ⇒ depart + end; orphaned ⇒ end);
  architect charter gains self-teardown (release bus + architect-teardown.sh as
  final act, also on blocked/abandoned); orchestrator charter drops the
  teardown act, keeps it only as dead-agent fallback, and releases its own bus
  at retirement; handover guard counts a released bus as returned and the
  stream close gains a teardown step.
- Live-fire evidence from the fleet-sidebar close (2026-07-21), all verified:
  - `architect-teardown.sh` matches the architect pane by pane TITLE `arch:<id>`,
    which claude clobbers live with the session name — teardown finds no pane and
    neither returns focus nor closes it. Fix: match a reliable handle (window
    name, or a tmux window user-option), not the clobbered pane title. The same
    clobbering breaks reaping's pane-title check.
  - A bus blocked on its monitor never exits on its own: it must be WOKEN by an
    inbound message and tear its monitor down itself; killing the monitor
    externally leaves the bus asleep forever (Decision-046). Passive
    watch-and-wait makes closes take tens of minutes; closes must wake actively.
  - The native `--worktree` launcher (wrapper claude process) outlives its child
    architect and holds a blank window until reaped.
  - The architect never touched its stream's `_closed` marker before teardown
    (protocol orders it first); ingestion proceeded without it.
  - An operator approval given in the ORCHESTRATOR pane has no sanctioned
    delivery path to the architect: the bus relay is (correctly) rejected as
    peer traffic, and the flow silently stalls at the done gate until the
    operator types in the architect's own window (or keystrokes are injected).
  - One session's bus released itself after completing a relay errand, mid-parent-
    session — release belongs to the parent's close, not an errand's end.

### Delivered — agent-closing corrective (2026-07-21, architect on f/agent-closing)

Four deliverables, all committed on f/agent-closing (base 8203b6f):
- D1 stable handle: architect windows gain a `@arch_id=<id>` tmux WINDOW user-option at
  launch; `architect-teardown.sh` and orchestrator reaping resolve the window by
  `@arch_id` and close at WINDOW granularity (taking the mounted sidebar pane with it) —
  immune to the pane-title clobber. The `arch:<id>` pane title is kept only as a
  non-load-bearing human hint. `@arch_id` is the small stable contract sidebar-fixes
  consumes for mount idempotency.
- D2 bus active-wake (Decision-046): `agents/bus.md` now frames release as an inbound
  WAKE (never an external monitor-kill); the existing teardown + verify-watcher-dead
  sequence stays. Orphan path left as the watch-dies exit (not a wake) by design.
- D3 premature release: `agents/bus.md` gains an explicit "an errand's end is NEVER a
  release" rule; release is pinned to parent close or orphaning only.
- D4 operator relay (Decision-047): `operator_origin` envelope flag added to
  `tools/bus.py` + `tools/message.schema.json` (present-and-true-only, mirrors
  `notify_user`; `--operator-origin` on send/broadcast); `agents/bus.md` relays it
  verbatim and surfaces it distinctly from peer prose; `agents/architect.md` Phase 4
  honors an `operator_origin`-flagged `THAT IS ALL` as the operator's own close;
  `agents/orchestrator.md` relays the operator's gate word typed in its own pane.
  Operator ruled the relay stays LITERAL to Decision-047 (no conductor-only hardening)
  — the security scanner's spoofable-bypass flag is an ACCEPTED, sanctioned trade-off
  under the cooperative single-operator trust model (no bus message is authenticated).

ARCHITECTURE determination: EDITED (`ARCHITECTURE.md`, commit 3660f27). Triggers fired —
"how components connect" (teardown/reaping re-keyed onto `@arch_id`) and a new
cross-cutting pattern (operator-origin relay data-flow). Recorded, not skipped.

Result: **done** · branch `f/agent-closing` @ HEAD `3660f27` (6 commits; 🎉 anchor
`d24f10a`, `Base: 8203b6f`) · Tested (agreed layered method): unittest suite 27/27
(5 new operator_origin tests) + teardown tmux integration test PASS — both run by the
architect in-session; the charter/behavior half (active-wake, premature-release,
done-gate honoring, reaping) is UNVERIFIED until the next live close, stated plainly ·
Tasks spawned: none · Proposed Decision-048 (the `@arch_id` handle ruling) and the
operator-relay ruling are recorded in the workstream log for orchestrator promotion; a
cross-file Decision-046/047 number collision in `skills/*.md` is flagged for the
orchestrator to reconcile (not touched — decisions.md is the orchestrator's).

## Proposal

Make close mean CLOSED, by charter text alone (Decision-041): a bus is released
at close or self-exits when orphaned; the closing agent's last act is its own
teardown (bus, pane, session); parents reap only the dead. Delivered as charter
amendments — see Findings.

## Testing

First live release (2026-07-21, this orchestrator's own bus): the agent
released and departed cleanly, but its armed Monitor — the persistent
inotify watch on the inbox — OUTLIVED it, visible to the operator as an
open watcher on a sleeping session; a second zombie watcher from an
already-dead session was found beside it. Both killed by hand. The bus
charter now orders: stop the Monitor and VERIFY the watcher process is gone
before departing, on both the release and the orphan paths.

Agreed shape (pending its live run): the NEXT feature close is the test —
after `THAT IS ALL` / `ALL IT IS`, observe that no bus, pane, session, or
sub-agent of the closed feature remains (tmux list-panes, bus roster). Until
that observation, this stays open.

Method agreed for the agent-closing corrective (operator, 2026-07-21): LAYERED —
(a) unit test for the operator_origin flag; (b) a tmux integration test for the
re-keyed teardown; (c) the charter/behavior half rides the next live close.
Results:
- (a) `python3 -m unittest discover -s tests` → 27/27 (5 new `operator_origin`
  tests: envelope round-trip, schema validity, send + broadcast receive) — PASS,
  run by the architect in-session.
- (b) teardown tmux integration test — PASS, run by the architect on a scratch tmux
  server: a window carrying `@arch_id=verify` but a clobbered `some-clobbered-session-
  name` pane title was resolved via `@arch_id`, focus returned to the return pane, the
  window killed, exit 0.
- (c) active-wake, premature-release, done-gate honoring, and reaping are agent-behavior
  changes provable only at a live close — UNVERIFIED-until-live, stated plainly. This
  session's own self-teardown is the first live exercise of the re-keyed teardown.

## Changelog entry

### 🐛 Bug fixes

- 🚪 Feature closes now actually complete. Teardown and reaping resolve the architect
  window by a stable `@arch_id` tmux window user-option instead of the `arch:<id>` pane
  title that `claude` clobbers live — so the close returns the operator's focus and kills
  the architect window (with its mounted sidebar pane) instead of stalling. The bus now
  exits only when woken by an inbound release message and tears down its own inotify
  watcher before departing (never left asleep by an external monitor-kill), and an
  errand's end is never mistaken for a release (Decisions 041/046).
- 🖖 Operator approvals reach a gate from any pane. An approval typed outside the
  architect's own window (typically the orchestrator pane) relays over the bus as a
  distinct operator-origin message class the architect honors as the operator's own
  `THAT IS ALL`; ordinary peer traffic still never closes a gate (Decision-047).

## Readme delta

No change — evidenced. README describes the gates at the contract level ("your comments
are the gates", "no gate ever approves itself" — README.md:102-104; "your explicit
approval" :57) and never documents which pane an approval is typed in. This corrective
fixes internal delivery robustness (the close completes; an approval reaches the gate)
without adding a documented user capability or changing a usage instruction, so no
README section becomes inaccurate. Checked README.md:23,57,102-104.

### First live observation (orchestrator, 2026-07-21 21:5x, this feature's own close)

- PASS — bus half: the architect's bus released, departed, and its inbox
  watcher was verifiably gone (pgrep observation; remaining watchers all
  belonged to live sessions).
- FAIL — window half: the architect window survived with the live session in
  it; NO `@arch_id` was observed on the window despite the stream log's
  bootstrap claim, so the patched teardown found no window and exited without
  killing. Cause reads as a missed bootstrap on a pre-fix window, not a defect
  in the delivered path (future windows get `@arch_id` from the amended launch
  recipe). Orchestrator reaped as the dead-agent fallback (window-granular).
- Next observation: the sidebar-fixes close — its window carries a bootstrapped
  `@arch_id=sidebar-fixes` (readback verified), so it exercises the delivered
  teardown end-to-end.
