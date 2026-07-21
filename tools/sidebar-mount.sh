#!/usr/bin/env bash
# Mount the orchid-sidebar renderer as a pinned left pane in a tmux window.
# Usage: sidebar-mount.sh [target-window]
#   target-window: tmux window id/name to mount into (default: current window)
# Idempotent: does nothing if the target window already has a pane titled
# 'orchid-sidebar'. Never errors a session launch — exits 0 even when tmux
# is unavailable or the split fails.
set -euo pipefail

if ! command -v tmux >/dev/null 2>&1 || [ -z "${TMUX:-}" ]; then
  echo "sidebar-mount: not inside tmux, skipping sidebar mount" >&2
  exit 0
fi

DIR="$(cd "$(dirname "$0")" && pwd)"
window="${1:-$(tmux display-message -p '#{window_id}')}"

if tmux list-panes -t "$window" -F '#{pane_title}' 2>/dev/null | grep -qx 'orchid-sidebar'; then
  exit 0
fi

if ! pane=$(tmux split-window -h -b -l '17%' -d -t "$window" -P -F '#{pane_id}' "python3 '$DIR/sidebar.py'"); then
  echo "sidebar-mount: split failed, skipping sidebar mount" >&2
  exit 0
fi
tmux select-pane -t "$pane" -T 'orchid-sidebar' 2>/dev/null || true

exit 0
