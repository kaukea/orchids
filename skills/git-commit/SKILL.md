---
name: git-commit
description: Use when committing files to git. It describes format and content to include in the commit messages that MUST be followed.
share: github
compatibility: Requires git
metadata:
  tags: [git, commit, gitmoji, plan, task]
---

# git commits (MUST)

## Checklist

- [ ] Tests run if any exist
- [ ] Format applied (see below)
- [ ] Subject ≤ 52 characters
- [ ] Body wrapped at 72 characters
- [ ] Trailers present (`Branch:`, `Co-authored-by:`)
- [ ] Scope rules followed

Commit one logical change at a time. The user may override any rule.

## Scope discipline (MUST)

- **Touch only what you modified.** External changes during a workflow (user edits, tool output, parallel processes) are not yours by default — do not stage, commit, revert, or delete them.
- **Related external changes:** inspect, pre-stage what looks related, ask once grouped, positive default: *"Include these N because <reason>?"*
- **Unrelated external changes:** ask once, combined: *"These N files look unrelated to this workflow — confirm? If so, once the merge commit has landed, should I commit them on main, open a new feature branch, or will you handle it yourself?"*
- **User edits to `.md` files** are committed separately from code changes.
- **Stage specific paths:** `git add <file>`, never `git add -A` / `git add .`.
- **Verify the current branch before staging.** `git branch --show-current` or read `git status`. If the workflow requires a feature branch and you're not on `f/…`, stop.
- **Surface merge conflicts; do not auto-resolve.** Show the conflicting hunks, propose a resolution, wait for confirmation.
- **Test results are not fabricated.** The `✅ x/y` (or 🚫) line reflects a run you actually performed in this session. If you didn't run tests, omit the line.
- **`main` is immutable:** no amend, no rebase, no rewrite. Tags and notes are SHA-anchored and would be lost.
- **Feature branches are mutable** for trivial fixups only (typo, prose, a missing semicolon). Larger changes get a new commit.
- **No destructive operations without explicit user consent:** `reset --hard`, `--force` / `--force-with-lease`, `--no-verify`, `branch -D <unmerged>`, `checkout -- <dirty>`, `push`, `rebase`, `cherry-pick`.

## Style

- `<subject>` describes the change in imperative form, e.g. "Encapsulate class X". Avoid generic opener verbs like "add".
- `<subject>` starts with a capital letter and never ends with punctuation.
- Both `<subject>` and the body explain the **WHY**, not the HOW. Keep technical detail short and only when necessary. No `HOW:` or other prefixes — the body is explanation only.

## Format

```
<gitmoji> <subject>

<test-emoji> x/y

<body>

Branch: <branch-name>
Co-authored-by: <model> <junie@serialseb.com>
```

- `<subject>` line ≤ 52 characters.
- `<model>` in `Co-authored-by:` is the LLM model name and version; the email address in brackets is fixed.
- `<gitmoji>` is the closest match in https://gitmoji.dev, in Unicode.
- `<test-emoji>` is ✅ (passed) or 🚫 (failed), followed by `<x>` succeeding and `<y>` total. If no tests were run, omit the line entirely.
- Body lines wrap at 72 characters.
- `Branch:` is required on every commit and is the current feature branch — never `main`, with one exception:
  an operator-accepted micro-task commit (`workflow` skill → Micro-task path) carries `Branch: main`.
