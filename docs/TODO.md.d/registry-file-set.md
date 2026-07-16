- created: 2026-07-12
- created_by: fable-5

## Blockers
- none

## Questions
- none

## Findings
- readme-sync trigger has fired (user-facing tool exists); no README/ARCHITECTURE/
  CHANGELOG/decisions in orchids yet; session rulings live only in chat + git log.
- Operator ruling (2026-07-16): README is mandatory and contains the WHY and the
  WHAT only; the HOW goes in ARCHITECTURE.md.
- Operator ruling (2026-07-16): owin.org was NEVER in the plans — it was invented
  by an agent session (commits f426a02/56bba34, 2026-07-12). install.txt header
  fixed; CNAME + index.html remain for the operator to delete.
- 2026-07-16: README.md and ARCHITECTURE.md written (why/what vs how split).
  Still missing: CHANGELOG, docs/decisions.md.
- Operator (2026-07-16): the GitHub `kauk` username/org is not yet available;
  waiting on it for the canonical repo list. Until then the interim homes are
  `serialseb/kauk` and `serialseb/orchids` — the explicit URLs in README.md,
  ARCHITECTURE.md, and Agent-installation.md are deliberate placeholders to
  swap when the `kauk/*` namespace lands.
- Operator (2026-07-16): the bootstrap contract is "install kauk/orchids" →
  the agent resolves the repo on GitHub and reads `Agent-installation.md`
  (where to go, what to install). install.txt renamed accordingly.

## Proposal
Write the registry set: README (why + what only), ARCHITECTURE (the how, one page),
docs/decisions.md seeded with session rulings (.git-channel handover, .ai.toml
modes, fixed roles), CHANGELOG.

## Testing
readme-sync checklist passes; decisions greppable by #keyword.
