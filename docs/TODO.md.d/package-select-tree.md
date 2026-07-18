- created: 2026-07-18
- created_by: operator
- created_during: f/workstream-log

## Blockers
- Lives upstream: the install/selection UX belongs to the package manager
  (`serialseb/kauk`, pull-only). This task carries the requirement until it is
  handed over there (Decision-009: fixes to another repo ride that repo's
  workflow).

## Questions
- Selection medium default: ASCII tree + answers in words, checkbox dialogs
  (multi-select, ≤4 options/question, paged), or tree-with-preview hybrid?

## Findings
- Slash commands render no widgets; the conversation is the form. Agents render
  ASCII trees trivially; the question tool provides flat multi-select checkboxes;
  a question option's preview pane can display the full tree alongside.

## Proposal
A skill (shipped with the kauk package) standardizing how an agent displays a
package's installable nodes and captures the selection at install time: render
the tree with `[x]`/`[ ]` states grouped by role, take toggles conversationally
(or via paged multi-select), re-render until confirmed, then hand the result
back to kauk by writing the `.ai.toml` delivery sections. One convention, every
repo, instead of each install improvising its own selection dialogue.

## Testing
Run `kauk install` in a scratch repo driven only by the skill: tree rendered,
selections taken, `.ai.toml` matches the confirmed tree, `kauk sync --status`
agrees.
