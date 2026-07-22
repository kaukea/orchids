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

- Operator live pass, 2026-07-22, on the sidebar-fixes branch build mounted in
  his window. Some of the duplicate bus rows observed were real duplicates:
  the orchestrator session that morning had spawned a second bus sidecar by
  mistake, so multiplicity was partly genuine process noise, not only a
  display defect.
- "app-identifying" as a permanent first row: that feature closed 2026-07-21 —
  the row is stale state (likely a leftover bus/state file); the fix should
  find and clear the source, not just hide the label.

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
3. **Subagent aggregation**: only the first feature ever shows subagents —
   every agent's subagents must render under their own parent row.
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

## Testing

Operator visual pass on the live sidebar (the method that produced this list),
plus unit coverage for the model changes: internal-row filtering, per-parent
subagent aggregation, bus collapsing, truncation with ellipsis, the
three-plus-one status vocabulary including the 5s waiting threshold, the
paused-project gray vs orchid-gradient header path, and the deterministic
title scheme (never the program name; dimmed repo name pre-announce).
