#!/usr/bin/env python3
"""Two-way sync between a repo's board (docs/TODO.md + sidecars) and GitHub.

Files are canonical. `push` projects active tasks as issues (gh# written back
onto the badge) and as rows of the user-level Project; `pull` ingests
GitHub-born changes (new issues -> sidecar stubs + board lines, issues closed
on GitHub -> board status) before files rule again.

Usage:
  board_gh.py push [--repo-root PATH] [--no-project]
  board_gh.py pull [--repo-root PATH]

Requires: gh CLI authenticated; the `project` scope for Project operations.
"""

import argparse
import json
import re
import subprocess
from datetime import date
from pathlib import Path

PROJECT_TITLE = "Orchidarium"
PROJECT_OWNER = "serialseb"
ACTIVE = {"todo", "doing", "blocked", "paused"}
CLOSED = {"done", "functional", "cancelled"}
LINE_RE = re.compile(
    r"^- `(?P<badge>[^`]*)` \[(?P<title>.+?)\]"
    r"\((?P<path>TODO\.md\.d/[\w-]+\.md)\)(?P<edges>.*)$"
)


def sh(*args, check=True):
    r = subprocess.run(args, capture_output=True, text=True)
    if check and r.returncode != 0:
        raise RuntimeError(f"{' '.join(args)}: {r.stderr.strip()}")
    return r.stdout


def gh_json(*args):
    out = sh("gh", *args)
    return json.loads(out) if out.strip() else None


class Task:
    def __init__(self, idx: int, m: re.Match):
        self.idx, self.title, self.path, self.edges = \
            idx, m["title"], m["path"], m["edges"]
        parts = [p.strip() for p in m["badge"].split("·")]
        parts += [""] * (6 - len(parts))
        (self.type, self.status, self.urgency,
         self.readiness, self.component, gh) = parts[:6]
        self.gh = int(gh[3:]) if gh.startswith("gh#") else None

    def line(self) -> str:
        gh = f"gh#{self.gh}" if self.gh else ""
        badge = " · ".join([self.type, self.status, self.urgency,
                            self.readiness, self.component, gh])
        badge = re.sub("  +", " ", badge).rstrip()
        return f"- `{badge}` [{self.title}]({self.path}){self.edges}"


class Board:
    def __init__(self, root: Path):
        self.root = root
        self.todo = root / "docs" / "TODO.md"
        self.lines = self.todo.read_text().splitlines()
        self.repo = self._detect_repo()

    def _detect_repo(self):
        url = sh("git", "-C", str(self.root), "remote", "get-url", "origin").strip()
        m = re.search(r"github\.com[:/]([^/]+/[^/.]+)", url)
        if not m:
            raise RuntimeError(f"cannot derive owner/repo from origin '{url}'")
        return m.group(1)

    def tasks(self):
        out = []
        for i, line in enumerate(self.lines):
            m = LINE_RE.match(line)
            if m:
                out.append(Task(i, m))
        return out

    def write(self, task: Task):
        self.lines[task.idx] = task.line()

    def append_line(self, line: str):
        while self.lines and not self.lines[-1].strip():
            self.lines.pop()
        self.lines.append(line)

    def save(self):
        self.todo.write_text("\n".join(self.lines) + "\n")


def sidecar_questions(root: Path, rel: str) -> str:
    p = root / "docs" / rel
    if not p.exists():
        return ""
    m = re.search(r"## Questions\n(.*?)(?=\n## |\Z)", p.read_text(), re.S)
    return m.group(1).strip() if m else ""


def issue_body(board: Board, t: Task) -> str:
    lines = [
        f"`{t.type} · {t.status} · {t.urgency or '—'} · "
        f"{t.readiness} · {t.component or '—'}`",
        "",
        f"Source of truth: `docs/{t.path}` — this issue is a projection; "
        "edits here are ingested at the next sync, then the board rules.",
    ]
    q = sidecar_questions(board.root, t.path)
    if q and q.lower().strip("- .") not in {"none", "none known yet"}:
        lines += ["", "### Open questions", q]
    return "\n".join(lines)


def list_board_issues(repo: str, state="all"):
    return gh_json("issue", "list", "-R", repo, "--state", state,
                   "--label", "board", "--limit", "500",
                   "--json", "number,title,state,body,url") or []


def ensure_label(repo: str):
    subprocess.run(["gh", "label", "create", "board", "-R", repo,
                    "-c", "#6f42c1", "-d", "Projected from the file board"],
                   capture_output=True, text=True)


