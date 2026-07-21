- created: 2026-07-20
- created_by: Sebastien Lambla

## Blockers

- ~~⊘handover-contract; both interactive boundaries parked the autonomous path~~ —
  OVERRULED (operator, 2026-07-20, Decision-027): "for cloud, there is absolutely no
  blocker." Waiting delays discovering the deviance in the system — start now. The
  contract is encoded; the gates apply INSIDE the flow (summary → MAKE IT SO; THAT IS
  ALL → housekeeper), they do not gate starting it.

## Questions

- ~~First slice?~~ RULED (operator, 2026-07-20): the FULL PATH to PR in one slice —
  the whole spine surfaces its deviance at once.

## Findings

- **The design: TitanShield `docs/TODO.md.d/rework-task-lists.md`** (2026-07-01,
  operator-ratified). Key parts this task implements orchids-side: the AUTONOMOUS origin
  (`readiness = stage × origin`) with the strict self-authorize boundary, the shared
  close spine (review via auto-opened PR; THAT IS ALL stays the final gate; the
  housekeeper is the only writer to `main`, closing via `gh pr merge --squash`), and the
  verified cloud-trigger facts (routines ≥1h, `/fire` OAuth endpoint, `@claude` mention
  path; PR/Release-only routine triggers).
- **The cloud flow (Decision-027):** new feature = a GitHub issue → the orchestrator
  asks its intake questions before the task reaches the board proper → the ripener's
  functional-completeness rounds, all as comments on the issue (or a discussion —
  operator is indifferent) → statistical readiness reached → architect kicked off
  automatically → tech plan, few or no questions, summary → MAKE IT SO → pull request →
  THAT IS ALL → housekeeper amends + merges the PR. Locally the same spine runs on
  worktrees.
- Question economy (Decision-027): better questions upstream, fewer downstream; the
  current gates reflect today's error rate and shrink as upstream improves.
- The [[github-board-sync]] lane (issues mirror, Orchidarium Project, board-sync
  workflow) already gives the issue substrate and a cloud-triage precedent.

- **Live-fire record (2026-07-21, session-naming / gh#34):** hop 0 ingest ✓ ·
  plan hop refused an unripe stub then fully passed post-ripening (prologue
  handoff, branch, tech plan comment) ✓ · build hop passed and correctly PARKED
  at PR creation on the org policy (now a documented prerequisite) ✓ · revise
  hop reconciled the branch to the mid-build-frozen naming contract, catching
  sites the build missed ✓ · close hop refused 3× on missing/wrong-vocabulary
  gate (charter integrity; never merged, never guessed) — mechanical close
  artifacts proven on the demo PR (grey button → `close-spine` → squash) and via
  operator-approved repair. Defects found live and fixed in-branch: checkout
  skew (board reads pinned to origin/main), refusal not halting the job,
  substring gates (exact-form now), handoff badge drift (retired vocabulary),
  work-log stream split (PR vs issue number) and lost-on-failure saves.
- **Enforcement:** `close-spine` repository ruleset (id 19333120) greys the
  merge button until the close hop publishes the check — gates as mechanism,
  not vocabulary (operator: "operators will click the green button").
- **README:** edited (cloud-path paragraph in the off-terminal story) — commit
  1e2eb94. **ARCHITECTURE:** edited (new "The cloud path" section — trigger
  fired: new substrate, new roles, new connection) — commit f9506f4.
  **CHANGELOG:** promotion DEFERRED by the operator (2026-07-21) — the entry
  was authored, then withdrawn per the operator gate; it promotes in a later
  release round. Not a gap.
- **Follow-ups for the board** (orchestrator promotes): intake dedup on
  gh-ingest (duplicate stub for an existing task) · readiness ORIGIN stamping
  after a cloud MAKE IT SO (no role writes the board post-handoff) · hop
  wall-time measurement + resolved-id/branch hints in dispatch · REVISE
  dispatch lacks a comment input (role coped by reading the PR thread) ·
  cloud-path `--name` adoption per the naming contract · WATCH (half-fired):
  close-spine catches ALL PRs into main — the orchestrator's board-round PR
  #58 stranded BLOCKED; operator unblocking + adding repository-admin bypass
  (explicit "merge with bypass", no bare green button); orchestrator lane told
  to publish the check at its own close gate. Direct-push semantics VERIFIED
  (orchestrator, 2026-07-21): rulesets DO gate direct pushes — its board push
  was rejected; board-sync ingest and local close pushes are broken until the
  bypass list carries Repository admin + the GitHub Actions app (operator
  applying). close-spine semantics made canon in the workflow header: the
  check IS a closing role's published judgment; setting it without a passed
  close gate is forgery · nested-line projection gap (already filed by the
  orchestrator).

## Proposal

First slice = the FULL PATH (operator, 2026-07-20): a GitHub issue carries the feature;
the orchestrator's intake and the ripening rounds run as issue comments (driven manually
until the ripener charter lands); the architect is kicked off; tech plan with few or no
questions; the summary question → MAKE IT SO → pull request; THAT IS ALL → the
housekeeper amends and merges the PR. The local worktree spine is untouched. HOW —
Actions wiring, kick-off mechanics, the PR close path — is the architect's tech plan,
not pre-decided here (Decision-025/027).

