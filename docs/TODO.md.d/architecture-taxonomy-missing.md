- created: 2026-07-17
- created_by: opus-4.8

## Blockers
- Needs the operator: the vocabulary is a controlled list and `AGENTS.files.md` §TODO
  is explicit that "agents do not invent values". Cannot be ripened to done by an agent
  alone.

## Questions
- What are orchids' `functionality` → `component` pairs? De facto today, from the board:
  `Publication` → `publication`; `Process machinery` → `process`; `Future` → `sync`;
  `Role delivery` → `sync`, `process`. Ratify, rename, or replace?
- Should `board_lint.py` fail loudly when the Taxonomy table is absent, instead of
  silently loading an empty glossary and blaming every task? The current failure mode
  points at 13 innocent tasks rather than at the one missing table.

## Findings
- `ARCHITECTURE.md` has no `## Taxonomy` section. `board_lint.py:load_glossary()`
  parses one out of that heading; with it absent the glossary is empty, so every task's
  component is "not in <X> taxonomy". Board reports `13 tasks, 0 functionalities,
  13 errors` — it has never passed its own lint.
- `AGENTS.shared.md` states the taxonomy "lives in the project's ARCHITECTURE.md" and
  `AGENTS.files.md` lints `value ∈ glossary`. Both point at a table that was never
  written for this repo. The rule exists; the data does not.
- Pre-existing badge error, unrelated to the glossary: `self-install-link-collision`
  carries readiness stage `parked`, which is not in the enum
  (`queued|working|blocked-on-answers|plan-ready|complete`). `parked` was retired when
  stages replaced it. One-line fix, but it is a real board-data error.
- `tools/board_lint.py` only runs from its delivered path (`.claude/tools/`): `ROOT` is
  computed as three `dirname`s up from `__file__`, so running the source copy at
  `tools/board_lint.py` resolves ROOT to the parent of the repo and dies on a missing
  ARCHITECTURE.md. Worth knowing before anyone "fixes" the wrong thing.

## Proposal
1. Agree the `functionality` → `component` table with the operator.
2. Add `## Taxonomy` to `ARCHITECTURE.md`.
3. Correct `self-install-link-collision`'s stage.
4. Decide whether the lint should hard-fail on a missing table.

## Testing
`python3 .claude/tools/board_lint.py` exits 0 with 0 errors over the real board.
Deliberately introducing a bogus component still fails — the lint must not be made to
pass by weakening it.
