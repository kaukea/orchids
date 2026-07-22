#!/usr/bin/env python3
"""Token-free question-popup broker (sidebar-polish item 12c-f).

An agent asks a question over the bus (`bus.py ask`); this script — a plain
long-running process, never an agent, never spending a token — is what makes
that ask() actually reach the operator and come back with an answer:

    watch loop -> finds a new question broadcast (tools/bus.py's
    _question_envelope, scanned via tools/sidebar_model.py's own bus-root
    resolution, never a re-derived traversal) -> waits until the operator is
    not mid-input (12e) -> pops a native `tmux display-popup` over the
    operator's CURRENT window (12c) -> reads keypresses, accepting ONLY the
    defined option keys, no default/dismiss/timeout (12d) -> sends the
    answer back over the bus to the asking session (`bus.py send
    --in-reply-to`).

None of this is parameterizable by the asking agent (12f): `bus.py ask` has
no flag that skips deferral or widens the accepted keys — those rules live
entirely here.

Design split (mirrors tools/sidebar.py's render_lines()/curses split): every
decision is a pure function taking plain data — match_option_key(),
is_operator_busy(), pending_questions() — unit-testable with no tty, no
tmux, no live process. Only main()/_handle_question()/the tmux/termios calls
below them are I/O and need a live tmux session to exercise for real; that
part is NOT covered by tests/test_orchard_question_broker.py and needs a
human/live check (see the step's report).

ASSUMPTIONS flagged for the operator (this trial's HOW decisions):
  - "operator's current window" is resolved via the most recently active
    attached tmux CLIENT (`tmux list-clients`), then that client's current
    window — the best fleet-wide proxy available; a single-operator,
    possibly-multi-client tmux server is assumed.
  - "recent activity" (the idle fallback for typing outside a claude
    session, 12e) is tmux's own `client_activity` — updated on every
    keystroke sent to the server, independent of the harness. There is no
    per-keystroke Claude Code hook; the harness only exposes UserPromptSubmit
    (fires on SEND, not while typing), which is used here as the "just
    submitted, safe now" signal that overrides mere recency of pane activity
    for one instant, per is_operator_busy()'s docstring.
  - `bus.py ask` itself has no timeout (blocks until answered) — the
    no-timeout-auto-pick rule (12d) is about the POPUP's keypress handling,
    not about how long an agent's ask() may block.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sidebar_model  # noqa: E402

_TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
_BUS_PY = os.path.join(_TOOLS_DIR, "bus.py")

# Sender identity this script uses when it answers a question over the bus —
# it is not an agent session, so it has no CLAUDE_CODE_SESSION_ID of its own.
BROKER_SENDER = "question-broker"

DEFAULT_POLL_SECONDS = 1.0
DEFAULT_IDLE_SECONDS = 5.0  # reuses item 9's "~5s" waiting threshold convention


# --------------------------------------------------------------------------
# Pure decision functions — unit-tested directly, no tty/tmux involved.
# --------------------------------------------------------------------------

def match_option_key(key: str, num_options: int) -> int | None:
    """Sidebar-polish item 12d: the popup responds ONLY to its defined
    option keys and ignores every other keypress — no default, no
    dismiss-on-any-key, no timeout auto-pick.

    Options are numbered 1..num_options; `key` is accepted iff it is exactly
    one of those digit characters. Returns the 0-based option index, or
    None for anything else (letters, arrows, enter, escape, punctuation,
    multi-char sequences, empty input) — the caller's loop simply keeps
    reading on None, never treating it as a selection.
    """
    if num_options <= 0 or len(key) != 1 or not key.isdigit():
        return None
    n = int(key)
    if 1 <= n <= num_options:
        return n - 1
    return None


def is_operator_busy(now: float, last_submit_ts: float | None,
                      last_activity_ts: float | None, idle_seconds: float) -> bool:
    """Sidebar-polish item 12e: True means DEFER (do not pop yet).

    Clear to pop (returns False) when either:
      - there has been no raw input activity for `idle_seconds` (the idle
        fallback, for typing outside a claude session), or
      - the most recent signal is a submit (UserPromptSubmit fired at or
        after the last observed activity) — a submit is the harness's
        explicit "I just sent it" signal and takes precedence over mere
        recency, since the send keystroke itself is also "activity".

    Otherwise (recent activity with no submit since) the operator is taken
    to have input in flight, and the caller must not pop.
    """
    if last_activity_ts is None:
        return False
    if now - last_activity_ts >= idle_seconds:
        return False
    if last_submit_ts is not None and last_submit_ts >= last_activity_ts:
        return False
    return True


def pending_questions(bus_roots: list[Path], seen_ids: set[str]) -> list[dict]:
    """Scan every bus root for question broadcasts not in `seen_ids`.

    Non-destructive peek — mirrors tools/sidebar_model.py's own
    _BusAggregator.scan(): messages are owned by their recipients, this
    script only looks. A question fans out to every peer's inbox as one
    copy per peer (each with a fresh envelope `id` but the SAME
    `question_id`), so within a single call this also de-duplicates on
    question_id — the caller only needs to fold the returned question_ids
    into `seen_ids` once handled.

    Returns dicts sorted by `ts`: {question_id, question, options, asker}.
    """
    found: dict[str, dict] = {}
    for root in bus_roots:
        if not root.is_dir():
            continue
        for session_dir in root.iterdir():
            if not session_dir.is_dir():
                continue
            for f in session_dir.glob("*.json"):
                if f.name.startswith("."):
                    continue
                try:
                    env = json.loads(f.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    continue
                qid = env.get("question_id")
                if not qid or qid in seen_ids or qid in found:
                    continue
                found[qid] = {
                    "question_id": qid,
                    "question": env.get("question"),
                    "options": env.get("options") or [],
                    "asker": env.get("from"),
                    "ts": env.get("ts") or "",
                }
    return sorted(found.values(), key=lambda q: q["ts"])


# --------------------------------------------------------------------------
# I/O glue — needs a live tmux session / real tty; not unit-tested.
# --------------------------------------------------------------------------

def _run(cmd: list[str]) -> str:
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return ""
    return out.stdout.strip() if out.returncode == 0 else ""


def _broker_dir() -> Path | None:
    common = _run(["git", "rev-parse", "--git-common-dir"])
    if not common:
        return None
    return Path(common).resolve() / "the-works" / "broker"


def _last_submit_ts() -> float | None:
    d = _broker_dir()
    if d is None:
        return None
    marker = d / "last-submit-ts"
    try:
        return float(marker.read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        return None


def _last_client_activity_ts() -> float | None:
    """Most recent `client_activity` (epoch seconds) across attached tmux
    clients — tmux's own raw-input-recency signal, independent of the
    harness (see module ASSUMPTIONS)."""
    out = _run(["tmux", "list-clients", "-F", "#{client_activity}"])
    values = [float(v) for v in out.splitlines() if v.strip().isdigit()]
    return max(values) if values else None


def _operator_current_window() -> str | None:
    """The window of the most recently active attached tmux client — the
    best fleet-wide proxy for "wherever the operator currently is" (see
    module ASSUMPTIONS)."""
    out = _run(["tmux", "list-clients", "-F", "#{client_activity} #{client_session}"])
    best_ts, best_session = None, None
    for line in out.splitlines():
        parts = line.split(" ", 1)
        if len(parts) != 2 or not parts[0].isdigit():
            continue
        ts, session = float(parts[0]), parts[1]
        if best_ts is None or ts > best_ts:
            best_ts, best_session = ts, session
    if best_session is None:
        return None
    return _run(["tmux", "display-message", "-p", "-t", best_session, "#{window_id}"]) or None


def _popup_read_main(question: str, options: list[str], answer_file: str) -> None:
    """Runs INSIDE the tmux popup: prints the question + numbered options,
    then a raw-mode key reader that only exits on a valid option key (item
    12d) — no default, no dismiss-on-any-key, no timeout."""
    import termios
    import tty

    numbered = "\r\n".join(f"{i + 1}. {opt}" for i, opt in enumerate(options))
    sys.stdout.write(f"{question}\r\n\r\n{numbered}\r\n")
    sys.stdout.flush()

    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        while True:
            ch = sys.stdin.read(1)
            idx = match_option_key(ch, len(options))
            if idx is not None:
                break
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
    Path(answer_file).write_text(
        json.dumps({"index": idx, "option": options[idx]}), encoding="utf-8",
    )


def _shell_quote(s: str) -> str:
    import shlex
    return shlex.quote(s)


def _render_popup(window: str, question: str, options: list[str]) -> dict | None:
    """Pops a native tmux popup over `window` (item 12c) running the inner
    reader above; blocks until it exits (a valid key was read — the inner
    reader itself never returns early), then reads the answer file it wrote.
    """
    answer_file = f"/tmp/.orchard-question-answer-{os.getpid()}-{int(time.time() * 1000)}.json"
    inner = [
        sys.executable, os.path.abspath(__file__), "_popup-read",
        "--question", question, "--answer-file", answer_file,
    ]
    for opt in options:
        inner += ["--option", opt]
    cmd = ["tmux", "display-popup", "-E"]
    if window:
        cmd += ["-t", window]
    cmd += ["-T", " orchid question ", " ".join(_shell_quote(c) for c in inner)]
    try:
        subprocess.run(cmd, timeout=None)
    except (FileNotFoundError, OSError):
        return None
    try:
        data = json.loads(Path(answer_file).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    finally:
        Path(answer_file).unlink(missing_ok=True)
    return data


def _handle_question(q: dict) -> None:
    window = _operator_current_window()
    answer = _render_popup(window, q["question"] or "", q["options"])
    if answer is None:
        return  # tmux/popup failed — leave the ❓ signal standing, no crash
    body = json.dumps(answer)
    subprocess.run(
        [sys.executable, _BUS_PY, "send", "--from", BROKER_SENDER,
         "--to", q["asker"], "--in-reply-to", q["question_id"], "--body", body],
        capture_output=True, text=True,
    )


def watch(poll_interval: float = DEFAULT_POLL_SECONDS,
          idle_seconds: float = DEFAULT_IDLE_SECONDS) -> None:
    seen_ids: set[str] = set()
    pending: list[dict] = []
    while True:
        roots = sidebar_model.iter_bus_roots()
        for q in pending_questions(roots, seen_ids):
            seen_ids.add(q["question_id"])
            pending.append(q)
        if pending:
            now = time.time()
            busy = is_operator_busy(now, _last_submit_ts(), _last_client_activity_ts(),
                                     idle_seconds)
            if not busy:
                _handle_question(pending.pop(0))
        time.sleep(poll_interval)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    w = sub.add_parser("watch", help="run the long-lived broker loop")
    w.add_argument("--poll-interval", type=float, default=DEFAULT_POLL_SECONDS)
    w.add_argument("--idle-seconds", type=float, default=DEFAULT_IDLE_SECONDS)

    r = sub.add_parser("_popup-read", help=argparse.SUPPRESS)  # internal, run by the popup itself
    r.add_argument("--question", required=True)
    r.add_argument("--option", dest="option", action="append", required=True)
    r.add_argument("--answer-file", required=True)

    args = p.parse_args()
    if args.cmd == "watch":
        watch(args.poll_interval, args.idle_seconds)
    elif args.cmd == "_popup-read":
        _popup_read_main(args.question, args.option, args.answer_file)


if __name__ == "__main__":
    main()