### Agreed plan (frozen 2026-07-20, operator MAKE IT SO)

HOW, agreed with the operator:

- **Runtime:** hand-rolled headless CLI in GitHub Actions (`claude -p --agent <role>`),
  NOT the official claude-code-action — full control of role charters and gates.
- **Auth:** subscription OAuth token as repo secret `CLAUDE_CODE_OAUTH_TOKEN`
  (operator runs `claude setup-token`; external gate before live-fire).
- **Gate vocabulary** (comments, actor-gated to serialseb): kick-off = `ENGAGE` and/or
  ⚙️ · build gate = `MAKE IT SO` extended with 🖖 · close gate = `THAT IS ALL`
  extended with 🚪.
- **No orchestrator bypass:** hop 1 opens with a cloud-orchestrator prologue (board
  status → doing, delegated-to link, sidecar handoff check) before the architect runs;
  board writes keep their single writer. Operator-less statistical kick-off stays
  deferred with ripener automation.
- **Spine** (event-driven hops, no waiting jobs; state = issue thread + sidecar on
  branch `f/<id>`; no worktree, per the ratified design):
  hop 1 `ENGAGE` → prologue, branch, architect plan, plan comment ·
  hop 2 `MAKE IT SO` → resume, build, test, close docs, open PR (`Fixes #n`), PR
  review comments re-summon for revision ·
  hop 3 `THAT IS ALL` on the PR → housekeeper verifies docs, amends,
  `gh pr merge --squash`, `archive/<id>` tag + commit-count note.
- **Deliverables:** `agents/orchestrator-cloud.md` (prologue-only charter),
  `agents/architect-cloud.md`, `agents/housekeeper-cloud.md`,
  `.github/workflows/cloud-path.yml`, ARCHITECTURE cloud-path component, CHANGELOG.
- **Deferred:** ripener automation; autonomous-origin self-authorized MAKE IT SO;
  general comment→sidecar ingestion; consuming-repo rollout + cross-owner privacy fix
  (Decision-013 fallout); Orchidarium field updates from cloud hops.

## Testing

Agreed (operator, 2026-07-20): live-fire — one real feature through the full cloud
path on kaukea/orchids with every gate honoured (no self-approved MAKE IT SO, no
self-approved close). Target re-ruled (operator, 2026-07-21) after the first live hops: the
sidebar task (`fleet-sidebar`, gh#23) proved genuinely blocked on
`session-naming` — so **`session-naming` itself rides the live-fire**: its open
questions ARE the intake round on its issue, and shipping it unblocks the
sidebar for a follow-up cloud run. Flow: orchestrator projects it to an issue,
operator answers the intake questions as comments, sidecar ripens, `ENGAGE` →
gates given live. (Original target and the three refusal runs — auth 401 ×2,
not-ripe guard — are recorded in `## Findings`.)

TESTED (2026-07-21): the live-fire ran to completion — see the live-fire
record in `## Findings`. Every gate was operator-given; no agent
self-approved MAKE IT SO or the close; the close hop's three refusals under
imperfect gate evidence are part of the passing result.

Result: done · branch f/cloud-architect · live-fire passed on session-naming
(gh#34, PR #38, squash cfc7f283, archive/session-naming) · follow-ups listed
in Findings for board promotion.
