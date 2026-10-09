"""Create the GitHub backlog (labels, sprint milestones, issues, Project board) from backlog/backlog.json.

Usage:
    python scripts/create_backlog.py --dry-run   # show what would be created
    python scripts/create_backlog.py             # create everything

Needs the GitHub CLI logged in with the project scope:  gh auth login --scopes project
Safe to re-run: existing labels, milestones, issues, project and fields are reused.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GH = shutil.which("gh") or r"C:\Program Files\GitHub CLI\gh.exe"

TYPE_COLORS = {"Functional": "1d76db", "Non-Functional": "5319e7", "Task": "fbca04", "Extra": "e99695"}
NOT_IN_SRS = {"Task": " (task, not in SRS)", "Extra": " (extra feature, not in SRS - see DEVIATIONS.md)"}
PRIORITY_COLORS = {"High": "d93f0b", "Medium": "f9d0c4"}
AREA_COLOR = "c2e0c6"

DRY_RUN = False


def gh(*args, check=True, mutate=True):
    """Run a gh command and return stdout. Mutating commands are only printed in dry-run mode."""
    if DRY_RUN and mutate:
        print("  [dry-run] gh " + " ".join(a if " " not in a else repr(a) for a in args[:6]) + (" ..." if len(args) > 6 else ""))
        return ""
    result = subprocess.run([GH, *args], capture_output=True, text=True, encoding="utf-8")
    if check and result.returncode != 0:
        raise RuntimeError(f"gh {' '.join(args[:4])} failed:\n{result.stderr.strip()}")
    return result.stdout.strip() if result.returncode == 0 else None


def gh_json(*args):
    out = gh(*args, mutate=False, check=not DRY_RUN)
    return json.loads(out) if out else None


def issue_title(item):
    return f"[{item['id']}] {item['title']}"


def issue_body(item, data):
    member = data["team"][item["assignee"]]
    lines = [
        f"**User story:** {item['story']}",
        "",
        "### Acceptance criteria",
        *[f"- [ ] {c}" for c in item["criteria"]],
        "",
        "### Details",
        f"- **SRS reference:** {item['id']}" + NOT_IN_SRS.get(item["type"], ""),
        f"- **Type:** {item['type']}",
        f"- **Feature area:** {item['area']}",
        f"- **Priority:** {item['priority']}",
        f"- **Story points:** {item['points']}",
        f"- **Sprint:** {data['sprints'][item['sprint']]['title']}",
        f"- **Assignee:** {item['assignee']} ({member['role']})",
        "",
        f"_Raise a PR from `{member['branch']}` with `Closes #<this issue>` in the description._",
    ]
    return "\n".join(lines)


def ensure_labels(repo, items):
    print("Labels")
    labels = {}
    for t, c in TYPE_COLORS.items():
        labels[t.lower()] = (c, f"{t} requirement/task")
    for p, c in PRIORITY_COLORS.items():
        labels[f"priority: {p.lower()}"] = (c, f"{p} priority (from SRS)")
    for area in sorted({i["area"] for i in items}):
        labels[f"area: {area}"] = (AREA_COLOR, f"Feature area: {area}")
    for name, (color, desc) in labels.items():
        gh("label", "create", name, "--repo", repo, "--color", color, "--description", desc, "--force")
        print(f"  {name}")


def item_labels(item):
    return [item["type"].lower(), f"priority: {item['priority'].lower()}", f"area: {item['area']}"]


def ensure_milestones(repo, sprints):
    print("Milestones")
    existing = {m["title"] for m in (gh_json("api", f"repos/{repo}/milestones?state=all&per_page=100") or [])}
    for s in sprints.values():
        if s["title"] in existing:
            print(f"  exists: {s['title']}")
            continue
        gh("api", f"repos/{repo}/milestones", "-X", "POST",
           "-f", f"title={s['title']}", "-f", f"due_on={s['due']}T23:59:59Z")
        print(f"  created: {s['title']}")


def ensure_issues(repo, data):
    print("Issues")
    existing = {i["title"]: i["url"] for i in (gh_json("issue", "list", "--repo", repo, "--state", "all",
                                                         "--limit", "500", "--json", "title,url") or [])}
    urls = {}
    for item in data["items"]:
        title = issue_title(item)
        if title in existing:
            urls[item["id"]] = existing[title]
            print(f"  exists: {title}")
            continue
        user = data["team"][item["assignee"]]["github"]
        base = ["issue", "create", "--repo", repo, "--title", title, "--body", issue_body(item, data),
                "--milestone", data["sprints"][item["sprint"]]["title"]]
        for label in item_labels(item):
            base += ["--label", label]
        url = gh(*base, "--assignee", user, check=False)
        if url is None:
            # Assignee must be a collaborator on the repo; create unassigned rather than fail.
            url = gh(*base)
            print(f"  WARNING: could not assign {user} (add them as a collaborator, then assign manually)")
        urls[item["id"]] = url
        print(f"  created: {title} -> {url or '(dry-run)'}")
    return urls


def ensure_project(org, repo, title):
    print("Project")
    projects = (gh_json("project", "list", "--owner", org, "--format", "json", "--limit", "100") or {}).get("projects", [])
    match = next((p for p in projects if p["title"] == title), None)
    if match:
        number = match["number"]
        print(f"  exists: #{number} {title}")
    else:
        out = gh("project", "create", "--owner", org, "--title", title, "--format", "json")
        number = json.loads(out)["number"] if out else 0
        print(f"  created: #{number} {title}")
    gh("project", "link", str(number), "--owner", org, "--repo", repo, check=False)
    print(f"  linked to {repo}")
    return number


def ensure_fields(org, number, data):
    print("Project fields")
    wanted = {
        "Story Points": ("NUMBER", None),
        "Sprint": ("SINGLE_SELECT", [s["title"] for s in data["sprints"].values()]),
        "Priority": ("SINGLE_SELECT", ["High", "Medium"]),
        "SRS ID": ("TEXT", None),
    }
    fields = (gh_json("project", "field-list", str(number), "--owner", org, "--format", "json", "--limit", "100")
              or {}).get("fields", [])
    names = {f["name"] for f in fields}
    for name, (dtype, options) in wanted.items():
        if name in names:
            print(f"  exists: {name}")
            continue
        args = ["project", "field-create", str(number), "--owner", org, "--name", name, "--data-type", dtype]
        if options:
            args += ["--single-select-options", ",".join(options)]
        gh(*args)
        print(f"  created: {name}")
    fields = (gh_json("project", "field-list", str(number), "--owner", org, "--format", "json", "--limit", "100")
              or {}).get("fields", [])
    return {f["name"]: f for f in fields}


def add_items(org, number, urls, fields, data):
    print("Project items")
    project_id = (gh_json("project", "view", str(number), "--owner", org, "--format", "json") or {}).get("id")

    def option_id(field, value):
        return next(o["id"] for o in fields[field]["options"] if o["name"] == value)

    for item in data["items"]:
        url = urls.get(item["id"])
        if not url:
            continue
        out = gh("project", "item-add", str(number), "--owner", org, "--url", url, "--format", "json")
        if not out:
            continue
        item_id = json.loads(out)["id"]
        common = ["project", "item-edit", "--id", item_id, "--project-id", project_id]
        gh(*common, "--field-id", fields["Story Points"]["id"], "--number", str(item["points"]))
        gh(*common, "--field-id", fields["Sprint"]["id"],
           "--single-select-option-id", option_id("Sprint", data["sprints"][item["sprint"]]["title"]))
        gh(*common, "--field-id", fields["Priority"]["id"],
           "--single-select-option-id", option_id("Priority", item["priority"]))
        gh(*common, "--field-id", fields["SRS ID"]["id"], "--text", item["id"])
        print(f"  {item['id']}: {item['points']} pts, {item['sprint']}")


def main():
    global DRY_RUN
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dry-run", action="store_true", help="print actions without changing GitHub")
    parser.add_argument("--backlog", default=str(ROOT / "backlog" / "backlog.json"))
    args = parser.parse_args()
    DRY_RUN = args.dry_run

    data = json.loads(Path(args.backlog).read_text(encoding="utf-8"))
    repo = data["repo"]
    org = repo.split("/")[0]

    if not os.path.exists(GH):
        sys.exit("GitHub CLI not found. Install it with: winget install GitHub.cli")
    if not DRY_RUN and gh("auth", "status", check=False, mutate=False) is None:
        sys.exit("Not logged in. Run: gh auth login --scopes project")

    ensure_labels(repo, data["items"])
    ensure_milestones(repo, data["sprints"])
    urls = ensure_issues(repo, data)
    number = ensure_project(org, repo, data["project_title"])
    if DRY_RUN:
        print(f"Project fields / items: would add {len(data['items'])} issues with Story Points, Sprint, Priority, SRS ID")
        return
    fields = ensure_fields(org, number, data)
    add_items(org, number, urls, fields, data)
    url = (gh_json("project", "view", str(number), "--owner", org, "--format", "json") or {}).get("url")
    print(f"\nDone. Open: {url}")


if __name__ == "__main__":
    main()
