- created: 2026-07-16
- created_by: fable-5
- completed: 2026-07-17
- completed_during: main (orchestrator board work)

### Why cancelled
**Moved to kauk, not dropped.** This is kauk engine work — this sidecar's own Proposal
says so ("Fix in kauk … during link laying, resolve src and dst"). Under the operator
ruling of 2026-07-17, work to be done by kauk belongs on kauk's board, so it now lives
at `serialseb/kauk` → `docs/TODO.md.d/self-install-link-collision.md` (`cli` /
`cli-core`), carrying the findings, the operator's 2026-07-16 parking ruling, and the
proposal intact. It stays parked; only its home changed.

**What orchids keeps:** the standing workaround below is an orchids working rule and
still applies until kauk ships the guard — never commit the `T` typechange on
`AGENTS.shared.md` / `AGENTS.files.md`.

## Blockers
- none

## Questions
- Should the engine (kauk) skip `link` entries whose resolved src and dst are the
  same repo-relative path in the installing repo, or should the orchids manifest
  gain a self-install guard?

## Findings
- orchids was self-installed (kauk init + install, commit 957fd72), mirroring kauk
  Decision-008 dogfooding. Skills/agents/hooks/tools/settings links are collision-free
  (src dir differs from dst dir).
- The two root `link` entries collide under self-install: `link AGENTS.shared.md
  AGENTS.shared.md` (and files.md) have src == dst here, so the migration replaced
  the canonical SOURCE files with symlinks into the gitignored vendored clone.
  Committing that would ship dangling symlinks to every consumer. The files were
  restored with `git checkout --` before committing.
- Consequence: every `kauk sync` run inside this repo will re-typechange those two
  root files until the engine or manifest guards src == dst. Do not commit `T`
  typechanges on AGENTS.shared.md / AGENTS.files.md.
- Editing skills in this repo: edit `skills/` (the source) directly, not through the
  `.claude/skills/` symlinks — those point at the vendored clone, and push-back sync
  targets a checked-out origin.

## Operator ruling (2026-07-16)
- Parked: kauk migration work is deferred; not dealing with it now.
- Sync is expected to rebase the clone; a manually-made old copy means it
  predates the tool — not a sync defect.
- Stopgap in this repo: when sync typechanges the root AGENTS files, merge
  manually if the changes make sense; never commit the `T` symlink form.
- Known: the repo is non-conforming and carries too many skills; both get
  fixed later.

## Proposal
Fix in kauk (when migration work resumes): during link laying, resolve src
and dst; if identical, skip the entry (the repo IS the package). One-line
guard, no manifest change needed.

## Testing
In this repo: run `kauk sync`, confirm AGENTS.shared.md / AGENTS.files.md stay
regular files.
