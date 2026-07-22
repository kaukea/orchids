- created: 2026-07-22
- created_by: gh-ingest
- created_during: interactive

## Blockers
- None known yet.

## Questions
- Ingested from GitHub issue #123 — needs triage: type, component,
  urgency, scope.

## Findings
- Filed on GitHub (https://github.com/kaukea/orchids/issues/123); original body preserved below.

#tags #labels #github #board #vocabulary #urgency #area #emoji

Operator rulings (2026-07-21), settling [[tags-and-labels]]:

- Board tags and GitHub labels are ONE system: the vocabulary lives in
  AGENTS.files.md §TODO (single source), `board_gh.py` mirrors it, and every
  issue's label set is REPLACED from its board line at each push. Projection-only:
  the board stays canonical; label edits on GitHub are overwritten.
- Labels are emoji-FIRST, always ("⚙️ area/process", never "area/⚙️ process").
- Urgency simplified: `urgent` is KILLED — it is never urgent until it is
  critical; `low` renamed `nice-to-have` — closer to reality. Enum:
  critical · nice-to-have · idea (empty = normal). Former urgent lines demoted to
  normal; the operator re-raises individually.
- `component` renamed `area` everywhere; labels carry the `area/` prefix.
- Locality tags: ☁️ cloud (reporting — it WAS built in the cloud), 🛰️ analyzable
  (CAN go to the cloud), 🛋️ house-bound (local-only from inception).
- Progress labels derived, not stored: 📋 todo · 🚧 doing (stage=working) ·
  ✅ done (done|functional); ⛔ blocked derived from unresolved ⊘ edges.
- Multi-part features are a PARENT with sub-todos, one area per leaf; parent
  issues link their children ([[rules-tuning]] is the worked example).
