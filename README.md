# AI-Based Legal Assistant, e-Lawyer and Case Guidance System

Software Engineering Mini-Project (UE24CS341A), Project ID 28.

A web application that gives general legal information for common problems in India. You describe your problem in plain language and the app:

- identifies the legal area (consumer, property and tenancy, family, criminal, employment, cyber fraud, RTI)
- gives a plain-language summary and the usual step-by-step procedure
- lists relevant Acts and Supreme Court judgments from an approved list
- says clearly when you should consult a lawyer, and shows emergency helplines when needed
- provides fillable document templates (RTI application, consumer complaint, rent agreement, legal notice and more)
- saves the question history of registered users, collects feedback, and lets administrators manage all legal content

> This is a student project. It gives general information only and is **not legal advice**.

## Team

| Member | SRN | GitHub |
|---|---|---|
| Prathith Shetty | PES2UG24AM121 | [@PrathithShetty](https://github.com/PrathithShetty) |
| Niharika Mirle | PES2UG24AM105 | [@Niharika1704](https://github.com/Niharika1704) |
| Nidhi | PES2UG24AM102 | [@nidhibillava3103](https://github.com/nidhibillava3103) |
| Prarthana D Acharya | PES2UG24AM119 | [@prarthanaa11](https://github.com/prarthanaa11) |

## Tech stack

| Layer | Choice | Why |
|---|---|---|
| Backend | Python 3.12, Flask 3 | Simple, well known, one command to run |
| Database | SQLite | No setup needed; file-based |
| Frontend | Server-rendered HTML (Jinja), CSS, vanilla JavaScript | No build step; works on any modern browser |
| AI (optional) | Claude API (`claude-opus-5-5`) via the `anthropic` SDK | Writes the plain-language summary; the app works without it |
| Tests | pytest | Unit and integration tests per module, run in CI |
| CI | GitHub Actions | Runs tests on every push and pull request |
| Hosting | Render (free plan, HTTPS) | `render.yaml` included |

## Run it locally

You need Python 3.10 or newer.

```bash
git clone https://github.com/AI-Legal-Assistant-Team/AI-legal-assistant.git
cd AI-legal-assistant
python -m venv .venv
.venv\Scripts\activate          # Windows  (macOS/Linux: source .venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env          # Windows  (macOS/Linux: cp .env.example .env)
```

Open `.env` and set `SECRET_KEY`, `ADMIN_EMAIL` and `ADMIN_PASSWORD`. Then start the app:

```bash
python run.py
```

Open http://127.0.0.1:5000. The database is created and filled with the legal knowledge base on first start. Log in with your `ADMIN_EMAIL` and `ADMIN_PASSWORD` to see the **Admin** menu.

### AI summaries (optional)

Without an API key the app answers from its built-in, admin-approved knowledge base. To have Claude write the summary, put your key from https://console.anthropic.com in `.env` as `ANTHROPIC_API_KEY` and restart. If the AI is slow, unavailable or declines, the app automatically falls back to the knowledge base.

The AI only writes the summary paragraph. The category, steps and references always come from the approved database, so the app never shows an invented law or case.

## Run the tests

```bash
python -m pytest
```

Load test (with the app running): `python scripts/load_test.py --users 10 --requests 5`

## Project structure

```
legal_assistant/
  __init__.py        app factory, error handling, security hooks
  config.py          settings from environment variables
  db.py              SQLite connection, schema creation, seeding
  schema.sql         tables (SRS Appendix B field layouts)
  security.py        login/admin checks, CSRF, HTTPS, security headers
  auth.py            registration, login, logout               FR-01..04          Member 1
  account.py         user dashboard and profile                EX-02              Member 1
  history.py         My cases: saved queries, case status      FR-20, FR-21, EX-01  Member 1
  query.py           question API and structured response      FR-05..09, FR-11   Member 2
  ai.py              AI summary with knowledge-base fallback   FR-07, NFR-05      Member 2
  classifier.py      legal category classifier                 FR-10              Member 3
  guidance.py        steps, lawyer and emergency notices       FR-12, FR-13, NFR-06  Member 3
  references.py      legal references                          FR-14..16          Member 3
  doc_templates.py   document templates                        FR-17..19          Member 3
  feedback.py        feedback                                  FR-22              Member 4
  admin.py           admin dashboard                           FR-23..25          Member 4
  knowledge/         seed data: categories, references, templates
  templates/, static/  pages, CSS, JavaScript
tests/               pytest tests, one or more files per module
scripts/             backlog creation, load test
backlog/             sprint plan and backlog (from the SRS)
```

## Requirement traceability

| Requirement | Implemented in | Tested in |
|---|---|---|
| FR-01 to FR-04 | `auth.py`, `security.py` | `tests/test_auth.py`, `tests/test_admin.py` |
| FR-05 to FR-09, FR-11 | `query.py`, `ai.py`, `disclaimer.py` | `tests/test_query.py`, `tests/test_ai.py` |
| FR-10 | `classifier.py` | `tests/test_classifier.py` |
| FR-12, FR-13 | `guidance.py` | `tests/test_guidance.py` |
| FR-14 to FR-16 | `references.py` | `tests/test_references.py` |
| FR-17 to FR-19 | `doc_templates.py` | `tests/test_templates.py` |
| FR-20, FR-21, EX-01, EX-02 | `query.py`, `history.py`, `account.py` | `tests/test_cases.py` |
| FR-22 | `feedback.py` | `tests/test_feedback.py` |
| FR-23 to FR-25 | `admin.py` | `tests/test_admin.py` |
| NFR-01 to NFR-03 | response timing, threaded server, `scripts/load_test.py` | `tests/test_query.py`, load test |
| NFR-04 to NFR-06 | `disclaimer.py`, `ai.py` prompt rules, `guidance.py` | `tests/test_query.py`, `tests/test_guidance.py`, `tests/test_ai.py` |
| NFR-07 to NFR-11 | `security.py`, `auth.py`, `history.py` | `tests/test_app.py`, `tests/test_auth.py`, `tests/test_cases.py` |
| NFR-12 to NFR-16 | responsive UI, modules, error pages, pytest | whole test suite, manual browser check |

All test cases (69 cases across 17 types of testing, with results) are in [AI_Legal_Assistant_Test_Cases_16.xlsx](AI_Legal_Assistant_Test_Cases_16.xlsx).

## Deploy (HTTPS)

1. Push to GitHub and sign in to https://render.com.
2. Choose **New > Blueprint** and select this repository. Render reads `render.yaml`.
3. Set `ADMIN_EMAIL`, `ADMIN_PASSWORD` and optionally `ANTHROPIC_API_KEY`.

On the free plan the SQLite file is reset when the service restarts, so the knowledge base is re-seeded and saved user data is lost. That is fine for a demo; attach a persistent disk for real use.

## Team workflow

Backlog and sprints: [project board](https://github.com/users/PrathithShetty/projects/1) · [backlog/SPRINT_PLAN.md](backlog/SPRINT_PLAN.md)

| Member | Role | Branch | Modules |
|---|---|---|---|
| Prathith Shetty (repo owner) | Member 1 - User & Case Management | `feature/user-case-management` | `auth.py`, `account.py`, `history.py` |
| Niharika Mirle | Member 2 - Legal Query & AI Assistant | `feature/ai-legal-assistant` | `query.py`, `ai.py`, Ask page |
| Nidhi | Member 3 - Case Guidance & Recommendation | `feature/case-guidance` | `classifier.py`, `guidance.py`, `references.py`, `doc_templates.py` |
| Prarthana D Acharya | Member 4 - Admin, Database & Analytics | `feature/admin-dashboard` | `admin.py`, `feedback.py`, load test, deployment |

### Merge order

Later modules build on earlier ones, so pull requests are merged in this order. Start your PR only after the one before yours is merged into `main`.

| Sprint | Order |
|---|---|
| Sprint 1 (19-23 Oct) | Prathith → Nidhi → Niharika → Prarthana |
| Sprint 2 (26-30 Oct) | Nidhi → Niharika → Prathith → Prarthana |

### Pull request rules

1. Work on your own branch; never commit directly to `main` (it is protected).
2. Put `Closes #<issue number>` in the PR description for every backlog item it completes.
3. The `build` check (runs all tests) must be green.
4. One teammate reviews: **Files changed → Review changes → Approve**.
5. The repo owner clicks the green **Merge pull request** button (not *Close pull request*).
6. Move your cards to **Done** on the board.
7. Record any change from the submitted SRS/SAD/Test Plan in [DEVIATIONS.md](DEVIATIONS.md).

Found a bug while testing? Open a new issue with the **Bug report** template and mention the test case ID.

Practice PR by Nidhi (PES2UG24AM102)

Practice PR by Prathith Shetty (PES2UG24AM121)

Practice PR by Niharika (PES2UG24AM105)

Practice PR by Prarthana (PES2UG24AM119)
