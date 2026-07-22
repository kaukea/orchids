#!/usr/bin/env bash
# UserPromptSubmit hook — sidebar-polish item 12e: stamps "the operator just
# submitted" so tools/orchard-question-broker.py's deferral check
# (is_operator_busy) knows a previously in-flight message has now been SENT,
# and it is safe to pop a queued question. Structural only — renders
# nothing, asks nothing of the model; additive alongside this repo's other
# UserPromptSubmit hooks (handover/migration reminders).
set -eu

gcd="$(git rev-parse --git-common-dir 2>/dev/null)" || exit 0
dir="$gcd/the-works/broker"
mkdir -p "$dir" 2>/dev/null || exit 0
tmp="$dir/.last-submit-ts.$$"
date +%s.%N > "$tmp" 2>/dev/null && mv "$tmp" "$dir/last-submit-ts" || rm -f "$tmp" 2>/dev/null
exit 0
