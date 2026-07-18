---
name: handover
description: The handover protocol. NOT a manual command — the handover is written only as part of the close housework (the workflow-complete skill) that MAKE IT SO triggers, at success or abandonment. Writes a transient, uncommittable HANDOVER.md (in .git/the-works/) carrying CHATTER ONLY — short-lived gotchas the spawning parent needs, nothing else — so the parent absorbs the child WITHOUT re-deriving it. Durable facts never go here; they are appended straight into decisions/changelog/todo. Also defines how a parent ingests one on a child's return.
share: github
compatibility: Requires git
metadata:
  tags: [handover, branch, session, orchestration, chatter, close, makeitso]
---

# Intent (handover)

A handover bridges a child session and the parent that spawned it, so the parent
absorbs the child's work by reading it — never by re-deriving it. Re-investigating what
a branch already did is the token waste this prevents.

**The handover carries CHATTER ONLY.** Durable facts do NOT belong here:

- A decision made → appended to `docs/decisions.md` (`AGENTS.files.md` §Decisions).
- Work done / a feature finished → `CHANGELOG.md`.
- Remaining or follow-up work, and the LINK that explains it ("was scheduled for X,
  moved to Y as a follow-up") → the board (`docs/TODO.md` + sidecar), written at the
  moment of deferral, not at handover time.

Those live in append-only durable docs; the parent finds what's new by reading their
tail (decisions by date/number, the CHANGELOG `Work in progress` section), never by
re-reading the whole file and never from a copy in the handover. Duplicating them into
the handover is the waste this protocol removes.

What is left — and all the handover is for — is **chatter**: short-lived, no-durable-
home context the parent needs to not stumble. *"Got that part done; USB port 3 is dead,
don't retry it; the process is stopped at step 4; good luck."* Useful for exactly one
hop, then gone.

## Symmetric protocol — every node, same behaviour

An agent never needs to know its depth in the tree (whether it has children, or is
itself a child). The protocol is identical at every node:

- **On finish** — route durable facts to their homes (with links), then write a
  handover up for whoever spawned you. Do this whether or not you think anyone is above
  you; if no one is, the next session ingests it.
- **On receive** — ingest (below). The return-hook fires for any session that opens and
  finds `HANDOVER.md`, regardless of tree position.

Because chatter is one-hop (consumed and dropped on ingest) and durable facts converge
in the same append-only docs at every level, the reduction to deltas happens on its
own — the top parent sees deltas plus one layer of chatter, never the whole subtree.

## File

- Path: `$(git rev-parse --git-common-dir)/the-works/HANDOVER.md` — INSIDE `.git/`, so it is
  **physically uncommittable**: no `git add -A`, no forgotten gitignore, no accident
  can ever land it in history. The common dir means a worktree child and the
  main-checkout parent see the same file. The writer creates `the-works/` if it
  does not exist yet (`mkdir -p`).
- This is the ONLY channel where conversational context, personal information, or
  anything sensitive may be written. Such content NEVER goes into committed files
  (sidecars, TODO, decisions, changelog, commit messages). If such content is ever
  found committed — including in past history — it is scrubbed the moment it is
  detected, history rewrite included (`AGENTS.shared.md` → Sensitive content rule).
- Self-destructing: the parent deletes it the MOMENT it has read it.

## Write it (during the close housework — never a manual command)

There is no `/handover` command. The handover is written as a step of `workflow-complete`
when a workflow closes — at success (squash) or abandonment (cancellation). A mid-work
pause does NOT produce a handover: switching away gives the child no turn (Decision-051),
and the branch + durable docs carry the state. First make sure every durable fact has
reached its home (decision / changelog / todo + links). Then the handover holds only:

- Branch / feature-id and outcome: `done` | `reverted` | `wip`.
- **Chatter** — gotchas, dead-ends not to repeat, current state of an in-flight
  process, incidental context the parent needs.
- **Confidence marks** — what is **verified** (and how) vs **suspected**, so the parent
  can trust precisely.

Write to be trusted: you had full context the parent lacks; a complete, honest,
confidence-marked handover is what lets the parent act without re-deriving. Then confirm
it's written and tell the operator it's safe to start a fresh session.

## Ingest it (parent session, on a child's return)

**Batch rule** — when several `HANDOVER*.md` files sit in `.git/the-works/` (e.g.
strays gathered by a migration under provenance-stamped names), ingest ALL of them
in one boot pass, oldest-first by mtime, each per the steps below. Legacy strays may
predate the durable-facts discipline: anything durable-looking found inside (a
decision, an outcome, deferred work) is promoted to its proper home
(decisions / CHANGELOG / board) during triage instead of assumed already there.

The parent MUST:

1. **Read** `HANDOVER.md`. **TRUST YOUR BRANCH** — act on it; do not re-derive the
   child's work or sweep the repo to "confirm" it. The child knew more than you do now;
   re-investigation is waste and usually reaches a worse answer. Read only the specific
   durable entries you actually need (decisions tail, the todo).
2. **Triage each chatter line:**
   - **Spent** (value ends once read — "stopped at step 4") → drop it.
   - **Standing** (still true, with a nameable reader + expiry trigger — "USB3 dead
     until the hardware swap") → it is no longer chatter; promote it to a one-line
     active constraint on the relevant `TODO` item, carrying its removal trigger.
     Removed later by whoever satisfies that trigger.
3. **Delete** it — the moment it is read, like the old Mission Impossible tapes. Always. Nothing is lost: durable facts were already in
   their homes, and anything that had to outlive one hop was just promoted with its own
   expiry.

## Rules

- Chatter only — durable facts go to decisions/changelog/todo, never the handover.
- It lives under `.git/` — uncommittable by construction; never copy it into the tree.
- Ingest-then-delete — never left stale; a gathered batch drains fully in one pass.
- TRUST YOUR BRANCH — the receiver acts on the handover and does not re-derive; the
  writer earns that trust with a complete, confidence-marked handover.
- Link at the moment of deferral — the "moved from X to Y" relationship goes into the
  `TODO`, not the handover (see `AGENTS.shared.md` → Handover & delegation).
- Override: the operator may bypass any rule per-session by saying so.
