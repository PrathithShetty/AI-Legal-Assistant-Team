"""Generate backlog/backlog.csv and backlog/SPRINT_PLAN.md from backlog/backlog.json."""
import csv
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BACKLOG = ROOT / "backlog"

data = json.loads((BACKLOG / "backlog.json").read_text(encoding="utf-8"))
items, team, sprints = data["items"], data["team"], data["sprints"]

with open(BACKLOG / "backlog.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["ID", "Title", "Type", "Feature Area", "Priority", "Story Points", "Sprint", "Assignee", "GitHub",
                "User Story", "Acceptance Criteria"])
    for i in items:
        w.writerow([i["id"], i["title"], i["type"], i["area"], i["priority"], i["points"], sprints[i["sprint"]]["title"],
                    i["assignee"], team[i["assignee"]]["github"], i["story"], "; ".join(i["criteria"])])

load = defaultdict(lambda: defaultdict(int))
for i in items:
    load[i["sprint"]][i["assignee"]] += i["points"]

md = [
    "# Sprint Plan - AI-Based Legal Assistant, e-Lawyer and Case Guidance System",
    "",
    "Project ID 28 | UE24CS341A Software Engineering | Repo: "
    f"[{data['repo']}](https://github.com/{data['repo']})",
    "",
    "## Team",
    "",
    "| Member | SRN | GitHub |",
    "|---|---|---|",
    *[f"| {n} | {t['srn']} | [@{t['github']}](https://github.com/{t['github']}) |" for n, t in team.items()],
    "",
    "## Estimation",
    "",
    "Story points use the Fibonacci scale (1, 2, 3, 5, 8): 1 = trivial UI/text change, 2-3 = small feature with "
    "validation and tests, 5 = feature with backend + frontend + data, 8 = feature with external integration "
    "(LLM service). Each FR and NFR from the SRS is one backlog item; BR-01 to BR-05 are folded into the "
    "acceptance criteria of the related items (FR-04, FR-07, FR-09, NFR-04).",
    "",
    "## Points per member",
    "",
    "| Member | " + " | ".join(sprints) + " | Total |",
    "|---|" + "---|" * (len(sprints) + 1),
]
for name in team:
    row = [load[s][name] for s in sprints]
    md.append(f"| {name} | " + " | ".join(str(x) for x in row) + f" | {sum(row)} |")
totals = [sum(load[s].values()) for s in sprints]
md.append("| **Total** | " + " | ".join(f"**{t}**" for t in totals) + f" | **{sum(totals)}** |")

for key, s in sprints.items():
    sprint_items = [i for i in items if i["sprint"] == key]
    md += ["", f"## {s['title']}", "", f"Due: {s['due']} | {sum(i['points'] for i in sprint_items)} points", "",
           "| ID | Title | Area | Priority | Pts | Assignee |", "|---|---|---|---|---|---|"]
    for i in sorted(sprint_items, key=lambda i: (i["assignee"], i["id"])):
        md.append(f"| {i['id']} | {i['title']} | {i['area']} | {i['priority']} | {i['points']} | {i['assignee']} |")

md += [
    "",
    "## Sprint goals",
    "",
    "- **Sprint 0 (dry run):** repo skeleton, CI, branch protection; every member raises one practice PR.",
    "- **Sprint 1:** working core product - register/login, ask a legal question, get a structured AI answer with "
    "category, procedure steps, lawyer recommendation and disclaimer. Deliverable: 1-minute demo video.",
    "- **Sprint 2:** legal references, document templates, query history, feedback and admin dashboard; performance, "
    "security and quality NFRs; final documentation and deviation log. Deliverable: 2-minute demo video, "
    "development frozen.",
    "",
    "## Workflow",
    "",
    "1. Pick your issue on the board and move it to **In Progress**.",
    "2. Create a branch: `git checkout -b <srs-id>-short-name` (e.g. `fr-07-ai-response`).",
    "3. Commit and push, then open a PR with `Closes #<issue number>` in the description. The assignee raises the PR.",
    "4. CI (`build` check) must pass and the repo owner reviews and merges the PR.",
    "5. Merging closes the issue and moves the card to **Done**.",
    "6. Any change from the submitted SRS/SAD/Test Plan goes in `DEVIATIONS.md`.",
]
(BACKLOG / "SPRINT_PLAN.md").write_text("\n".join(md) + "\n", encoding="utf-8")
print("Wrote backlog/backlog.csv and backlog/SPRINT_PLAN.md")
for s in sprints:
    print(s, dict(load[s]), "total", sum(load[s].values()))
