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

## Findings — build + test (2026-07-19, architect)

Code review of the three drafts found, and the build fixed:

- **Identity was derived from the working directory.** It ignored the environment,
  which already publishes the answer, and collided for any two sessions sharing a
  location (orchestrator + groomer both resolved to `orch`). Now
  `CLAUDE_CODE_SESSION_ID`.
- **None of the three bus files were in `manifest.conf`.** They were never linked into
  `.claude/`, so `settings.json`'s SessionStart hook pointed at a path that did not
  exist and the sidecar's `.claude/tools/bus.py` resolved to nothing. The bus had
  never actually run in any session.
- **`teardown` existed but nothing called it** — no SessionEnd wiring anywhere. Dead
  inboxes persisted, so `send` to a finished agent returned exit 0 and the message sat
  forever. Both files promised loud failure; that promise was false. Now wired.
- **The sidecar only drained on monitor events**, so a message already waiting fired no
  event and was never collected. It now drains once at arm time.
- **The "withheld id is a structural gate" claim was false** and is removed — the id is
  an environment variable. What the design gives is detection (an agent that never
  announces is visibly absent), not prevention.
- Malformed envelopes are no longer unlinked after the error is recorded, so a bad
  message can actually be inspected.

Empirically established (verified, not inferred):

- A subagent **inherits its parent's environment verbatim** — session id, agent type,
  PID. Load-bearing: it is what lets a sidecar resolve to its parent's mailbox without
  being told, and it is why subagents cannot be separately addressed by env alone.
- `--session-id <uuid>` **mints a new session at a chosen id**, so a creator can know a
  created agent's address before first contact.
- The sidecar can **read its parent's transcript** (shared session id), so occupancy and
  spend need no cooperation from the parent.
- **`persistent: true` on the Monitor is mandatory.** Without it the watch expires after
  five minutes and the agent goes deaf while still reporting itself as listening —
  observed live. With it, a file event wakes the subagent even though its turn has
  ended.

## Testing — results

1. **Script in isolation — PASS.** Ordering preserved, drain empties, second drain
   returns `[]`, broadcast reaches peers and excludes the sender, request/reply carry
   their ids, 8 concurrent sends all landed with no filename collision, atomic writes
   leave no partials. Clean errors (not tracebacks) outside a git repo and with no
   session id.
2. **Registry — PASS.** Inbox created at start, present for broadcast, removed by
   teardown; send to a torn-down agent exits 1 with a clear message.
3. **Sidecar delivery — PASS.** A live bus subagent, woken by a persistent monitor,
   drained a message written by a separate process and relayed it upward; the token
   `WAKE-TOKEN-BASILISK-4402` appeared in the parent's context as prose.
4. **Isolation — PASS.** The envelope id `d9c22a6b9efe` never reached the parent. No
   JSON, no file names, no paths — only prose. The `visible` flag was reported
   correctly as internal.
   Bonus: two sidecars raced on one inbox; one drained, the other got `[]`. No duplicate
   delivery, no crash.
5. **Gate — FAILS AS WRITTEN, and cannot pass.** The gate tested "no bus => no ID =>
   cannot send". Demonstrated false: `$CLAUDE_CODE_SESSION_ID` is readable by any agent
   and a send with no sidecar loaded returned exit 0 and was delivered. The property was
   removed deliberately (Decision-017). The replacement property holds: an agent that
   never loads a bus never announces, so it is invisible to its peers — detection rather
   than prevention. **Operator ruling wanted on whether that substitution is accepted.**

## Deferred — for the orchestrator

- **Model + effort in identity/status.** Parked deliberately: identity-at-birth and
  status-at-time can legitimately differ (a model disengaging, tokens running out), so
  it needs a rule for which wins, not just a field.
- **Denominators** (context window size, rate card) — land with the model decision, and
  until then counts ship raw: occupancy cannot be expressed as a percentage and spend
  cannot be turned into money.
- **Phase-two lean `HELLO` + lazy metadata fetch.** Not scheduled: at present n it costs
  more than the broadcast it replaces. Measured trigger — large n with sparse interest,
  i.e. once orchard exists.
- **Ongoing sidecar liveness.** Announcement proves the bus loaded at birth; nothing
  detects a sidecar that dies mid-session, and the agent then goes deaf silently.
- **Monitor per-event line suppression** (pre-existing question above).
- **Status transitions.** The `started · loaded · developing · spawning-agent · testing ·
  blocked · finished · failed · abandoned` state machine is NOT built. `orchid:status`
  is pull-based and sidecar-answered, so it reports `live` from the transcript but
  cannot know the parent's workflow state — only the parent can push that. Whether the
  architect/orchestrator definitions gain that is an open scope call (see Result).

Result: done — bus mechanism built and tested; branch `f/status-channel`; gates 1-4 pass
live, gate 5 rejected as written with a replacement proposed. No tasks spawned; deferred
items above are for the orchestrator to triage.

## Parent session — decided, wiring deferred to the spawn (2026-07-20)

- The bus already READS `ORCHID_PARENT_SESSION` (identity_of); the consuming side is done.
- Producing side: the orchestrator passes its own id as an env var on the architect's launch
  line — `ORCHID_PARENT_SESSION=$CLAUDE_CODE_SESSION_ID claude --agent architect …`. Env var,
  not a file, because we own the command line. This is ONE string on the spawn command and
  belongs to the spawn/tmux work, NOT this feature — do not couple it here or touch the tmux
  layout for it.
- Agent type needs no passing: an agent launched with `--agent <x>` is aware of what it is;
  `identity` takes the type from the agent, not from an env var.
- Until the spawn wires the env var, an architect's identity broadcast carries
  `parent_session: null`. Acceptable; it resolves when the spawn work lands.
