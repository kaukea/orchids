# 2026-07-20 — `doing-skills` skill renamed `authoring-skills`

The frontmatter-contract skill is renamed `doing-skills` → `authoring-skills`
(Decision-003). Consuming repos drop any stale `doing-skills` laydown so only
`authoring-skills` (laid fresh by `kauk sync`) remains. Link-mode installs are
already pruned by `kauk sync` (its target is gone after the rename); this
migration cleans a stale symlink for older kauk versions and flags the
copy/local case for judgement — a real directory may carry local edits and is
never clobbered.

## Detect → convert

```sh
# Remove a laid-down doing-skills ONLY when it is a symlink whose target is gone
# (dangling after the package rename). A real directory (copy/local mode) is left
# untouched for the judgement step below — it may hold local edits.
d=".claude/skills/doing-skills"
if [ -L "$d" ] && [ ! -e "$d" ]; then rm "$d"; fi
true
```

## Then: reconcile a copy/local install (judgement)

If `.claude/skills/doing-skills` still exists as a real directory (copy or
`local` mode in `.ai.toml`), it is a pre-rename local variant. Move any local
edits into `.claude/skills/authoring-skills` (laid by `kauk sync`), then remove
the old directory. Update any repo-local reference to the `doing-skills` skill
name to `authoring-skills`.

## Verify

No `.claude/skills/doing-skills` remains (neither a dangling symlink nor, after
reconciliation, a real directory); the frontmatter-contract skill is present as
`.claude/skills/authoring-skills`.