def push(board: Board, with_project: bool):
    ensure_label(board.repo)
    existing = {i["number"]: i for i in list_board_issues(board.repo)}
    created, updated, closed = 0, 0, 0
    for t in board.tasks():
        if t.status in ACTIVE and t.gh is None:
            out = sh("gh", "issue", "create", "-R", board.repo,
                     "--title", t.title, "--label", "board",
                     "--body", issue_body(board, t))
            t.gh = int(out.strip().rsplit("/", 1)[1])
            board.write(t)
            created += 1
        elif t.gh is not None and t.gh in existing:
            issue = existing[t.gh]
            if t.status in CLOSED and issue["state"] == "OPEN":
                sh("gh", "issue", "close", "-R", board.repo, str(t.gh),
                   "-c", f"Board: task reached `{t.status}`.")
                closed += 1
            elif t.status in ACTIVE:
                body = issue_body(board, t)
                if issue["body"] != body or issue["title"] != t.title:
                    sh("gh", "issue", "edit", "-R", board.repo, str(t.gh),
                       "--title", t.title, "--body", body)
                    updated += 1
                if issue["state"] != "OPEN":
                    sh("gh", "issue", "reopen", "-R", board.repo, str(t.gh))
    board.save()
    print(f"push {board.repo}: {created} created, {updated} updated, "
          f"{closed} closed")
    if with_project:
        project_sync(board)


# ---------- Projects v2 ----------

def gql(query: str, **vars):
    args = ["api", "graphql", "-f", f"query={query}"]
    for k, v in vars.items():
        args += ["-f", f"{k}={v}"]
    return gh_json(*args)


FIELDS_QUERY = """query($id:ID!){node(id:$id){... on ProjectV2{
  fields(first:50){nodes{... on ProjectV2FieldCommon{id name}
  ... on ProjectV2SingleSelectField{id name options{id name}}}}}}}"""

SELECT_FIELDS = {
    "Status": ["todo", "doing", "blocked", "paused", "functional",
               "done", "cancelled"],
    "Urgency": ["urgent", "high", "low", "idea"],
    "Readiness": ["queued", "working", "blocked-on-answers", "plan-ready",
                  "complete"],
}
TEXT_FIELDS = ["Component", "Repo"]


def ensure_project():
    data = gql("""query($login:String!){user(login:$login){
        projectsV2(first:50){nodes{id title number}}}}""", login=PROJECT_OWNER)
    for p in data["data"]["user"]["projectsV2"]["nodes"]:
        if p["title"] == PROJECT_TITLE:
            return p
    owner = gql("query($login:String!){user(login:$login){id}}",
                login=PROJECT_OWNER)["data"]["user"]["id"]
    made = gql("""mutation($owner:ID!,$title:String!){
        createProjectV2(input:{ownerId:$owner,title:$title}){
        projectV2{id title number}}}""", owner=owner, title=PROJECT_TITLE)
    return made["data"]["createProjectV2"]["projectV2"]


def ensure_fields(project_id: str):
    have = {f["name"] for f in
            gql(FIELDS_QUERY, id=project_id)["data"]["node"]["fields"]["nodes"]
            if f}
    for name, opts in SELECT_FIELDS.items():
        if name in have:
            continue
        opts_gql = ",".join(
            '{name:"%s",color:GRAY,description:""}' % o for o in opts)
        gql("""mutation($id:ID!){createProjectV2Field(input:{projectId:$id,
            dataType:SINGLE_SELECT,name:"%s",singleSelectOptions:[%s]})
            {clientMutationId}}""" % (name, opts_gql), id=project_id)
    for name in TEXT_FIELDS:
        if name not in have:
            gql("""mutation($id:ID!){createProjectV2Field(input:{projectId:$id,
                dataType:TEXT,name:"%s"}){clientMutationId}}""" % name,
                id=project_id)
    return {f["name"]: f for f in
            gql(FIELDS_QUERY, id=project_id)["data"]["node"]["fields"]["nodes"]
            if f}


def project_items(project_id: str):
    items, cursor = {}, None
    while True:
        data = gql("""query($id:ID!,$after:String){node(id:$id){
            ... on ProjectV2{items(first:100,after:$after){
            pageInfo{hasNextPage endCursor}
            nodes{id content{... on Issue{url}}}}}}}""",
            id=project_id, after=cursor or "")
        page = data["data"]["node"]["items"]
        for n in page["nodes"]:
            if n["content"]:
                items[n["content"]["url"]] = n["id"]
        if not page["pageInfo"]["hasNextPage"]:
            return items
        cursor = page["pageInfo"]["endCursor"]


