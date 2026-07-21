- created: 2026-07-21
- created_by: Sebastien Lambla

## Blockers

- None.

## Questions

- Anchor form for decisions.md entries: GitHub heading anchors (stable but unwieldy —
  the timestamp is in the heading) vs `?plain=1#L<n>` line links (precise; stable in
  an append-only file, but GitHub-web-specific and dead in editors)?
- Do `[[id]]` wiki tokens stay as the greppable convention with link syntax added
  (`[[id]](TODO.md.d/<id>.md)`-style), or convert wholesale to plain markdown links?
- Scope of the retro sweep: decisions.md + all sidecars + issue projections
  (board_gh's issue_body quotes the sidecar path as inert code — should be a link)?

## Findings

- Operator request (2026-07-21): links to documents that are in git must actually
  link — to the DOCUMENT and the LINE — decisions, sidecars, etc.
- Current state: `[[task-id]]` wiki tokens and bare `Decision-NNN` mentions link
  nowhere; the only real links are the board's title links
  (`[title](TODO.md.d/<id>.md)`) and occasional full URLs. Consumers that would
  benefit: GitHub-rendered views (issues, blob), editors, the cloud hops that
  cold-start from issue threads.

## Proposal

Rule the link convention (forms per the Questions), enforce it forward at write time
(AGENTS.files.md formats), and run one retro sweep converting existing references in
decisions.md, sidecars, and the board_gh projection bodies.

## Testing

To agree when ripened — expected shape: clicking any reference in a GitHub-rendered
doc lands on the target document at the referenced entry/line; a sweep-checker greps
zero bare `Decision-NNN` / `[[id]]` mentions without link syntax.
