- created: 2026-07-19
- created_by: fable-5
- created_during: f/status-channel

## Blockers

- Depends on the repo-scoped bus landing first ([[status-channel]]) — Orchard extends it,
  it does not replace it.

## Questions

- Is the cross-repo hop live (a bus that spans repos) or a relay between two repo-scoped
  buses? The latter keeps each repo's bus unchanged and confines the new part to the hop.
- Addressing across repos: an agent ID is unique within a repository, so a cross-repo
  address needs the repo as a qualifier. What is the canonical repo identifier?
- Broadcast semantics across repos — does a broadcast stop at the repo boundary? (Almost
  certainly yes; crossing it by default would be surprising.)

## Findings

- Messaging is REPO-SCOPED by design: agents, orchestrators and third-party local agents
  are all scoped by repository, so the bus is too ([[status-channel]]).
- Distinct from [[cross-repo-inbox]]: that is the OFFLINE, durable delivery of requirements
  and knowledge between projects. Orchard is the LIVE messaging path. Same boundary, two
  different mechanisms — do not merge them (operator).
- Motivating instance: on 2026-07-19 work was discovered in seb.tv that belonged to orchids,
  with no channel to deliver it — so it was edited into a vendored clone and pushed straight
  to main, bypassing the workflow. The wrong path was the only path.

## Proposal

Codename **Orchard**: extend agent messaging across repository boundaries. Scope to be set
once the repo-scoped bus is proven in use.

## Testing

To agree when the task is groomed — expected shape: an agent in one repository addresses an
agent in another and the message is delivered, with broadcast still confined to its own repo.
