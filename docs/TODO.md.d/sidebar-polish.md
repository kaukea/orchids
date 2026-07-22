# Sidebar polish: the second corrective round from the operator's live pass

- created: 2026-07-22
- created_by: Sebastien Lambla

## Blockers

- None hard. Independent of the [[sidebar-fixes]] close — that task gates on its
  own recorded result; this round collects everything the operator's live pass
  found beyond it.

## Questions

- ~~Per-agent colors: which palette?~~ RULED (operator, 2026-07-22): build
  against the **8 most popular orchid colours** — an orchid-species
  palette (e.g. the whites, pinks, purples, magentas, yellows, oranges,
  greens and blues orchids actually come in), NOT the ANSI set. Operator
  eyeballs the live pane and corrects any hue that reads wrong.
- ~~Bus singleton: design question?~~ RULED (operator, 2026-07-22,
  Decision-051): the bus sidecar is a singleton PER AGENT — exactly one
  each, duplicates/orphans are the defect, correctived in
  [[bus-singleton]]. This round renders exactly one bus row per live
  agent: top of the list, italic, greyed, 📬.
- Emoji set for the status vocabulary (operator invites proposals; current
  proposal in the item below).
- ~~/orchard `add <path>`: what counts as "an orchids installation"?~~
  RULED (operator, 2026-07-22): `.ai.toml` presence is SUFFICIENT for now —
  other repos will exist in the future, and richer detection is deferred to
  the low-priority follow-up [[install-detecting]], blocked on the real
  kauk CLI shipping.

## Findings

