#!/usr/bin/env bash
# Stop hook. When the architect countersigns the operator's "THAT IS ALL" with a final
# "ALL IT IS", return the tmux client to the orchestrator pane (captured at spawn in
# .return-window) and close the architect's OWN pane. No-op for any other agent/message.
# Logs every invocation to /tmp/architect-close.log so a miss is diagnosable.
set -eu

log=/tmp/architect-close.log
ts=$(date '+%F %T' 2>/dev/null || echo '?')
say(){ printf '%s [close-hook] %s\n' "$ts" "$1" >> "$log" 2>/dev/null || true; }

input=$(cat)
tp=$(printf '%s' "$input" | jq -r '.transcript_path // empty' 2>/dev/null || true)
root=$(git rev-parse --show-toplevel 2>/dev/null || echo "$PWD")
rw="$root/.return-window"

[ -n "$tp" ] && [ -f "$tp" ] || { say "no transcript (tp='$tp')"; exit 0; }

# last NON-EMPTY assistant text — a trailing tool-only/empty turn after the countersign
# must not mask it (that was the recurring close-miss)
last=$(jq -rs 'map(select(.type=="assistant") | (.message.content // []) | map(select(.type=="text").text) | join("")) | map(select(. != "")) | last // ""' "$tp" 2>/dev/null || true)
last=$(printf '%s' "$last" | sed -e 's/[[:space:]]*$//' | awk 'NF{l=$0} END{print l}')
[ "$last" = "ALL IT IS" ] || { say "no match (last='$last')"; exit 0; }
[ -f "$rw" ] || { say "match but no .return-window at $rw"; exit 0; }

ret=$(sed -n 1p "$rw" 2>/dev/null || true)
sock=$(sed -n 2p "$rw" 2>/dev/null || true)
[ -n "$sock" ] || sock="${TMUX%%,*}"        # fall back to inherited $TMUX socket
tx(){ tmux -S "$sock" "$@"; }

# the architect's OWN pane — NOT the "current" pane, which may be elsewhere if the
# operator switched away
arch="${TMUX_PANE:-}"
arch_win=$(tx display-message -p -t "$arch" '#{window_id}' 2>/dev/null || true)
say "MATCH ret='$ret' sock='$sock' arch='$arch' arch_win='$arch_win'"

[ -n "$sock" ] || { say "no tmux socket — leaving pane for manual close"; exit 0; }

# Return target (line 1): a pane id `%N` (Decision-006) or a legacy window id `@N`.
case "$ret" in
  %*)
    ret_win=$(tx display-message -p -t "$ret" '#{window_id}' 2>/dev/null || true)
    tx switch-client -t "$ret" 2>/dev/null || true
    if [ -n "$ret_win" ]; then tx select-window -t "$ret_win" 2>/dev/null || true; fi
    tx select-pane -t "$ret" 2>/dev/null || say "return to pane $ret FAILED"
    ;;
  *)
    tx switch-client -t "$ret" 2>/dev/null || tx select-window -t "$ret" 2>/dev/null || say "return to $ret FAILED"
    ;;
esac

# SAFETY: never kill the return target — neither the orchestrator's pane nor (legacy
# window-id form) any pane of the orchestrator's window. Mis-fires return only.
if [ -z "$arch" ] || [ "$arch" = "$ret" ] || [ "$arch_win" = "$ret" ]; then
  say "arch='$arch'/'$arch_win' resolves to return target or empty — NOT killing"
  exit 0
fi
# Killing the last pane of a window kills the window, so kill-pane also covers the
# legacy window-per-architect layout.
tx kill-pane -t "$arch" 2>/dev/null || say "kill $arch FAILED"
exit 0
