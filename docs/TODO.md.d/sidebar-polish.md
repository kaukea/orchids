# Sidebar polish: the second corrective round from the operator's live pass

- created: 2026-07-22
- created_by: Sebastien Lambla

## Blockers

- None hard. Independent of the [[sidebar-fixes]] close — that task gates on its
  own recorded result; this round collects everything the operator's live pass
  found beyond it.

## Questions

- Per-agent colors: match Claude Code's subagent palette (red/blue/green/
  yellow/purple/orange/pink/cyan) — confirm terminal rendering fidelity is
  acceptable in the sidebar's tmux pane before committing to exact hues.
- Bus singleton: today EVERY agent loads its own bus sidecar (Decision-041) —
  the operator expected ONE message bus per repo. Display-wise this round
  collapses buses to a single top row; whether the MECHANISM becomes a true
  singleton is a design question to rule on (touches Decision-041).
- Emoji set for the status vocabulary (operator invites proposals; current
  proposal in the item below).
- /orchard `add <path>`: what counts as "an orchids installation in progress"
  at a path — .ai.toml present? manifest laydowns partial? Define the
  detection precisely at bloom time.

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
3. **Subagent aggregation**: only the first feature ever shows subagents —
   every agent's subagents must render under their own parent row.
4. **Per-agent color**, matching Claude Code's subagent color palette where
   the terminal allows (see Questions).
5. **Buses**: shown at the TOP, italic, greyed, with a message icon (📬
   proposed) — they are expected to always be there; collapse to one row
   (they are one logical bus). Mechanism-singleton question parked in
   Questions.
6. **Auto-mount**: the orchestrator mounts the sidebar the moment it first
   launches work — no manual mount step.
7. **Commands**: `/orchard show|hide|add <path>`, where `add` detects whether
   an orchids installation is actually present/in progress at the path.
8. **Ellipsis before clipping**: truncated row text (e.g. "agent-closing
   Done, awaiting…") shows an ellipsis, never a hard cut.
9. **Status vocabulary**, exactly three live states plus one parked state:
   - **working** 🚧 — the agent has active subagents or is working itself;
   - **waiting** — an external component is taking time (threshold ~5s);
     proposed glyph ⏱️ (static, fixed-width — no animation per item 1);
   - **done** ✅;
   - **awaiting another agent** — distinct glyph in very light gray to read
     as "not started yet"; proposed 🪷 (a closed bloom, dim) or 💤.

## Testing

Operator visual pass on the live sidebar (the method that produced this list),
plus unit coverage for the model changes: internal-row filtering, per-parent
subagent aggregation, bus collapsing, truncation with ellipsis, and the
three-plus-one status vocabulary including the 5s waiting threshold.
