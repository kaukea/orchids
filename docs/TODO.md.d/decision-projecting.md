- created: 2026-07-21
- created_by: Sebastien Lambla

## Blockers

- None.

## Questions

- ~~Duplicate/superseded close mechanics?~~ RULED (operator, 2026-07-22):
  NATIVE — the UI closes as duplicate, so the API does too: the close
  mutation's duplicate state with its duplicate-of reference. Body-note
  ("Superseded by #N"/"Duplicate of #N") remains the FALLBACK only if the
  API path proves narrower than the UI. Superseded decisions close
  not-planned with the superseded-by reference.

- ~~Duplicate close reason: native `state_reason=DUPLICATE`, or a body-note
  fallback?~~ RULED (operator, 2026-07-22): native, and cheaper than assumed.
  `gh issue close --reason` doesn't expose it, but the raw GraphQL schema
  does: `CloseIssueInput.duplicateIssueId: ID` alongside
  `stateReason: IssueClosedStateReason` (confirmed against
  `octokit/graphql-schema`, shipped by GitHub Dec 2024) — a first-class
  mutation, not a workaround, using the same `gql()` helper already in
  `tools/board_gh.py` for `createIssueType`/`updateIssueIssueType`. No
  body-note fallback needed; decisions.md has no separate "duplicate" state
  distinct from "superseded" anyway (only Decision-029's board-task
  convention has one) — supersession itself projects as GitHub's native
  duplicate-of, old entry closed pointing at the new one, matching the
  file's existing `Superseded by Decision-MMM` direction.
- ~~How does sync match a decision to its GitHub issue without a place in
  decisions.md to store one?~~ RULED (operator, 2026-07-22): title-based,
  stateless. `Decision-NNN` is already the stable key; the issue title is
  literally `Decision-NNN: <title>`, matched via one bulk
  `gh issue list --search "Decision- in:title"` call per sync run (not N
  per-decision searches), filtered client-side against
  `^Decision-(\d+): `. No stored mapping anywhere, decisions.md's canonical
  heading+hashtag-only format untouched. Considered and rejected: embedding
  a gh# in the heading (violates the canonical format); a Projects-v2 custom
  field for matching (adds a lookup indirection state-search-by-title
  already avoids). Also added, per operator request, as pure redundant
  metadata (not used for matching): `Decision Number`/`Decision Title`
  Projects-v2 text fields, same mechanism as `Area` — free, future-proofing,
  no admin-level action (Projects-v2 fields are project-scoped; GitHub Issue
  Types, used for the `Decision` type itself, are org-scoped/admin — the two
  are different permission tiers, both already exercised by this codebase).

## Findings

- Type creation is a non-issue: `ensure_issue_types` (merged, org-scoped,
  create-if-missing) is generic over any type name — adding a "Decision"
  type is a one-line extension of `TYPE_ISSUE_TYPES`-style mapping, not new
  machinery. Confirmed against `tools/board_gh.py:286-298`.
- Decisions are not board tasks — they don't come from `board.tasks()` (which
  reads TODO sidecars). `sync_issue_types`/the close loop in `push()` iterate
  tasks only, so decision-projecting needs its OWN sync pass over
  `docs/decisions.md` entries in parallel, reusing the type/close primitives
  rather than hooking into the existing per-task loops. Consistent with the
  proposal's "same way tasks do, with a different type" — not a scope change,
  just confirming the shape for the architect.
- Native Priority and Issue Dependencies (Decision-053) don't apply to this
  proposal's scope — decisions don't carry urgency or `⊘` blocking edges
  today, so no reuse/question there.

## Proposal

Decisions (docs/decisions.md entries) synchronize to the GitHub task board the
same way tasks do, with a DIFFERENT type than tasks so they can be referenced
correctly from issues and from each other.

Lifecycle mirrors exactly what the decisions file already does, using the
fields GitHub currently has:

- each decision becomes a mirrored item of its own type, referenceable by
  number/link;