def set_field(project_id, item_id, field, value):
    if "options" in field:
        opt = next((o["id"] for o in field["options"]
                    if o["name"] == value), None)
        if not opt:
            return
        val = '{singleSelectOptionId:"%s"}' % opt
    else:
        val = '{text:"%s"}' % value
    gql("""mutation($p:ID!,$i:ID!,$f:ID!){updateProjectV2ItemFieldValue(
        input:{projectId:$p,itemId:$i,fieldId:$f,value:%s})
        {clientMutationId}}""" % val,
        p=project_id, i=item_id, f=field["id"])


def project_sync(board: Board):
    project = ensure_project()
    fields = ensure_fields(project["id"])
    items = project_items(project["id"])
    issues = {i["number"]: i for i in list_board_issues(board.repo)}
    n = 0
    for t in board.tasks():
        if t.gh is None or t.status not in ACTIVE or t.gh not in issues:
            continue
        url = issues[t.gh]["url"]
        item_id = items.get(url)
        if not item_id:
            node = gql("query($u:URI!){resource(url:$u){... on Issue{id}}}",
                       u=url)["data"]["resource"]["id"]
            item_id = gql("""mutation($p:ID!,$c:ID!){addProjectV2ItemById(
                input:{projectId:$p,contentId:$c}){item{id}}}""",
                p=project["id"], c=node
                )["data"]["addProjectV2ItemById"]["item"]["id"]
        set_field(project["id"], item_id, fields["Status"], t.status)
        if t.urgency:
            set_field(project["id"], item_id, fields["Urgency"], t.urgency)
        stage = t.readiness.split("/")[0]
        if stage:
            set_field(project["id"], item_id, fields["Readiness"], stage)
        if t.component:
            set_field(project["id"], item_id, fields["Component"], t.component)
        set_field(project["id"], item_id, fields["Repo"], board.repo)
        n += 1
    print(f"project {PROJECT_TITLE}: {n} rows ensured for {board.repo}")


# ---------- pull ----------

STUB = """- created: {today}
- created_by: gh-ingest
- created_during: interactive

## Blockers
- None known yet.

## Questions
- Ingested from GitHub issue #{num} — needs triage: type, component,
  urgency, scope.

## Findings
- Filed on GitHub ({url}); original body preserved below.

{body}
"""


def slugify(title: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return s[:48] or "gh-task"


def pull(board: Board):
    tasks = board.tasks()
    by_gh = {t.gh: t for t in tasks if t.gh is not None}
    closed_from_gh, ingested = 0, 0
    for issue in list_board_issues(board.repo):
        t = by_gh.get(issue["number"])
        if t and t.status in ACTIVE and issue["state"] != "OPEN":
            t.status = "done"
            board.write(t)
            closed_from_gh += 1
    all_open = gh_json("issue", "list", "-R", board.repo, "--state", "open",
                       "--limit", "500",
                       "--json", "number,title,body,url,labels") or []
    for issue in all_open:
        if issue["number"] in by_gh:
            continue
        # already board-labelled but unknown here = a projection in flight
        # (gh# commit not yet visible to this checkout) — never re-ingest
        if any(l["name"] == "board" for l in issue["labels"]):
            continue
        slug = slugify(issue["title"])
        sidecar = board.root / "docs" / "TODO.md.d" / f"{slug}.md"
        if sidecar.exists():
            slug = f"{slug}-gh{issue['number']}"
            sidecar = board.root / "docs" / "TODO.md.d" / f"{slug}.md"
        sidecar.write_text(STUB.format(
            today=date.today().isoformat(), num=issue["number"],
            url=issue["url"], body=issue["body"] or "(no body)"))
        board.append_line(
            f"- `feature · todo · · queued · · gh#{issue['number']}` "
            f"[{issue['title']}](TODO.md.d/{slug}.md)")
        ensure_label(board.repo)
        sh("gh", "issue", "edit", "-R", board.repo, str(issue["number"]),
           "--add-label", "board")
        ingested += 1
    board.save()
    print(f"pull {board.repo}: {ingested} ingested, "
          f"{closed_from_gh} closed-from-GitHub")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("verb", choices=["push", "pull"])
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--no-project", action="store_true")
    a = ap.parse_args()
    board = Board(Path(a.repo_root).resolve())
    if a.verb == "push":
        push(board, with_project=not a.no_project)
    else:
        pull(board)


if __name__ == "__main__":
    main()
