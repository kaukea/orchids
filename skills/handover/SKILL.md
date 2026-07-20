---
name: handover
description: The workstream-log protocol — how sessions pass work to successors and parents. Every session keeps its OWN small, rolling, parseable log in .git/the-works/<stream>/ (state, findings, dead ends, pending decisions, pointers), written as the work progresses, never at the end. A reset or agent change cannot destroy a workstream; the successor reads the stream's logs oldest-first. At close the stream is marked closed; the ingesting parent (or the top-level session itself) promotes pending decisions and remaining work into docs/decisions.md and the TODO, then archives the stream under .git/the-works/_ingested/ (provisional retention). Replaces the monolithic HANDOVER.md.
roles: [process/workflow]
share: github
compatibility: Requires git
metadata:
  tags: [handover, workstream-log, session, orchestration, chatter, close, reset, relay]
---

# Intent (workstream logs)

A workstream log bridges every session boundary — a child returning to its parent,
AND a bloated session being reset to a fresh successor of the same role. Both
readers get the same thing: enough to continue WITHOUT re-explaining or
re-deriving. Re-investigating what a previous session already did or already ruled
out is the waste this prevents.

One file PER SESSION, not one growing document. Agents skim large files and infer
the rest — small per-session files read whole are the countermeasure.

## Layout

```
$(git rev-parse --git-common-dir)/the-works/<stream>/
    <YYYYMMDD-HHMMSS>-<role>.md     one per session; name = session start, sortable
    _closed                          marker: stream finished, awaiting ingestion
```

- `<stream>` is the feature-id for workflow sessions; the role name (e.g.
  `orchestrator`) for role sessions outside a feature.
- INSIDE `.git/` — physically uncommittable, worktree-shared (Decision-008).
  This is the ONLY place conversational context, personal information, or
  anything sensitive may be written; committed docs carry sanitized technical
  state only (`AGENTS.shared.md` → Sensitive content rule).
- The writer creates the directory on first write (`mkdir -p`).

## Session log format

Created AT SESSION START, updated as the session progresses — never reconstructed
at the end. Fixed sections so logs parse and merge mechanically:

```markdown
- session: <YYYY-MM-DD HH:MM TZ> start
- role: <role> (<model>)
- stream: <stream-id>

## State
The one section REWRITTEN in place: where things stand right now, and the next
step. A successor reading only this section can continue.

## Findings
Appended when established, not at close: verified facts, measurements, results.

## Dead ends
Paths tried and failed, and WHY — so no successor retries them.

## Decisions (pending promotion)
Rulings agreed with the operator this session, awaiting promotion to
docs/decisions.md at ingest. Sanitized wording — they will be committed.

## Dispatched sub-agents
The LEDGER. One line per sub-agent AT THE MOMENT IT IS DISPATCHED — never after
it returns: `<id/label> · <what it was sent to do> · dispatched <HH:MM> ·
returned <HH:MM|NO>`. Mark the return when it lands. A sub-agent in flight lives
only in process memory; if the process exits, this ledger is the ONLY trace that
something was running. It is what the end-of-task guard (below) reads.

## Pointers
Files, docs, URLs, sidecars a successor needs. Enough for a cold start.
```

Confidence-mark entries: **verified** (and how) vs **suspected**.

## Rules of the stream

- **One session, one file.** A session NEVER edits another session's log — it
  reads them (oldest→newest; later supersedes older) and writes only its own.
- **Rolling, not retrospective.** State is updated when it changes; findings and
  dead ends land when they happen. A session that dies mid-flight has, by
  construction, already written what its successor needs — this is what makes a
  reset or an agent swap non-destructive.
- **Write AS you change, not in catch-ups.** The log is written at the moment of
  the change — each state change, finding, dead end, decision and dispatch is
  flushed as it happens, never batched into a periodic summary. Batching
  reintroduces exactly the window this protocol exists to close: everything
  since the last catch-up dies with the process. This binds every role,
  including the orchestrator.

## End-of-task guard (MUST)

Before ANY session declares its work finished — an architect presenting `done` or
countersigning, a role session reporting a task complete, an orchestrator reporting
a feature closed — it MUST clear this guard:

- [ ] **No sub-agent left in flight.** Every entry in the `## Dispatched sub-agents`
  ledger has returned, was re-dispatched, or is explicitly recorded as abandoned with
  its work reassigned. A session NEVER ends with an unreturned sub-agent.
- [ ] **End state verified by observation, not by report.** Where the work has an
  observable end state, check the state itself rather than trusting an agent's
  summary — for a close: the tag exists, the branch is gone, the squash is on `main`,
  the push landed, the worktree is removed, the tree is clean. Reports can be lost,
  stale, or wrong; the repository cannot.
- **Durable facts still go to their homes** — the log is the staging area, not
  the destination. Sanitized technical findings are flushed to the stream's
  committed sidecar (`## Findings`) by the session that owns it; decisions and
  remaining work reach `docs/decisions.md` / the TODO via promotion (below),
  never directly from a child session (single-writer: the board and decisions
  belong to the orchestrator / top-level session).
- **Not everything leaves the stream.** Most log content is useful only inside
  the workstream; at ingestion it retires to `_ingested/` rather than being
  promoted — that is by design.

## Reset / agent change (the relay)

Nothing special to write: the rolling log IS the relay. The successor session of
the same stream reads the directory oldest-first, then opens its own file and
continues. Link at the moment of deferral still applies: if work is split or
delegated, the TODO relationship is written when it happens, not left in the log.

## Close (a stream finishing)

As part of the close housework (`workflow-complete`):

1. Append the final `## State`: outcome `done` | `reverted` | `wip`, merged SHA
   or tombstone tag.
2. Flush sanitized durable findings into the stream's committed sidecar.
3. `touch <stream-dir>/_closed` — the marker the hook announces to the parent.

## Ingest (parent — or the top-level session itself)

The `_closed` marker (announced by the shared `settings.json` hook) means a
stream awaits ingestion. The ingester MUST:

1. **Read** the stream's logs oldest→newest — later entries supersede older.
   **TRUST YOUR BRANCH**: act on them; do not re-derive the work.
2. **Promote**: `## Decisions (pending promotion)` → `docs/decisions.md`
   (canonical format); remaining/follow-up work → the TODO; any standing
   constraint (still true, nameable reader, expiry trigger) → a one-line
   constraint on the relevant TODO item.
3. **Archive the stream directory** the moment ingestion is done — move it to
   `$(git rev-parse --git-common-dir)/the-works/_ingested/<stream>/` (still
   uncommittable; outside the hook's announcement glob). PROVISIONAL retention:
   ingested logs are kept while we learn whether their negative record (dead
   ends, failures) earns its keep for cross-checking README / CHANGELOG /
   commit claims; the retention ruling follows after a few weeks of use.

A top-level session (no parent above it) self-promotes at its own close — the
symmetric protocol needs no knowledge of tree depth: finish → mark closed →
whoever is above ingests; if no one is, you are the promoter.

## Rules

- Sensitive content ONLY here (and MOOD.md) — never in committed files. Found
  committed → scrubbed immediately, history rewrite included
  (`AGENTS.shared.md`).
- One file per session; rolling updates; read oldest→newest.
- Ingest-then-archive — a closed stream never lingers in the announcement
  path after promotion; it moves to `_ingested/` (provisional retention).
- Promotion is the ingester's job — child sessions do not write the board or
  `docs/decisions.md` directly.
- Override: the operator may bypass any rule per-session by saying so.
