# Changelog

## Work in progress

_base: `f65ad36`_

### ✨ New features

- 📋 Registry file set: README (the why/what) + ARCHITECTURE (the how) front
  door, the "install kauk/orchids" bootstrap contract
  (`Agent-installation.md`), and `docs/decisions.md` seeded with the
  history-rewrite charter.
- 🗃️ The works: transients (`HANDOVER.md`, `MOOD.md`) namespaced into
  `.git/the-works/`; dated, state-guarded `migrations/` catch any repo up in
  one pass (watermark + hook, the highest date IS the package version);
  cross-repo writes gated to package content surfaces; micro-tasks may ride
  `main` on an operator-accepted offer.

### 🐛 Bug fixes

---

#### 🗃️ `f/the-works-channel` → `archive/the-works-channel`

The uncommittable channel moves to `.git/the-works/` and every structural
change now ships a dated migration: `migrations/YYYY-MM-DD-<slug>.md`,
state-guarded and merge-safe, applied as one net-effect pass against the
per-clone `.git/the-works/migrated` watermark announced by a `settings.json`
hook (two entries backfill 2026-07-11 and 2026-07-18). Handover ingest drains
gathered batches oldest-first. The blanket `.ai/repositories/**` allow rules
narrow to `agents/`/`skills/`/`files/`, with the agent-behaviour norm that a
fix to another repo rides that repo's workflow. The workflow skill gains the
micro-task path (`Branch: main` sanctioned on exactly those commits).

_See the board entry (`docs/TODO.md.d/the-works-channel.md`) and
Decisions 008–010 in `docs/decisions.md`._

#### ✂️ `f/data-only-split` → `archive/data-only-split`

orchids becomes DATA-ONLY: the package manager (`bin/orchids`) moves to
`serialseb/kauk` as the stopgap CLI, and `skills/skill-sync` retires in
favour of the `kauk` skill shipped by the kauk package itself (pull-only).
`manifest.conf` v2 typed lines (`skill`/`link`/`template`/`prefix`) expose
every distributed group — agents, hooks, tools, settings, AGENTS files,
templates — the engine hardcodes no layout. `templates/CLAUDE.md` holds the
exact prefix block; the install page bootstraps kauk first. Retro-closed
2026-07-17: the tree had landed on main verbatim as `904a9a0` (manual
close); the empty squash, tombstone tag, and note were fitted afterwards,
dated to the actual event.

_See `docs/TODO.md.d/tool-split-to-kauk.md` (findings & testing) and kauk
Decisions 007–008 in `serialseb/kauk/docs/decisions.md`._

#### 🔗 `f/kauk-script-name` → `archive/kauk-script-name`

The install page stops pointing agents at the retired `kauk-sync` name:
kauk Decision-009 ships the stopgap as `bin/kauk`, brand = command. One
rename sweep over the served instructions. Retro-closed 2026-07-17: the
tree had landed on main verbatim as `4035d21` (manual close); the branch
gained its missing anchor at close (`Base: 9ae9cd5`, dates preserved,
tree byte-identical to old head `b0d380b`).

_See kauk Decision-009 in `serialseb/kauk/docs/decisions.md`._

#### 📋 `f/registry-file-set` → `archive/registry-file-set`

Gives orchids its own registry file set: `README.md` sells the operating
model (agents, skills, rules as one versioned package), `ARCHITECTURE.md`
holds the mechanics, and `docs/decisions.md` opens with Decision-001 —
history migration is an orchestrator charter, gated by the project
`AGENTS.md` `repository:` field. The bootstrap contract becomes
"install kauk/orchids": `install.txt` renamed to `Agent-installation.md`,
with `index.html` (still served until the operator deletes the owin.org
remnants) regenerated to match. Close note: the branch was rebuilt at close
to repair a fabricated `Base:` SHA in its anchor commit; all work commits
and dates carried over verbatim.

_See `docs/TODO.md.d/registry-file-set.md` (findings & rulings) and
Decision-001 in `docs/decisions.md`._
