- created: 2026-07-22
- created_by: gh-ingest
- created_during: interactive

## Blockers
- None known yet.

## Questions
- Ingested from GitHub issue #125 — needs triage: type, component,
  urgency, scope.

## Findings
- Filed on GitHub (https://github.com/kaukea/orchids/issues/125); original body preserved below.

#cloud #gates #vocabulary #oauth #actions #handoff #badge #context #worklog #close-spine #app

> Close-spine ruleset clause superseded by Decision-040 (ruleset deleted; approach dropped).

Promoted from the cloud-architect stream (operator rulings, 2026-07-20/21):

- Runtime: hand-rolled headless CLI workflows (`claude -p --agent <role>` in
  GitHub Actions), NOT the official claude-code-action — full control of role
  charters and gates, matching the local spine. Auth: the subscription OAuth
  token (`claude setup-token` → repo secret), not a metered API key.
- Gate vocabulary amended (extends Decision-030): `MAKE IT SO` also accepts 🖖;
  `THAT IS ALL` also accepts 🚪. Gates are EXACT-form: the comment must BE the
  gate token, trimmed — a quoting comment never fires a hop. Actor-gated.
- ENGAGE does not bypass the orchestrator: hop 1 runs a cloud-orchestrator
  prologue (board handoff, sidecar ripeness) before any architect. Handoff badge
  contract: readiness stage → working ONLY; status stays todo; gh# inviolable;
  delegated-to lives in an issue comment.
- Context economy: the SIDECAR is canonical after each fold; hops read sidecar +
  gate comment, not the thread; every hop's last act writes handoff state back.
- Cloud work log rides the Actions cache (relay, not archive; housekeeper
  ingests before merge) — runners share no .git/the-works.
- close-spine: the status check IS a closing role's published judgment — setting
  it without a passed close gate is forgery. Org prerequisites documented in the
  workflow header ("Allow Actions to create PRs" ON). The ruleset is DISABLED
  until the named kaukea GitHub App exists (the built-in Actions identity cannot
  be bypass-listed) — re-enabling rides the app follow-up.
