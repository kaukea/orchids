- created: 2026-07-17
- created_by: fable-5

## Blockers
- Lives upstream: the kauk skill ships in the pull-only `serialseb/kauk` package, so
  the text change must be made in that repo (separate workstream). This task only
  carries the requirement until it is handed over there.

## Questions
- None — the ruling exists (Decision-007); only the upstream edit remains.

## Findings
- The harness refuses Edit/Write through symlinks ("Refusing to write through
  symlink") and no configuration toggle exists (verified against current Claude Code
  documentation, 2026-07-17). The skill's instruction "edit the skill at the path you
  loaded it from, never chase the target into `.ai/repositories/`" is therefore
  unexecutable.
- Decision-007 sanctions the replacement procedure: resolve the symlink, write the
  target in `.ai/repositories/<owner>/<repo>/` (kauk's local-edit surface; sync
  reconciles), and in the package's own repo mirror to the real source in the same
  turn. The fleet `settings.json` ships `Edit`/`Write` allow rules for
  `.ai/repositories/**`.
- Operator constraint (2026-07-17): real kauk installs GLOBALLY, not per-repo — the
  per-repo `.ai/repositories/` surface is the stopgap's. When the global install
  lands, the Decision-007 allow rules (and the resolve-target procedure's path) must
  follow the new local-edit surface, wherever kauk puts it.

## Proposal
In `serialseb/kauk`, amend the kauk skill's Intent paragraph: replace the
write-through-symlink claim with the Decision-007 procedure, and note that the
harness refusal is expected and not a policy "no". Fold in Decision-009 (orchids,
2026-07-18): the procedure applies only on explicit operator direction, only inside
the content surfaces (`agents/`, `skills/`, `files/`), and the skill must not present
clone write-back as the default route for fixing package content.

## Testing
In a consuming repo: an Edit addressed to a `.claude/` symlink is refused by the
harness; the resolved-target write succeeds without a permission prompt; `kauk sync`
round-trips the edit to the source repo.
