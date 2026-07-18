- created: 2026-07-18
- created_by: fable-5
- created_during: f/the-works-channel

## Blockers
- Operator decision: where orchids should be published (GitHub remote), and auth.

## Questions
- Which origin URL should this repo push to? Agent-installation.md references
  https://github.com/serialseb/orchids — remote is not configured locally.

## Findings
- Both closes on 2026-07-18 completed locally but the mandatory push failed:
  "fatal: 'origin' does not appear to be a git repository". Commits, archive/
  tags, and notes await a remote.

## Proposal
Configure the origin remote, then push main + archive/* tags + refs/notes/commits.

## Testing
`git push origin main --follow-tags` succeeds; `git ls-remote` shows the tags.
