# 2026-07-11 — transients leave the working tree for .git/

Historical entry (backdated to the change it describes, orchids `99aa903`).
Before this date, `HANDOVER.md` was a gitignored file at a repository or
worktree root, and `MOOD.md` a gitignored root file. Both moved into
`$(git rev-parse --git-common-dir)/` — uncommittable by construction and
shared across worktrees.

A later migration moves the destination again; every step below is guarded
by observable state, so merge the pending series and apply the net effect.

## Detect → convert

- If `HANDOVER.md` exists at the main repo root or at any worktree root
  (`git worktree list --porcelain`): it is a stranded pre-2026-07-11
  handover. It belongs in the uncommittable channel (destination per the
  newest pending migration), keeping one file per origin — never
  overwrite an existing handover.
- If `MOOD.md` exists at the main repo root: same — move it into the
  uncommittable channel. If one already exists at the destination, the
  destination file wins (it is newer); park the stray alongside it as
  `MOOD-legacy-root.md` for the operator.
- Remove `HANDOVER.md` / `MOOD.md` entries from `.gitignore` if present —
  nothing at the root needs ignoring once the files live under `.git/`.

## Verify

No `HANDOVER.md` or `MOOD.md` remains at any repo or worktree root.
