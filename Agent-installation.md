# orchids — agent install instructions
# Operators bootstrap any project by telling their agent: "install kauk/orchids".
#
# You are an AI coding agent. The operator asked you to install orchids (the shared
# skills/agents/rule-files package) into the current project, using kauk (the package
# manager). Follow these steps exactly; do not infer alternatives. If a step fails or
# a situation is not covered, STOP and report — do not improvise.

1. PRECONDITIONS
   - You are inside a git repository (`git rev-parse --show-toplevel`). If not, STOP.
   - Managed paths (.claude/skills, .claude/agents, .claude/hooks, .claude/tools,
     .claude/settings.json, AGENTS.shared.md, AGENTS.files.md) have no uncommitted
     REAL files. If they do, commit them first — the migration preserves local
     variants via git history.

2. VENDOR THE TOOL (kauk)
   mkdir -p .ai/repositories/serialseb
   git clone https://github.com/serialseb/kauk .ai/repositories/serialseb/kauk
   (If the clone already exists, skip. On this operator's Pi, the local canonical is
   /home/sudoku/src/serialseb/kauk — prefer it when present.)

3. RUN INIT
   .ai/repositories/serialseb/kauk/bin/kauk init
   This writes .ai.toml (sources tables + delivery config), gitignores
   .ai/repositories/, and lays kauk's own package (the `kauk` skill).

4. INSTALL THE ORCHIDS PACKAGE
   .ai/repositories/serialseb/kauk/bin/kauk install serialseb/orchids <origin>
   where <origin> is https://github.com/serialseb/orchids — on this operator's Pi,
   prefer /home/sudoku/src/serialseb/orchids when present. This clones the package,
   migrates existing files (byte-identical → symlink; project-only skills → adopted
   upstream; diverged → preserved in git history), lays absolute symlinks per the
   package manifest, prefixes CLAUDE.md, and creates AGENTS.md if missing.

5. IF INSTALL REPORTS "MERGE REQUIRED"
   For each listed file:
   - Read the local variant:  git show HEAD:<path>
   - Read the package file at <path> (it is now a symlink; your Edit/Write tools
     follow symlinks — you CAN write through it).
   - Intelligently merge: union of rules, reconciled prose, nothing local lost,
     nothing canonical dropped. Write the result through the symlink.
   Then run:  .ai/repositories/serialseb/kauk/bin/kauk sync

6. COMMIT
   Stage ONLY: .gitignore .ai.toml CLAUDE.md AGENTS.shared.md AGENTS.files.md
   .claude/skills .claude/agents .claude/hooks .claude/tools .claude/settings.json
   Never sweep in unrelated changes. Commit message: one line on the migration.

7. RULES THAT BIND YOU FROM NOW ON
   - Read AGENTS.shared.md and AGENTS.md before any other action, every session.
   - AGENTS.md and CLAUDE.md content are project-owned; packages never overwrite them.
   - Skill delivery is tuned in .ai.toml ([dev]/[infra]/[org]/["*"] sections,
     skillname = "exclude"|"copy"|"link"|"local"); do not hand-edit beyond that.
   - Workstream logs / MOOD.md live in $(git rev-parse --git-common-dir)/the-works/ — uncommittable
     by construction; sensitive content never enters git history.
   - Run `kauk sync` at workflow start and end (`kauk` skill).

8. REPORT
   Tell the operator: links laid, skills adopted, files merged, and show
   `kauk sync --status`.
