- created: 2026-07-21
- created_by: Sebastien Lambla

## Blockers

- None.

## Questions

- ~~**Labels overlap**: does the "labels" bullet drop as already-done (the
  tags-and-labels build shipped the full label vocabulary, Decision-035), or
  does it mean something additional?~~ RULED (operator, 2026-07-22): neither —
  the scope is the **sidecar fields generally**: every field the sidecar/board
  badge carries projects to GitHub. Where a GitHub field exists it MAPS; where
  none exists it is CREATED. The shipped label projection stands untouched.

## Findings

- Operator sizing note (2026-07-21): very mechanical work — mapping badge fields
  the board already carries onto GitHub fields GitHub already supports, inside
  the existing board→GitHub sync.
- 2026-07-22 recheck: nested-tasks-projecting's indentation fix (commit
  495a48d) is orthogonal to this task — it fixed line-parsing, not field
  content; no overlap there.
- 2026-07-22 recheck: `project_sync` in `tools/board_gh.py` already syncs
  Status, Urgency, Readiness, Component as GitHub Project custom fields — no
  Priority or Type field exists yet, and no relationship (blocked-by/blocking)
  sync exists.

## Proposal

Frozen plan, agreed with the operator 2026-07-22 (recorded as Decision-051 —
see there for the full rationale and the live-schema evidence gathered
during discovery):

- **type** — set GitHub's **native Issue Type** (`updateIssueIssueType`) for
  all five board types (bug/feature/refactor/housekeeping/completion). The
  org (`kaukea`) already has native types Bug and Feature; the missing three
  (Refactor, Housekeeping, Completion) are created org-wide via
  `createIssueType`, idempotent ensure-if-missing. The existing emoji label
  projection for type (Decision-035) is untouched and stays live alongside.
- **priority** — set GitHub's **native org Issue Field "Priority"**
  (`setIssueFieldValue`), sourced from board `urgency`. Mapping: `critical`→
  Urgent, empty/normal→Medium, `nice-to-have`→Low, `idea`→Low (`High` unused).
  The existing Projects-v2 "Urgency" custom field is KEPT and still written
  by `project_sync` — both stay live (operator ruling: Urgency stays
  "absolutely needed" alongside the new Priority field).
- **relationships** — board `⊘` (blocked_by) syncs to GitHub's **native Issue
  Dependencies** (`addBlockedBy`/`removeBlockedBy`), full reconciliation each
  push (add missing, remove stale), same "board is canonical" principle as
  the label sync. `blocking` needs no separate write — GitHub derives it as
  blocked_by's inverse view. `~<id>` (`related`) has **no native GitHub
  equivalent** (confirmed via GraphQL schema introspection — no
  `relatedIssues` field/mutation, and org Issue Fields don't support an
  issue-reference data type); it projects as a `### Related` body-text link
  list, the same mechanism already used for the parent/child sub-tasks list.
- Parent/child sub-issue nesting stays out of scope, already shipped via
  [[nested-tasks-projecting]] (body-text list, not GitHub's native sub-issue
  API). Label vocabulary (Decision-035) stays untouched.

**One pre-existing bug folded into this build mid-flight** (operator
instruction, relayed after live-sync testing surfaced 12 real failures):
`pull()` called `ensure_label` (singular) but the function is
`ensure_labels` (plural) — a latent `NameError` crashing every
issues-triggered board-sync run. Fixed in this branch (commit `c984121`).

**Still filed as a follow-up TODO, not fixed here** (orthogonal, not
triggered by testing): `Component` is written by `project_sync` without
being declared in `SELECT_FIELDS`/`TEXT_FIELDS` — works today only because
it was created out-of-band on the live GitHub Project.

**Build shape**: 3 steps inside `tools/board_gh.py`'s `project_sync` (Type,
Priority, Relationships), all via the existing `gql()` helper, no new
dependencies. Independent in logic but share one file — builders dispatch
sequentially rather than in parallel to avoid conflicting edits.

Expectation set by the operator: on the next synchronization after this
lands, every mirrored issue carries exactly the same values as the board.

## Testing

Method (pre-agreed): one live synchronization, then verify on a sample
covering each case — an issue with urgency set, one with ⊘ edges in both
directions, one with tags — that priority, type, both relationship
directions, and labels equal the board's values exactly.

**Run 2026-07-22, against the real `kaukea/orchids` repo/org:**

