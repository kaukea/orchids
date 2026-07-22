- created: 2026-07-22
- created_by: gh-ingest
- created_during: interactive

## Blockers
- None known yet.

## Questions
- Ingested from GitHub issue #116 — needs triage: type, component,
  urgency, scope.

## Findings
- Filed on GitHub (https://github.com/kaukea/orchids/issues/116); original body preserved below.

#bus #lifecycle #close #choreography #hooks #teardown #liveness #metadata #status #tmux

Shipped by [[hook-choreography]] (operator plan-gate rulings, 2026-07-20/21):

- Lifecycle signal on the bus: `bus.py signal --state <started|building|testing|done|finished|blocked|abandoned>`,
  body `{kind: lifecycle, state, feature_id}`; directed to `ORCHID_PARENT_SESSION`
  when known and live, else broadcast. The parent session id is wired into the
  environment at architect spawn.
- The close rides the signals: the architect signals `done` at its gate and
  `finished` at the ALL IT IS countersign; the orchestrator acts on `finished`.
  The operator's THAT IS ALL is the SOLE close gate (PR-merge semantics — a comment
  before it means amend/abandon). There is NO separate "close it" step.
- Teardown division: the orchestrator owns tmux (`tools/architect-teardown.sh` —
  focus-return, then kill the `arch:<id>` pane found by TITLE); the housekeeper owns
  the git close, unchanged. The transcript-grep Stop hook, its jq race and the
  `/tmp/architect-close.log` leak are retired.
- Liveness: when a close is expected and the architect looks absent, the orchestrator
  inspects the pane directly (gone / pane_dead); the bus `orchid:status` probe is
  secondary; no scheduler. The broad [[bus-liveness]] framework stays deferred.
- Metadata ([[agent-metadata]] folded in): model + effort ride `orchid:status`
  (mutable), NOT identity — resolving Decision-018's open which-wins question: status
  is the live truth for mutable fields, identity the birth record. Token classes stay
  broken out; effort reads null until an env source exists.
