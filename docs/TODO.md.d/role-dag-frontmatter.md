- created: 2026-07-17
- created_by: opus-4.8
- completed: 2026-07-20
- completed_during: f/role-dag-frontmatter

## Blockers
- None. Declarations are inert until kauk reads them; landing them early is safe.

## Questions
- None open — ruled 2026-07-17 (Findings, Decision-005).

## Findings
- Frontmatter is currently inconsistent and has never been machine-read: all 26 carry
  `name` + `description`; only 17 have `metadata`; 4 `share`; 4 `compatibility`;
  3 `tracked`. kauk touches `SKILL.md` at 5 places, all byte-level (`cmp -s`, `-e`,
  `cp`) — there is no YAML reader. Whatever key we add is the first frontmatter field
  that does anything.
- Existing `metadata.tags` are grep-bait keyword soup, not a taxonomy, and are consumed
  by nothing. `doing-skills` ships the literal placeholder
  `tags: [ <grep-able trigger words> ]`. Do not overload `tags` for roles.
- `skills/doing-skills/SKILL.md` defines the frontmatter contract the other 25 follow,
  so it is the keystone — it changes first or there is nothing to conform to. (It is
  also being renamed; see `skill-renames-and-splits`.)
- The node list is fixed by Decision-003. This task applies it; it does not relitigate it.

Operator rulings, 2026-07-17 (Decision-005) — close both questions; ruled directly,
the "one round with kauk first" waived (kauk's reader implements what is ruled here):
- **`roles:` is a list of slash-separated full paths** —
  `roles: [development/tofu, infrastructure/tofu]`. Chosen over bare node ids and
  over nested YAML / `role:` + `parent:` pairs.
- **Paths are placements.** Each declared path is a deliberate placement; an author
  MAY place a multi-parent node under a subset of its parents
  (`roles: [development/tofu]` alone is valid). Lint checks each declared path exists
  in the vocabulary — never completeness. Per-route delivery is expressible.
- **`general` is explicit** — `roles: [general]`; a missing `roles:` key is a lint
  error, so "forgot" is never readable as "deliberately general".

Build outcome (2026-07-20, architect on f/role-dag-frontmatter):
- Delivered: rename `doing-skills`→`authoring-skills` (executed here at operator
  direction — overlaps `skill-renames-and-splits`' rename item; orchestrator to
  reconcile that task's remaining scope), the `roles:` contract in
  `authoring-skills`, and `roles:` declared on all 26 skills per the Decision-003 tree.
- Proposal item 3 (lint) DROPPED by operator: validation is kauk's job at read
  time; an orchids lint over hand-authored declarations is circular. The
  vocabulary stays declared once in Decision-003, referenced by the contract,
  never restated.
- `write-to-s3` → `security/forensics` (Decision-003 provisional; the publication
  question is unchanged, tracked by `pre-publication-cleanup`).
- Spawned follow-up (kauk repo): add a `kauk package validate .` stub returning 0
  + a taxonomy TODO; real roles/taxonomy validation is implemented in kauk later.

## Proposal
1. Amend the frontmatter contract in `authoring-skills` (née `doing-skills`) with the
   ruled contract: `roles:` slash-path list, placement semantics, explicit `general`
   (Decision-005), and the DAG rule (multi-parent allowed).
2. Declare roles on all 26 skills per Decision-003.
3. Add a lint (extend `tools/board_lint.py` or a sibling) asserting: every skill
   declares ≥1 role (explicit `general` counts); every declared path resolves to an
   existing path in the vocabulary (placement subsets allowed — no completeness
   check); the vocabulary itself is declared in exactly one place.
4. Leave `manifest.conf`'s `role` field alone in this task — retiring it is kauk-facing
   and needs the reader to exist first.

## Testing
Lint run over the corpus: 26/26 skills declare a resolvable role path; a deliberately
bad path fails the lint, and so does a skill with no `roles:` key. Manual read-through of the diff against the Decision-003 tree.
Delivery itself cannot be tested until kauk implements the reader — say so, do not
imply otherwise.

## Docs determination (2026-07-20)
- README: updated the one `doing-skills` reference to `authoring-skills` (rename).
  The `roles:` contract is internal authoring detail — no user-facing surface
  changed, so no further README edit.
- ARCHITECTURE: no trigger fired. `roles:` is per-skill delivery metadata; it adds
  no component, boundary, wiring, or cross-cutting style change, and the vocabulary
  lives in Decision-003, not ARCHITECTURE. The rename touches no ARCHITECTURE
  reference (grep clean). No edit.
- CHANGELOG: appended (operator-gated) — WIP New-features bullet + the
  `archive/role-dag-frontmatter` detail block.
- MIGRATION: `migrations/2026-07-20-authoring-skills-rename.md` ships the rename
  (managed-artifact name change; state-guarded, never-clobber; link-mode already
  pruned by `kauk sync`).
- decisions.md: mid-feature rulings staged in the session log for orchestrator
  promotion (decisions.md is the orchestrator's to write, not the architect's).

Result: done · branch `f/role-dag-frontmatter`, implementation at 296c688 (rename
8d69f28, contract 9170b6d, declarations 296c688; this docs commit is HEAD) ·
tested by manual read-through of the 26-skill diff against the Decision-003 tree —
26/26 declare resolvable role paths, placements match (multi-parent `coding-tofu`
& `reverse-engineering-files`, git-split `git-commit`), only `roles:` lines added.
Delivery/enforcement is kauk-future, not tested here. Follow-ups: kauk `validate`
stub + taxonomy (new kauk task); `skill-renames-and-splits` rename item done here.
