- created: 2026-07-19
- created_by: fable-5
- created_during: f/status-channel

## Blockers

_None._

## Questions

- Can the operator's pane suppress per-event Monitor lines? The operator believes it is
  optional; the `Monitor` tool schema exposes no display control and no config tool is
  reachable from a session. Does not block the feature — only how noisy it looks.

## Findings

Established empirically 2026-07-19 (each verified, not inferred):

- **`SendMessage` reaches only agents spawned from within your own session.** A separate
  process with a name and a registry id is NOT reachable — tested against a purpose-built
  background session and against a foreign one, by name, by short id and by sessionId, all
  rejected. Discoverability is not addressability.
- **A subagent CAN push to its parent unprompted.** `SendMessage(to: "main")` from a subagent
  that was never messaged first returns `"Message queued for the main conversation's next
  turn."` and arrives wrapped as `<agent-message from=…>` with a harness warning that it is
  not user input — so an agent message structurally cannot impersonate operator authority.
- **An event creates a turn.** Notifications wake an otherwise-idle session; no polling loop
  is needed, and an idle or finished subagent costs nothing while waiting.
- **Monitor events land with whoever ARMED the monitor.** A subagent-armed monitor delivered
  all events to the subagent; the parent received none (verified by token absence). This is
  what keeps the raw stream out of the orchestrator's context.
- **The operator sees only the monitor's `description`, once per event — never the payload.**
  So `description` is operator-facing copy, not a debug label, and the payload is invisible
  to them (which is why a rendered board is the only informative artefact).
- **No CLI route injects a turn into a live session** (`--resume` and `--session-id` both
  refuse; the lock is transcript-write concurrency). `tmux send-keys` does work but arrives
  indistinguishable from operator typing — rejected as a channel for that reason.
- Nothing ships that provides a broker (no MCP pub/sub reference server, no connectable
  supervisor endpoint); the agent-teams mailbox is experimental and Claude Code deletes
  entries it does not recognise. The filesystem is the broker we already have.

## Proposal

A repo-scoped message bus. Agents never touch the mechanism: a **bus sidecar** owns sending
and receiving, and a **script** owns the envelope on both sides, so no agent learns the
format, the paths, or the ordering rules. Implementation must not leak into any prompt.

**Identity.** Every agent gets an ID at birth; that ID is its address. Its inbox is a folder
named for it under the repo's bus root. The set of folders IS the registry — broadcast writes
a copy into each, and there is nothing separate to maintain. The folder is created at session
start and removed at session end.

**Messages.** Ephemeral — deleted on consumption, so reading is "open the folder and take
what is there" with no bookkeeping. One JSON object per file, named `<datetime>.json` so
ordering is lexical.

**Envelope** (owned by the script, enforced on send and receive): sender, type, a
user-visible flag so an agent can surface something to the operator with no extra machinery,
and for request/response a request id plus in-reply-to, so an agent can have several requests
outstanding and match replies asynchronously.

**Kinds:** post, broadcast, request, reply.

**Delivery.** The sidecar watches its agent's folder (not a touch-file: one write, no second
step to forget) and drains the whole folder on any event, so a missed event self-heals. It
hands messages up with `SendMessage` — the only direction that can inject into a parent's
conversation.

**Injection.** A `SessionStart` hook creates the folder and tells the agent its inbox and to
load its bus. The **ID is withheld and returned by the bus** — a gate rather than a nudge, so
an agent that skips loading it cannot address anything or be addressed.

**Not in v1** (deliberate, revisit only on a real use case): opt-out and filtering, delivery
timeouts (they would need a scheduler; a requester can notice its own silence), conformance
detection (divergence between worktree activity and absent messages exposes it for free), and
crossing repository boundaries — that is [[orchard]].

**First consumer:** the architect emits a status transition at each state change
(`started` · `loaded` · `developing` · `spawning-agent` · `testing` · `blocked` ·
`finished` · `failed` · `abandoned`), so the orchestrator can hold a live board. Failure
states are mandatory: silence must never be mistakeable for progress.

## Testing

Operator-agreed — exercised end to end before this closes:

1. **Script, in isolation:** send, broadcast, request/reply and drain each produce and consume
   well-formed envelopes; ordering is preserved; consumed messages are deleted.
2. **Registry:** folder created at start, present for broadcast, removed at end.
3. **Sidecar:** a bus subagent watching a folder receives a message written by another process
   and delivers it upward — verified by a token that must appear in the parent context.
4. **Isolation:** raw traffic does NOT reach the parent except through the sidecar (verified by
   a token that must NOT appear).
5. **Gate:** an agent that never loads its bus has no ID and cannot send.

Pass = each observed live. A clean read of the code is not a pass.

## Handover — state at handoff (2026-07-19)

**Written by the orchestrator, which should not have been building this.** Three files exist
and are committed; treat them as a FIRST DRAFT to be reviewed, not as settled work.

Done (each committed with its own message):
- `tools/bus.py` — the envelope owner. Tested in isolation and passing: ordering preserved,
  broadcast reaches every peer and excludes the sender, request/reply correlate by id, drain
  empties, teardown clears the registry, atomic writes leave no partials, and sending to an
  agent with no inbox fails loudly. Identity derives from location (`whoami`): a linked
  worktree is its feature id, the main checkout is `orch`.
- `agents/bus.md` — the sidecar role.
- `hooks/bus-init.sh` + `settings.json` SessionStart wiring — creates the inbox and injects.
  Verified: valid JSON, inbox created, and the injection leaks neither identity nor path.

**REQUIRED: a full code review of all three before anything else.** They were written by one
agent in one pass with no second pair of eyes. Review at minimum: the `whoami` derivation
(what happens outside a git repo, or with two agents in one checkout — the orchestrator and a
groomer would collide on `orch`); concurrent drain versus delivery; whether `teardown` at
session end can strand messages; error paths; and whether the sidecar prompt can be made
harder to ignore.

Remaining work:
1. The architect and orchestrator definition edits — the architect asks its bus to send a
   status update at each transition (`started` · `loaded` · `developing` · `spawning-agent` ·
   `testing` · `blocked` · `finished` · `failed` · `abandoned`, failure states mandatory so a
   dead architect is never silent); the orchestrator keeps a board from what arrives and
   renders it. Behaviour only — NO mechanism in either prompt.
2. Testing gates 3, 4 and 5 from `## Testing` above, which are NOT yet done: a live bus
   subagent receiving a message written by another process and delivering it upward; the
   isolation check (raw traffic must not reach the parent except through the sidecar); and
   the gate check (an agent that never loads its bus cannot send).

Do not widen scope beyond this. Orchard (cross-repo) and injection-integrity are separate
board tasks and stay there.
