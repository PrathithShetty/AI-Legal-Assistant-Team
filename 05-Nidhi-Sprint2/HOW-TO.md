# Nidhi - Sprint 2 (26-30 Oct)

Branch: `feature/case-guidance`  ·  Merge order this sprint: **1 of 4** (Nidhi → Niharika → Prathith → Prarthana)

**You go first this sprint.** Raise your PR early so the others can start after it is merged.

## Your backlog items in this pull request

| Issue | ID | Item | Points |
|---|---|---|---|
| #19 | FR-17 | Display available document templates | 2 |
| #20 | FR-18 | Explain purpose of each template | 1 |
| #21 | FR-19 | View or generate supported templates | 5 |

Also yours this sprint (not code in this package):

- #45 T-04 Record 2-minute Sprint 2 demo video and upload to repo
- #49 EX-03 Case progress tracking and document checklist

## Files in this package

- `legal_assistant/doc_templates.py`
- `legal_assistant/static/templates.js`
- `legal_assistant/templates/templates/detail.html`
- `legal_assistant/templates/templates/index.html`
- `tests/test_templates.py`

## Steps

Do this during the sprint week, on your own laptop and GitHub account.

1. **Get the repo** (first time only), then open a terminal in the repo folder:
   ```bash
   git clone https://github.com/PrathithShetty/AI-Legal-Assistant-Team.git
   cd AI-Legal-Assistant-Team
   ```
   Already cloned? Run `git checkout main` and `git pull` instead.
2. **Switch to your branch:**
   ```bash
   git checkout feature/case-guidance
   git pull origin main
   ```
3. **Copy everything inside this package's `files` folder into the repo folder**, keeping the folder structure (say yes to replace if asked).
4. **Install and run the tests** (all must pass):
   ```bash
   python -m pip install -r requirements.txt
   python -m pytest
   ```
   Optional: `python run.py` and open http://127.0.0.1:5000 to see your feature.
5. **Commit and push:**
   ```bash
   git add -A
   git commit -m "Sprint 2: FR-17, FR-18, FR-19"
   git push -u origin feature/case-guidance
   ```
6. **Open the pull request:** go to https://github.com/PrathithShetty/AI-Legal-Assistant-Team, click **Compare & pull request** (base: `main`). Paste this into the description:
   ```
   Closes #19
   Closes #20
   Closes #21
   ```
7. Wait for the green **build** check, then ask for a review. A teammate approves; Prathith merges.
8. On the project board, move your cards to **Done** after the merge (https://github.com/users/PrathithShetty/projects/1).