- a SUPERSEDED decision closes on GitHub, pointing at the decision that
  replaces it (the file's strike + superseded-by marker, projected);
- a decision considered a DUPLICATE closes as a duplicate;
- task issues close as they do today — the closing conventions apply to both
  issues and decisions.

No new vocabulary, no new lifecycle states: project the existing semantics
onto GitHub's available fields, nothing more.

Built as `tools/board_gh.py`'s `sync_decisions()` + `decision_project_sync()`,
wired into the existing `push()` entry point right after the task sync passes
(own pass over `docs/decisions.md`, not hooked into the `board.tasks()` loop —
decisions aren't board tasks). Two internal passes: (1) create-or-update every
decision's issue (title/body/type) so every target node id exists, (2)
open/close state — struck+superseded entries close via
`closeIssue(stateReason: DUPLICATE, duplicateIssueId: <superseding issue>)`,
everything else stays/reopens open.

## Testing

DONE — one live synchronization run against the real `docs/decisions.md`
(56 entries) on `kaukea/orchids`, 2026-07-22, verified directly against
GitHub (not just the script's own output):

- 56/56 decisions created as issues titled `Decision-NNN: <title>`, typed
  `Decision`, no title collisions.
- Decision-006 (the file's only currently-struck entry) closed natively:
  `state=CLOSED`, `stateReason=DUPLICATE`, `duplicateOf` → issue #124
  "Decision-036: ...", exactly matching the file's `Superseded by
  Decision-036` marker.
- Decision-038 and Decision-036 (live/unstruck) confirmed open, typed
  `Decision`.
- Projects-v2 board: all 56 decision rows present, `Decision Number`/
  `Decision Title` fields populated correctly (sample checked: Decision-001).
- Script summary (`56 created, 0 updated, 1 closed, 0 reopened, 0
  ambiguous-skipped`) matched the independent GraphQL verification exactly.
- No rate-limit errors in this run.

## Result

**done.** Branch `f/decision-projecting`, HEAD `35dc8d4` (parser: `ad9793d`
🎉 anchor, `Base: 45940c6`; sync+wiring: `35dc8d4`).

Built: `TYPE_ISSUE_TYPES["decision"] = "Decision"`; `parse_decisions()`;
`list_decision_issues()`; `sync_decisions()`; `decision_project_sync()`;
wired into `push()`. Fan-out: discovery — 2 Explore agents (board_gh.py
mechanics, decisions.md format); build — 2 builders (parser; sync+wiring),
0 steps inline. Tested live against the real 56-entry decisions.md on
`kaukea/orchids`, verified independently via GraphQL — see Testing above.

`ARCHITECTURE.md` updated directly (data-flow trigger: decisions.md now has
a GitHub-projection data flow it didn't have before) — one line added to the
sidecar-contract bullet for `docs/decisions.md`.

No follow-up tasks spawned. One out-of-scope item surfaced during testing by
the orchestrator (callabloom API-quota/event-amplification during board
sync) — confirmed out of scope for this feature, orchestrator is boarding it
separately.

## Changelog entry

Decisions in `docs/decisions.md` now mirror to GitHub the same way tasks do:
each entry becomes its own `Decision`-typed issue, referenceable and
searchable from GitHub the moment it's projected. A superseded decision
closes there natively as a duplicate of the decision that replaced it, so
the file's strike-and-pointer convention is no longer something a reader has
to eyeball — it's real, traversable issue state. No new fields to maintain
by hand: matching is title-based and stateless, decisions.md's format is
unchanged.

## Readme delta

`README.md`'s "The board follows you off the terminal" paragraph currently
reads: "Active tasks mirror to GitHub issues and the private Orchidarium
project view...". Suggested addition, same paragraph:

> Decisions get the same treatment: every entry in `docs/decisions.md`
> mirrors as its own `Decision`-typed issue, closing natively as a duplicate
> of whatever superseded it — so a ruling is exactly as referenceable and
> exactly as visible off the terminal as a task.

## Decision entries

## [2026-07-22 17:10 CEST] Decision-NNN: Decision supersession projects as GitHub's native duplicate-of, not a body-note fallback
#decision-projecting #github #graphql #duplicate #supersession

GitHub's `closeIssue` GraphQL mutation has carried `stateReason: DUPLICATE`
plus `duplicateIssueId: ID` since December 2024 — confirmed against the
`octokit/graphql-schema` schema, not assumed. `gh issue close --reason` never
exposed it (CLI only offers `completed`/`not planned`), which is why an
earlier pass assumed a body-note fallback (the `~related` precedent,
Decision-053) would be needed. It isn't: reaching the native mutation is one
more `gql()` call, the same helper already used for `createIssueType`/
`updateIssueIssueType`. decisions.md has no separate "duplicate" state
distinct from "superseded" (only board tasks do, per Decision-029) — so
supersession itself projects as the native duplicate-of: the OLDER
(struck) decision's issue closes pointing at the NEWER (superseding) one,
matching the file's own `Superseded by Decision-MMM` direction.

## [2026-07-22 17:10 CEST] Decision-NNN: Decision-to-issue matching is title-based and stateless
#decision-projecting #github #matching

`docs/decisions.md`'s canonical entry format is heading + mandatory hashtag
line only — no room for a stored GitHub issue number, unlike task sidecars'
YAML front matter. Rather than extend that canonical format (which every
future decision write would then have to carry), sync matches a decision to
its GitHub issue by title text: the issue title is `Decision-NNN: <title>`,
looked up via one bulk `gh issue list --search "Decision- in:title"` call
per sync run and filtered client-side, not stored anywhere. `Decision-NNN`
was already the stable, human-assigned key: this reuses it rather than
inventing a second one. Considered and rejected: embedding a gh# in the
decisions.md heading (breaks the canonical format); a Projects-v2 custom
field for matching (adds an indirection the title lookup already avoids —
GitHub's own field-locking is non-existent per-field anyway, so a stored
field is no more tamper-proof than re-deriving it fresh every run). Also
added, per operator request, as pure redundant metadata (not used for
matching): `Decision Number`/`Decision Title` Projects-v2 text fields, same
mechanism already used for `Area` — free, future-proofing, no admin action
(Projects-v2 fields are project-scoped, unlike GitHub Issue Types which are
org-scoped/admin — both tiers already exercised elsewhere in this codebase).
