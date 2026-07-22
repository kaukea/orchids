#!/usr/bin/env bash
# Notification hook — backstop for sidebar-polish item 12b: when the harness
# raises its OWN native notification/question (bypassing the bus ask/popup
# path in tools/orchard-question-broker.py), broadcast the same
# waiting-on-operator signal the sidebar already reads
# (tools/sidebar_model.py's last_notify_user, set by an `orchid:activity:`
# broadcast carrying notify_user) — mechanical, independent of whether the
# model remembers to do it itself. This hook renders nothing on its own; the
# sidebar's already-built ❓ render is what shows it.
set -eu

root="$(git rev-parse --show-toplevel 2>/dev/null)" || exit 0
for candidate in "$root/.claude/tools/bus.py" "$root/tools/bus.py"; do
  [ -f "$candidate" ] && bus="$candidate" && break
done
[ -n "${bus:-}" ] || exit 0

me="$(python3 "$bus" whoami 2>/dev/null)" || exit 0
python3 "$bus" broadcast --from "$me" \
  --body "orchid:activity:awaiting operator (native prompt)" --notify-user \
  >/dev/null 2>&1 || true
exit 0