- `python3 tools/board_gh.py push` → `push kaukea/orchids: 12 created, 28
  updated, 4 closed` / `project Orchidarium: 52 rows ensured` — clean run,
  no errors.
- Spot-check via live GraphQL query on issue #28 (injection-integrity,
  board urgency=critical, `⊘readme-changelog-ownership ~session-start-hook`)
  and #32 (deviance-detection, board urgency=empty, `⊘injection-integrity`):
  - #28: native Issue Type = `Feature` ✓ (board type=feature); native
    Priority = `Urgent` ✓ (critical→Urgent); native `blockedBy` = [#31] ✓
    (readme-changelog-ownership = gh#31); native `blocking` = [#32] ✓;
    issue body carries `### Related` → `#3` ✓ (session-start-hook = gh#3);
    labels unchanged/correct (✨feature, 🔥critical, ⚙️area/process, 📋todo,
    ⛔blocked).
  - #32: native Issue Type = `Feature` ✓; native Priority = `Medium` ✓
    (empty/normal→Medium); native `blockedBy` = [#28] ✓; native `blocking`
    = [] ✓ (nothing blocks on it — correct).
  - "one with tags" leg of the plan: no board task currently carries a
    `#tag` token, so there was nothing to sample for that specific case —
    the tag/label system itself (Decision-035) is untouched by this work
    regardless.
- Mid-testing, live `push` runs surfaced 12 real failures from a separate
  issues-triggered sync path hitting the pre-existing `ensure_label`/
  `ensure_labels` typo (unrelated to this feature's new code, but blocking
  a clean test signal). Operator relayed the fix; folded into this build
  (commit `c984121`). Re-tested: `python3 tools/board_gh.py pull` → `pull
  kaukea/orchids: 1 ingested, 0 closed-from-GitHub` — completes end-to-end,
  no crash. (Ingested a pre-existing canary issue, #59 "Testing, do not act
  on it" — left untouched per its own title, board/sidecar stub committed
  as pull()'s normal designed output.)

**Result: PASS.** Every sampled field (type, priority, both relationship
directions, related-as-body-link, labels) matched the board exactly; the
folded-in fix verified against a real end-to-end sync.

### Architecture

No `ARCHITECTURE.md` trigger fired: `board_gh.py` remains the same
component with the same responsibility (project the board onto GitHub) and
the same one-way data flow (board → GitHub); this work only widens the set
of GitHub field surfaces it writes to (native Issue Type/Priority/
Dependencies, alongside the pre-existing Projects-v2 fields and labels). No
component added/removed/repurposed, no new module wiring, no
architectural-style change.

### Changelog entry

✨ Board sync now projects task type and urgency onto GitHub's native Issue
Type and Priority fields (creating the org's missing issue types the first
time it runs), and projects `⊘blocked-by`/`blocking` edges onto GitHub's
native Issue Dependencies with full reconciliation each push. `~related`
edges, which have no native GitHub equivalent, appear as a `### Related`
link list in the issue body. The existing Projects-v2 Urgency field and the
emoji-label projection are unchanged and keep running alongside the new
native fields.

🐛 Fixed a crash (`NameError`) in the board→GitHub pull that had been
failing every issues-triggered sync since `ensure_label`/`ensure_labels`
diverged.

### Readme delta

No change. `README.md` doesn't document `board_gh.py`'s field-by-field sync
behaviour (its usage there, if any, is at the push/pull command level,
unaffected by this work) — checked, nothing to update.

## Result

**done** — branch `f/field-projecting`, HEAD after this work: see the
commit log (`🎉` anchor → 3 `✨` builder commits (Type, Priority,
Relationships) → `🐛` ensure_label fix → `🔧` live-sync results). Tested
live against `kaukea/orchids`, PASS (see `## Testing` above). No follow-on
tasks spawned by this feature beyond the one pre-existing bug already
folded in; the `Component`-not-declared-in-SELECT_FIELDS/TEXT_FIELDS gap
remains a separate follow-up TODO for the orchestrator to file.

Delegation: discovery — 3 Explore sub-agents (board_gh.py code, badge
vocabulary/decisions, GitHub API capabilities), plus a short inline live
`gh api`/GraphQL probe sequence (justified: read-only capability
verification not answerable by static search). Build — 3 `builder`
sub-agents (Type, Priority, Relationships), dispatched sequentially
(shared file) per step; 1 step (the `ensure_label` typo fix) done inline
(justified: single-line, mechanical, no design decision, folded in
mid-build per operator instruction).
