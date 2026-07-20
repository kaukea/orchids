- created: 2026-07-20
- created_by: gh-ingest
- created_during: interactive

## Blockers
- None known yet.

## Questions
- Ingested from GitHub issue #23 — needs triage: type, component,
  urgency, scope.

## Findings
- Filed on GitHub (https://github.com/kaukea/orchids/issues/23); original body preserved below.

Needs:
 - See what repositories and tasks are being worked on
 - Navigate directly to a task by keyboard navigation
 - Distinguish agents waiting on the operator, working, done and closed
 - Usage of emoji and animated / full colors welcome

Example:
🗃️ **Orchids**
 |- <status> Task Navigator
 |  |- 🤖 Orchestrsating (or e.g. Architecting)
 |  |  |- (4 subbuilders) 

Behaviour
Each tmux has a series of repositories in which work is being done. That work gets split in features (Task Navigator showhn here, there may be multiple at the same time). 
This represents the whole of that work. Focusing on the pane allows navigating with the keyboard up and down, and switches to the sessioon for the repo, to the window for the featrue, to the pane for the actibity (So an Orchestrator may have different activities).
When a question is asked or a task is blocked by tge operator, the enttry requiring an answer flashes
Status is one of the following for which you will find an emoji: Waiting on user, Running (actively doing something), Standby (not closed just wiating after work has completed), Completed or Failed.

Implementation
 Agents broadcast their current activity by posting to the bus their current activity (Questioning, Anlayizing, Thinking, which gives the text. Subagents are only displayed by name as they get called and come back, to give the opereator a sense of what is going on.
For any session, left sidebar sized to 1/6th of the width  (to be refined based on actual usage), always visible by default, always showig the same content.
