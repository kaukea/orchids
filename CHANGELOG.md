# Changelog

## Work in progress

_base: `f65ad36`_

### ✨ New features

- 🎭 Close choreography on the bus: the architect's finish rides a bus `finished`
  signal, not a transcript-grepping Stop hook. At its `ALL IT IS` countersign the
  architect signals `finished`; the orchestrator returns the operator's focus and
  runs the close off that signal — so the operator's `THAT IS ALL` is the single
  close gate (like merging a PR), with no separate "close it". The old
  `architect-close.sh` Stop hook is retired along with its `jq` transcript race
  and its cross-session `/tmp/architect-close.log` leak; the tmux teardown moves
  into `architect-teardown.sh`, which finds the architect pane by its `arch:<id>`
  title, reads no transcript, and writes nothing to `/tmp`. Bus `status` now
  carries `model` and `effort` beside the broken-out token counts, so a reader has
  the denominator; a dead architect is caught by a direct pane check when a close
  is expected, with no scheduler.

- 📮 Message bus: independent agent sessions in one repository can talk to each
  other. A `bus` sidecar owns the entire mechanism, so no other role learns the
  format, the paths, or the ordering rules; agents ask it in plain language.
  Membership is established by hooks rather than prompts (code does not drift,
  models do): `SessionStart` creates the inbox and asks the session to load its
  bus and announce itself, `SessionEnd` broadcasts a departure and removes the
  inbox so a later send fails immediately instead of vanishing. An agent's
  address is its session id; only top-level sessions are members. Identity is
  broadcast once, while status — context occupancy and token spend — is pulled
  on demand and answered by the sidecar off the parent's transcript, costing the
  parent no context and still answering while it is busy or wedged. There is no
  delivery guarantee by design: a sender expects no answer and decides for
  itself whether to retry, abandon, or error.

- 📋 Registry file set: README (the why/what) + ARCHITECTURE (the how) front
  door, the "install kauk/orchids" bootstrap contract
  (`Agent-installation.md`), and `docs/decisions.md` seeded with the
  history-rewrite charter.
- 🗃️ The works: transients (`HANDOVER.md`, `MOOD.md`) namespaced into
  `.git/the-works/`; dated, state-guarded `migrations/` catch any repo up in
  one pass (watermark + hook, the highest date IS the package version);
  cross-repo writes gated to package content surfaces; micro-tasks may ride
  `main` on an operator-accepted offer.
- 📓 Workstream logs: every session keeps its own small rolling record in
  `.git/the-works/<stream>/` — state, findings, dead ends, decisions pending
  promotion, pointers — so resets and agent swaps never lose the thread;
  `_closed` streams are promoted by the ingester (single-writer on the board
  and decisions) then archived to `_ingested/` (provisional retention).

- 📋 The board on GitHub: active tasks become labelled issues (`gh#` on the
  badge), the private user Project **Orchidarium** aggregates all repos'
  active work with Status/Urgency/Readiness/Component fields, and an
  actor-gated `board-sync` workflow ingests phone-born issues and couch
  closes into the file board — files stay canonical; the orchestrator pulls
  at boot and pushes after board writes.

- 🏷️ Skill roles: every skill declares its place in the role DAG via a `roles:`
  frontmatter list of slash-paths (Decision-003/005) — placements not
  completeness, `general` explicit, multi-parent expressible. The
  frontmatter-contract skill is renamed `doing-skills` → `authoring-skills` and
  documents the contract; kauk validates the declarations when it reads them.

### 🐛 Bug fixes

---

#### 🏷️ `f/role-dag-frontmatter` → `archive/role-dag-frontmatter`

Every skill now declares its role placements in frontmatter: `roles:` is a list
of slash-separated full paths from the Decision-003 role DAG, each a deliberate
placement — a multi-parent skill may sit under a subset of its parents, `general`
is explicit, and a missing key is an error (never read as "deliberately
general"). The keystone `doing-skills` skill is renamed `authoring-skills`
(Decision-003, role `general`) and now documents the `roles:` contract,
referencing the vocabulary in `decisions.md` rather than restating it. All 26
skills are declared per the tree — `coding-tofu` and `reverse-engineering-files`
span two parents, `git-commit` spans `general` + `process/workflow`, and
`write-to-s3` takes its provisional `security/forensics`. The legacy
`manifest.conf` role is left in place until kauk reads frontmatter; enforcement
is deferred to a kauk `validate` stub, not an orchids lint.

_Board: [role-dag-frontmatter](docs/TODO.md.d/role-dag-frontmatter.md) ·
decisions: Decision-003, Decision-005._

#### 📋 `f/github-board-sync` → `archive/github-board-sync`

The fleet's cross-repo visibility pilot (orchids + kauk): `tools/board_gh.py`
projects the board to GitHub issues and Orchidarium Project rows and ingests
GitHub-born changes back; `.github/workflows/board-sync.yml` runs the
deterministic ingest on issue events (consumers carry only a thin reusable-
workflow shim); the orchestrator skill owns both directions. Known gaps and
the day-two scenarios live in the sidecar's 2026-07-19 test plan; repo
visibility fallout is ruled by Decision-013.

_Board: [github-board-sync](docs/TODO.md.d/github-board-sync.md) · decisions:
Decision-012, Decision-013._

#### 📓 `f/workstream-log` → `archive/workstream-log`

The monolithic `HANDOVER.md` becomes per-session rolling workstream logs in
`.git/the-works/<stream>/` (`handover` skill rewritten as the protocol): one
file per session, five fixed sections, read oldest→newest; `_closed` marker +
hook announcement; ingest = promote decisions/TODO (single-writer — children
never write main's docs) then archive the stream to `_ingested/`, kept
provisionally to evaluate the dead-ends record. A migration folds legacy flat
`HANDOVER*.md` into a closed `legacy` stream.

_See the board entry (`docs/TODO.md.d/workstream-log.md`) and Decision-011 in
`docs/decisions.md`._

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
