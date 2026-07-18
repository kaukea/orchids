- created: 2026-07-18
- created_by: operator
- created_during: f/workstream-log

## Blockers
- Lives upstream: the sync/install procedure is the kauk skill's
  (`serialseb/kauk`, pull-only). Carried here until handed over.

## Questions
- None — operator chose the simple form over per-file delta handling.

## Findings
- A running session loads skills, its own agent definition, and the rule files
  at start; `kauk sync` updating the clone does NOT refresh any of it — the
  session keeps obeying stale text.
- Operator ruling (2026-07-18): keep it SIMPLE — no per-file classification or
  partial reload logic; far from release, twelve projects in.
- Workstream logs (Decision-011) make a reset cheap and lossless: the successor
  boots on the new package with the thread intact.

## Proposal
Two changes to the kauk skill's sync/install procedure. First, retime the sync
(operator ruling 2026-07-18): START of a session/workflow = pull and converge —
absorbing changes there is nearly free (nothing invested yet, reset trivial);
END of a workflow = push-back ONLY when the stream edited vendored package
files, never a pull (the next session converges at its own start). Second, the
reset rule: if the pull
changed anything (non-empty diff old..new SHA), tell the operator plainly —
"kauk pulled updates; to run on them, reset this session (the workstream log
carries the thread)" — and let the operator decide. Declining is fine;
re-reading an individual changed skill remains the cheap fallback. No hook, no
delta analysis.

## Testing
In a consuming repo: sync with upstream changes → the message appears; sync
with no changes → silence. After an accepted reset, the new session runs the
updated skill text.
