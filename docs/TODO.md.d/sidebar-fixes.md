- created: 2026-07-21
- created_by: Sebastien Lambla
- created_during: fleet-sidebar

## Blockers

- fleet-sidebar's squash-merge not yet on `main` — fixes branch from the merged code.

## Questions

- Which defects, specifically? The operator observed numerous mistakes and issues during
  the close review but the list is not yet enumerated. Ripening should collect it: an
  operator walk-through of what they saw, plus a code audit of the delivered surfaces
  (`tools/sidebar_model.py`, `tools/sidebar.py`, `tools/sidebar_nav.py`,
  `tools/sidebar-mount.sh`, the activity-broadcast additions to the agent defs).

## Findings

- The feature was closed under operator waiver: the build's own unit tests (23/23) and
  smoke passed, but the operator's review judged the implementation to carry numerous
  mistakes and issues; the close was accepted with this corrective follow-up attached
  rather than amending in-branch.
- Known limitations already recorded by the build (candidates, not the full list):
  reader dedup is cross-scan by message id; a repolist entry with no bus activity
  renders an empty repo row.

## Proposal

Corrective only — make the delivered fleet sidebar meet its original spec
([[fleet-sidebar]] Proposal): audit the shipped implementation, enumerate the defects
(operator walk-through + code audit), fix them. No new capability, no scope growth;
anything additive discovered en route becomes its own task.

## Testing

Re-run the original agreed method with the operator's live visual pass front and
centre — flash animation, keyboard navigation landing on the right window, a row
updating when a job's window closes — since that live pass is where the issues
surfaced. Unit suite stays green.