- Item 7's build (registry-based dynamic appearance) supersedes
  `docs/decisions.md` Decision-043 ("Fleet sidebar aggregates via an
  explicit repolist — Orchard's discovery deferred") — flagging for the
  orchestrator to promote/record at ingest, not written by this architect
  directly per the decisions.md convention.
- Item 7's build also leaves three docs stale, describing the retired
  default-repolist-file behavior: `README.md:50`, `CHANGELOG.md:80-81`,
  and (cross-task, not this sidecar) `docs/TODO.md.d/fleet-sidebar.md:131-141`
  — the first two are staged in this sidecar's Result at close
  (Decision-034); the third belongs to a different task's sidecar and is
  noted here only as a pointer for the orchestrator to relay.
- Operator live pass, 2026-07-22, on the sidebar-fixes branch build mounted in
  his window. Some of the duplicate bus rows observed were real duplicates:
  the orchestrator session that morning had spawned a second bus sidecar by
  mistake, so multiplicity was partly genuine process noise, not only a
  display defect.
- "app-identifying" as a permanent first row: that feature closed 2026-07-21 —
  the row is stale state (likely a leftover bus/state file); the fix should
  find and clear the source, not just hide the label.

**Result: done.** Branch `f/sidebar-polish`, HEAD `e97a8d7` (post this write:
the sidecar-only commits closing this out land after). All 12 proposal items
(including the mid-build item-7 revision, item-2 extension, and item-12
sub-refinements a–g) built, merged, and unit-tested — 184/184 passing. The
live-only piece (item 12's bus-popup mechanism) was exercised directly with
the operator across three rounds, catching and fixing two real defects unit
tests couldn't reach (Enter-required keypress, invisible echo). See
`## Testing`'s "Actually run" subsection for the full breakdown, including
what still lacks a live pass (auto-mount at orchestrator boot, exit-grace
kill enforcement, popup multi-select/gate-keyword paths specifically).
Sub-agents dispatched this build: 6 read-only discovery explorers (Phase 1)
+ 9 builders (core rendering/status/filtering/aggregation/color/gradient,
auto-mount, viewport scroll, exit-grace lifecycle, title derivation, Orchard
registry, bus-popup mechanism round 1, bus-popup polish round 2) + 0 steps
built inline by the architect except two small, well-understood post-live-test
bug fixes (the os.read fix and the echo-linger fix — both under 15 lines,
directly diagnosed from live operator feedback, justified inline rather than
another builder round-trip) and the exact-wording fix a builder correctly
declined as outside its assigned scope. No task spawned outside this
feature's own scope beyond what's flagged above (Decision-043 supersession,
stale README/CHANGELOG/fleet-sidebar.md pointers — all noted for the
orchestrator to promote/relay at ingest).

## Proposal

The operator's itemized list, verbatim in substance:

1. **Drop the hourglass** ("sablier") task animation entirely — each time it
   disappears the task text shifts left and back. No spinner glyph; layout
   must never shift with state.
2. **Hide internal rows**: "app-identifying" (always first, internal, stale —
   see Findings) and the bare session-UUID row. Neither is operator-facing.
   EXTENDED (operator via orchestrator, 2026-07-22, operator-origin relay,
   req d9684a605004): beyond those two, ANY feature row whose lifecycle has
   ENDED must actually leave the sidebar — live case: `agent-closing`,
   which closed 2026-07-21 with a proper `finished` signal on the bus, still
   renders as the first task row today. Find and clear whatever state
   source keeps ended features alive (stale bus/state files surviving
   their lifecycle message, or the reader never pruning them) — do not
   just filter known names; the fix must generalize to any future ended
   feature, not special-case `agent-closing`/`app-identifying` by name.
   Secondary check folded in: confirm the "all subtask rows animate
   simultaneously" symptom is fully subsumed by item 1's animation
   removal; if any animation source survives item 1's fix, kill it there
   too.

   BUILD FINDING (core-rendering builder, 2026-07-22): eviction was
   implemented as evict-on-*observed* terminal signal, but live-checked
   against this repo's real bus data, `agent-closing`'s `finished` message
   was already drained from disk before any aggregator scan ever saw it —
   so this specific case still renders stale. Evict-on-observed-signal is
   necessary but not sufficient.

   RESOLVED (operator, 2026-07-22, direct): the real fix is a lifecycle
   contract, not a sidebar timeout — an agent leaves on its own accord when
   done by sending two messages then cleaning up and exiting; it gets 10
   seconds to do so. If it hasn't exited by then, the ORCHESTRATOR kills
   it — unless the agent specifically asked for more time when it
   announced its presence. For the sidebar to observe this and evict
   correctly (reusing the already-built evict-on-observed-terminal-signal
   logic), the orchestrator's kill action must itself broadcast a terminal
   (`abandoned`) lifecycle signal on the killed agent's behalf. Scope note:
   this is orchestrator/bus process-supervision, adjacent to but distinct
   from the separately-queued bus-singleton task (which scopes to the BUS
   SIDECAR being one-per-agent and reaping stray *sidecars*, not killing
   the whole agent process) — building it here since it's the direct,
   in-context answer to what item 2 needs to actually hold; flagging the
   overlap for the orchestrator/board to reconcile with bus-singleton at
   close.
   too.
3. **Subagent aggregation**: only the first feature ever shows subagents —
   every agent's subagents must render under their own parent row.

   BUILD FINDING (core-rendering builder, 2026-07-22): reproduced with 2
   architects each with their own subagents BEFORE any change — aggregation
   already nested correctly; a regression test now locks this in. The real
   cause of the reported symptom is more likely a viewport-scroll cutoff:
   the curses draw loop has no scroll-offset tracking (`if y >= max_y:
   break`), so once total rows exceed the pane's height, everything past
   that line — which could be a later feature's subagents — is simply
   never drawn, with no way to scroll to it. This feature's own additions
   (bus rows, project headers) push row counts higher, making the cutoff
   more likely, not less.

   RESOLVED (operator, 2026-07-22, direct): fix now, in this build — add
   scroll-follows-selection to the curses draw loop so the visible window
   tracks the selected row.
4. **Per-agent color**, matching Claude Code's subagent color palette where
   the terminal allows (see Questions).
5. **Buses**: shown at the TOP, italic, greyed, with a message icon (📬
   proposed) — they are expected to always be there; exactly ONE row per
   live agent (the per-agent singleton, Decision-051), none for dead
   agents; duplicates never render.
6. **Auto-mount**: the orchestrator mounts the sidebar the moment it first
   launches work — no manual mount step.
7. **Commands** — REVISED (operator via orchestrator, 2026-07-22,
   operator-origin relay, req 23f58ec9d9f2): `/orchard add <path>` is
   REVERTED, must not be built. Replaced by:
   (a) **Dynamic appearance** — installing orchids in a repo (`.ai.toml`
       presence remains the install signal) makes it appear immediately in
       every mounted sidebar, no add command, no hand-kept
       `ORCHIDS_SIDEBAR_REPOS` list; installation IS registration. Whether
       that env var retires or survives as an override is an architect HOW
       decision; the registry write may shim the stopgap kauk.
   (b) **Hiding is conversational** — operator asks the orchestrator or any
       agent to hide a repo; the agent presents a NUMBERED LIST of names as
       displayed in the sidebar and asks which to hide; the pick hides
       persistently across remounts. `/orchard hide <displayed-name>` may
       exist as a direct form; `show` re-lists hidden repos the same
       numbered way.
8. **Ellipsis before clipping**: truncated row text (e.g. "agent-closing
   Done, awaiting…") shows an ellipsis, never a hard cut.
9. **Status vocabulary** — REVISED (operator, 2026-07-22, direct): the
   "exactly three live plus one parked" framing was wrong; done and failed
   must never share a glyph ("can't put green for fail, same as you can't
   have green and green at a traffic light"), and idle is not the same
   thing as awaiting. Final six-state vocabulary, all static/fixed-width,
   no animation (per item 1):
   - **working** 🚧 — the agent has active subagents or is working itself;
   - **waiting** ⌚ (a watch, operator-corrected from the earlier ⏱️
     proposal) — an external component is taking time (threshold ~5s); ❓
     variant specifically when the wait is on the operator (item 12a);
   - **idle** ⚪ (existing glyph, reused) — the agent is present/connected
     and doing nothing except not leaving;
   - **awaiting another agent** 🪷 (a closed bloom, dim) — another agent's
     work is needed before this one can move on;
   - **done** ✅ — success;
   - **failed** ❌ — distinct glyph, never reuses done's green.

12. **Question notifications** (operator via orchestrator, 2026-07-22,
    operator-origin relay, req c86f7f710fb8) — currently missing entirely:
    (a) **Render** — a row whose agent is waiting on the operator shows ❓
        as its notification marker; this is the visible form of the
        **waiting** state specifically when the wait is on the operator (a
        sub-case, not a 5th state) — composes with item 9's vocabulary and
        item 1's no-layout-shift rule.
    (b) **Source reliability** — today the flag only appears if the agent
        remembers to broadcast `notify_user`; a question asked through the
        harness's own dialog never reaches the bus. Make it mechanical: a
        hook on the harness's notification/question event auto-broadcasts
        the waiting-on-operator flag, independent of model diligence.
    (c) **Mechanics REFINED** (operator via orchestrator, 2026-07-22,
        operator-origin relay, req 5479001fc484): the ask path is a typed
        QUESTION MESSAGE on the bus (question text + numbered options); the
        renderer is a TOKEN-FREE SCRIPT, not an agent. On a question
        message, it draws a native tmux `display-popup` (numbered options)
        over the operator's CURRENT window, captures the keypress, and
        returns the answer over the bus to the asking session. The ❓
        sidebar marker consumes the same message. The harness Notification
        hook (12b) stays as backstop for harness-native prompts that bypass
        this path. THIS IS A TRIAL — build it lean; fleet-wide forbidding of
        the question tools happens only after the operator sees it work
        live. **Test requirement**: a LIVE round trip — an agent asks over
        the bus, the popup renders wherever the operator is, the answer
        arrives back at the asker.
    (d) **Keypress handling REFINED** (operator via orchestrator,
        2026-07-22, operator-origin relay, req 3fac9e73f53b): the popup
        responds ONLY to its defined option keys and IGNORES every other
        keypress — no default selection, no dismiss-on-any-key, no timeout
        auto-pick. Rationale: questions often arrive while the operator is
        mid-typing; stray in-flight keystrokes must bounce off harmlessly,
        never count as an answer. **Test requirement**: feed non-option
        keys first, then an option key — only the option key registers.
    (e) **Popup deferral while operator is typing** (operator via
        orchestrator, 2026-07-22, operator-origin relay, req
        3f296674aa62): while the operator has input in flight, a new
        question does NOT pop. It announces passively — the sidebar ❓ plus
        a quiet one-line "I have a question" notice through the agent — and
        the popup itself renders only when the operator's in-flight message
        is SENT (or they go idle). Signal: the harness's `UserPromptSubmit`
        hook fires on submission inside a claude session; recent-activity
        idle detection is the fallback for typing outside one. Deferral is
        the PRIMARY protection; the only-option-keys rule (12d) remains the
        guard for whatever still slips through. Folds into the same queued
        popup step (12c/12d).

        EXACT WORDING (operator, 2026-07-22, direct): the passive notice
        text is `"I have a question: <title>…"` — using the (g)-added
        `--title` field as `<subject>`, ellipsis, nothing more. Confirm
        this exact format is what's rendered, and that the popup itself
        stays suppressed until the operator's in-flight message is sent
        (or they go idle) — not just that SOME passive signal exists.
    (f) **Presentation discipline is the broker's, not the model's**
        (operator via orchestrator, 2026-07-22, operator-origin relay, req
        383f0a0071a6): the deferral (12e) and input rules (12d) live in the
        SCRIPT — an agent cannot override them. Enforced by architecture,
        never left to model instructions: the asking agent's interface has
        NO parameter that skips deferral or widens the accepted keys.
10. **Project header rendering**: the project title centered over a
    background GRADIENT rendered with half-block cells (▀▄), in the
    traditional orchid colour (the classic orchid #DA70D6 family) — except
    PAUSED projects, which render a very light gray instead of the gradient.
    Technique (operator, 2026-07-22): a half VERTICAL cell whose foreground
    and background step darker/lighter along the gradient direction, text
    drawn on top; a reference implementation exists in the seb.house
    repository (believed near the tmux/vt tooling, e.g.
    `~/src/serialseb/seb.house/deb/pi/vt/`) — reuse its approach but NOT
    animated.
11. **Title derivation is inconsistent** (bug): observed "claude" as the
    main title followed by the project name, and elsewhere the repo followed
    by the project name and a subtitle — no discernible logic. Define ONE
    deterministic scheme and fix every announcing source. Proposal: main
    title = the feature/project human name, subtitle = current activity;
    the program name ("claude") NEVER appears; a session with no announced
    name yet shows the repo name dimmed until its announce lands.
    SCOPE LIMIT (operator, 2026-07-22): the title scheme applies ONLY to
    orchid-managed tabs/windows — the operator keeps separate personal tabs
    that this change must never touch.
    GRAMMAR — RESOLVED (operator, 2026-07-22, direct): NOT a runtime
    conversion. The declarative form ("field projection" vs the id's
    "field-projecting"/"projecting field") is authored AT THE MOMENT the
    ledger entry is written — i.e. the board's `[Short title](...)` /
    sidecar H1, per `AGENTS.files.md` §TODO ("the id is never shown as a
    bare slug"). Fix: every title-setting call site must read that
    authored short title as the canonical human name, falling back to the
    mechanical hyphen-to-space derivation ONLY when no sidecar/short-title
    exists yet (pre-intake stub) — no grammar-conversion code is built.

    BUILD NOTE (architect, 2026-07-22): the "repo name dimmed until
    announce lands" case and item 2's "hide the bare session-UUID row" case
    are, in the current data model, the same transient state (a session
    with no `name`/`feature_id` yet, whose id looks like a bare UUID) —
    they cannot be told apart without adding a grace-timer that isn't
    otherwise specified. Left as: such rows stay invisible for that
    (millisecond-scale) pre-announce window rather than rendering a dimmed
    placeholder, matching item 2's tested, already-shipped behavior. Not
    pursuing further disambiguation absent a concrete complaint that this
    window is actually visible/annoying in practice.

12. (g) **Popup UX refinements, live-tested round 2** (operator, 2026-07-22,
    direct, from actually using the built popup): all apply to
    `tools/orchard-question-broker.py` specifically (NOT the `AskUserQuestion`
    harness tool, which this repo cannot change):
    - **Echo the keypress**: raw mode currently reads with echo off — show the
      digit as it's read (brief visual confirmation) rather than a silent,
      invisible commit, so a mistyped key is noticeable.
    - **Single- vs multi-select must look and behave differently** — today
      `bus.py ask` only ever returns one option. Add a multi-select mode:
      digits TOGGLE membership (shown, e.g. `[x]`/`[ ]`), a confirm key
      commits the current selection; single-select stays instant-on-digit
      (unchanged). The two modes must be visually distinguishable, not just
      functionally.
    - **Escape = "continue the conversation," never a refusal**: pressing
      Escape sends back a distinct sentinel over the bus (not an option
      index, not "no answer") meaning the operator wants to keep discussing
      before deciding. The asking agent must treat this as "pause and keep
      talking," never as declined/cancelled. (This is the exact failure mode
      already hit once this session: an `AskUserQuestion` dismissal that was
      actually the operator needing to relay something else got surfaced as
      a flat rejection — the popup must not repeat that.)
    - **Always-available gate keywords**: regardless of the specific
      question asked, the popup must special-case recognize `MAKE IT SO` and
      `THAT IS ALL` as always-selectable — typing/selecting one broadcasts
      the corresponding gate signal directly, rather than forcing the
      operator through the narrower question first.
    - **Title + short summary**: the popup is missing a short title (so the
      operator can recall what they're choosing at a glance) and a short
      summary of what the decision is about, beyond the raw question text.
    - **Make it pretty and colored**: currently plain, uncolored text.
    - **Size to content, not a fixed fraction of the screen**: currently
      sized as a percentage of the terminal; should size to the actual
      question/options/title content instead.

## Testing

Operator visual pass on the live sidebar (the method that produced this list),
plus unit coverage for the model changes: internal-row filtering, per-parent
subagent aggregation, bus collapsing, truncation with ellipsis, the
status vocabulary including the operator-waiting variant, the
paused-project gray vs orchid-gradient header path, and the deterministic
title scheme (never the program name; dimmed repo name pre-announce).

### Actually run (2026-07-22)

- **Unit suite**: `python3 -m unittest discover -s tests -p "test_*.py"` —
  **184/184 passing** at close (grew from the pre-existing 31 across the
  build: status/filtering/aggregation/color/gradient rewrite, viewport
  scroll, exit-grace lifecycle, title derivation, Orchard registry, and the
  bus-popup question mechanism, each verified green before merge).
- **Live operator round-trip on the real bus-popup mechanism** (item 12,
  the one piece that categorically cannot be unit-tested): fired
  `bus.py ask` for real against the live tmux server, operator pressed
  keys on the actual popup. This SURFACED AND FIXED two real defects that
  passed unit tests but failed live:
  1. The raw-mode key reader needed Enter after a digit — root cause:
     `sys.stdin.read(1)` can still buffer behind `tty.setraw()`; fixed
     with a direct `os.read(fd, 1)`.
  2. The echoed keypress was invisible — root cause: the echo write and
     the popup's teardown happened in the same instant; fixed with a
     short deliberate linger (0.2s) before closing.
  Both fixes confirmed by a second live round with the operator directly
  pressing keys and confirming the result, not by re-reading the diff.
- Round-2 popup polish (title/summary/color/content-sizing/multi-select/
  continue-escape/gate-keywords, item 12g) is unit-tested for all pure
  logic; color rendering, live `[x]`/`[ ]` redraw, and the multi-select/
  gate-keyword paths specifically have NOT had their own dedicated live
  operator pass yet (only the single-select digit path was live-verified
  twice, post-fix) — flagging honestly rather than claiming untested
  ground as done. The trial framing (item 12c) already anticipates further
  live exercise before any fleet-wide adoption decision.
- **Not live-tested, needs an operator/real-environment check**: the
  orchestrator auto-mount-at-boot step (agents/orchestrator.md prose — not
  executable, can't be unit tested) and the exit-grace kill enforcement
  (requires an agent actually overrunning its grace period against a real
  orchestrator — not exercised this session). Both are small, reviewed
  diffs reusing existing, already-tested mechanisms
  (`tools/sidebar-mount.sh`'s idempotency; `tools/architect-teardown.sh`'s
  kill pattern), but stating plainly that no live pass happened for either.

## Changelog entry

Polished the fleet sidebar from the operator's second live-pass list: status
rows no longer animate (no spinner, no flashing waiting-state) and use a
clear six-glyph vocabulary (working/waiting/idle/awaiting-another-agent/
done/failed, done and failed never sharing a glyph); every agent's own
sub-agents nest under its row, not just the first; bus rows now render,
collapsed to one per live agent, at the top, dim and italic; internal and
stale rows (including any feature whose lifecycle has genuinely ended) no
longer linger; row text truncates with an ellipsis instead of a hard cut;
the sidebar scrolls to follow the selected row once the list outgrows the
pane; each agent gets a stable colour from an orchid-species palette; the
project header renders as a static colour-gradient bevel (flat gray when
paused); titles are now read from the task's own authored name instead of a
mechanical id transform; the sidebar auto-mounts into the orchestrator's own
window at boot, not just into spawned feature windows; repos with `.ai.toml`
now appear automatically (no add command), and hiding one is a conversational
ask-and-pick, persisted across remounts; agents now get a declared grace
period to exit cleanly after finishing, with the orchestrator stepping in
if that window is overrun; and a first, explicitly-trial version of asking
the operator a question through a native popup (rather than only a model
remembering to flag it) exists, refined twice against live use — including
that a question never interrupts the operator mid-keystroke, Escape always
means "let's keep talking" rather than "never mind," and the two workflow
gate phrases are always available regardless of what's being asked.

## Readme delta

User-facing changes worth a README mention: the fleet sidebar's visual
vocabulary changed (six static status glyphs, no more spinner/flashing
rows); `/orchard hide <name>` / `show` exist as a direct command form
alongside the conversational ask-a-running-agent-to-hide-a-repo flow;
installing orchids in a repo (`.ai.toml` present) is now sufficient for it
to appear in the fleet sidebar automatically, no manual registration step.
The bus-popup question mechanism is a trial, not yet a documented supported
surface — the orchestrator should decide at ingest whether it's ready for a
README mention or stays internal until the trial concludes.
