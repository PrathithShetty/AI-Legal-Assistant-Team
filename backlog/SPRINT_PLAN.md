# Sprint Plan - AI-Based Legal Assistant, e-Lawyer and Case Guidance System

Project ID 28 | UE24CS341A Software Engineering | Repo: [PrathithShetty/AI-Legal-Assistant-Team](https://github.com/PrathithShetty/AI-Legal-Assistant-Team)

## Team

| Member | SRN | GitHub |
|---|---|---|
| Prathith Shetty | PES2UG24AM121 | [@PrathithShetty](https://github.com/PrathithShetty) |
| Niharika Mirle | PES2UG24AM105 | [@Niharika1704](https://github.com/Niharika1704) |
| Nidhi | PES2UG24AM102 | [@nidhibillava3103](https://github.com/nidhibillava3103) |
| Prarthana D Acharya | PES2UG24AM119 | [@prarthanaa11](https://github.com/prarthanaa11) |

## Estimation

Story points use the Fibonacci scale (1, 2, 3, 5, 8): 1 = trivial UI/text change, 2-3 = small feature with validation and tests, 5 = feature with backend + frontend + data, 8 = feature with external integration (LLM service). Each FR and NFR from the SRS is one backlog item; BR-01 to BR-05 are folded into the acceptance criteria of the related items (FR-04, FR-07, FR-09, NFR-04).

## Points per member

| Member | Sprint 0 | Sprint 1 | Sprint 2 | Total |
|---|---|---|---|---|
| Prathith Shetty | 7 | 16 | 14 | 37 |
| Niharika Mirle | 0 | 10 | 20 | 30 |
| Nidhi | 0 | 19 | 14 | 33 |
| Prarthana D Acharya | 0 | 17 | 17 | 34 |
| **Total** | **7** | **62** | **65** | **134** |

## Sprint 0 - Dry Run (12-16 Oct)

Due: 2026-10-16 | 7 points

| ID | Title | Area | Priority | Pts | Assignee |
|---|---|---|---|---|---|
| T-01 | Set up project skeleton (frontend, backend, database) | Setup | High | 3 | Prathith Shetty |
| T-02 | Enable GitHub Actions CI and protect main branch | Setup | High | 2 | Prathith Shetty |
| T-06 | Document team roles, branches and merge order in the README | Setup | Medium | 1 | Prathith Shetty |
| T-07 | Add GitHub issue templates for bug reports and user stories | Setup | Medium | 1 | Prathith Shetty |

## Sprint 1 (19-23 Oct)

Due: 2026-10-23 | 62 points

| ID | Title | Area | Priority | Pts | Assignee |
|---|---|---|---|---|---|
| FR-10 | Classify legal queries into categories | Issue Guidance | High | 5 | Nidhi |
| FR-12 | Provide procedure steps for identified issue | Issue Guidance | High | 3 | Nidhi |
| FR-13 | Indicate when professional legal help is required | Issue Guidance | High | 2 | Nidhi |
| FR-14 | Retrieve relevant legal references | Legal References | Medium | 5 | Nidhi |
| FR-15 | Display legal reference details | Legal References | Medium | 2 | Nidhi |
| FR-16 | Indicate when no reference is available | Legal References | Medium | 1 | Nidhi |
| NFR-06 | Encourage consulting a qualified lawyer when needed | Safety | High | 1 | Nidhi |
| FR-05 | Submit legal question in natural language | AI Legal Query | High | 2 | Niharika Mirle |
| FR-06 | Validate query input | AI Legal Query | High | 1 | Niharika Mirle |
| FR-08 | Present responses in a clear, structured format | AI Legal Query | High | 3 | Niharika Mirle |
| FR-09 | Display legal disclaimer with responses | AI Legal Query | High | 1 | Niharika Mirle |
| FR-11 | Display identified legal category | Issue Guidance | High | 1 | Niharika Mirle |
| NFR-04 | Communicate output is informational, not legal advice | Safety | High | 1 | Niharika Mirle |
| T-03 | Record 1-minute Sprint 1 demo video and upload to repo | Delivery | High | 1 | Niharika Mirle |
| FR-22 | Submit feedback | Feedback/Admin | Medium | 2 | Prarthana D Acharya |
| FR-23 | Admin: manage approved legal information | Feedback/Admin | Medium | 5 | Prarthana D Acharya |
| NFR-01 | Responses within reasonable time | Performance | Medium | 3 | Prarthana D Acharya |
| NFR-02 | Process queries without unnecessary delays | Performance | Medium | 2 | Prarthana D Acharya |
| NFR-03 | Support multiple concurrent users | Performance | Medium | 3 | Prarthana D Acharya |
| NFR-08 | Authorization for administrative functions | Security | Medium | 2 | Prarthana D Acharya |
| FR-01 | User account creation | Authentication | High | 3 | Prathith Shetty |
| FR-02 | Validate registration information | Authentication | High | 2 | Prathith Shetty |
| FR-03 | Login and logout | Authentication | High | 3 | Prathith Shetty |
| FR-04 | Restrict administrative functions to administrators | Authentication | High | 3 | Prathith Shetty |
| NFR-07 | Authenticate before account-specific information | Security | High | 2 | Prathith Shetty |
| NFR-11 | Passwords not stored in plain text | Security | High | 1 | Prathith Shetty |
| NFR-13 | Maintainability through modular components | Quality | High | 2 | Prathith Shetty |

## Sprint 2 (26-30 Oct)

Due: 2026-10-30 | 65 points

| ID | Title | Area | Priority | Pts | Assignee |
|---|---|---|---|---|---|
| EX-03 | Case progress tracking and document checklist | Issue Guidance | Medium | 5 | Nidhi |
| FR-17 | Display available document templates | Document Templates | Medium | 2 | Nidhi |
| FR-18 | Explain purpose of each template | Document Templates | Medium | 1 | Nidhi |
| FR-19 | View or generate supported templates | Document Templates | Medium | 5 | Nidhi |
| T-04 | Record 2-minute Sprint 2 demo video and upload to repo | Delivery | High | 1 | Nidhi |
| FR-07 | Generate informational AI response | AI Legal Query | High | 8 | Niharika Mirle |
| NFR-05 | Avoid presenting uncertain information as guaranteed | Safety | High | 3 | Niharika Mirle |
| NFR-12 | Usability for non-technical users | Quality | High | 3 | Niharika Mirle |
| NFR-14 | Reliability: handle invalid or unsupported inputs gracefully | Quality | Medium | 2 | Niharika Mirle |
| NFR-15 | Testability: independently testable modules | Quality | Medium | 2 | Niharika Mirle |
| NFR-16 | Portability across modern browsers | Quality | Medium | 2 | Niharika Mirle |
| EX-04 | Admin analytics, reports and user management | Feedback/Admin | Medium | 5 | Prarthana D Acharya |
| FR-24 | Admin: manage legal references and templates | Feedback/Admin | Medium | 5 | Prarthana D Acharya |
| FR-25 | Admin: review submitted feedback | Feedback/Admin | Medium | 3 | Prarthana D Acharya |
| NFR-10 | Secure HTTPS communication | Security | Medium | 2 | Prarthana D Acharya |
| T-05 | Complete documentation and deviation log; freeze development | Delivery | High | 2 | Prarthana D Acharya |
| EX-01 | Case status: mark cases Open or Resolved | User & Case Management | Medium | 2 | Prathith Shetty |
| EX-02 | User dashboard and profile | User & Case Management | Medium | 3 | Prathith Shetty |
| FR-20 | Store queries and responses for registered users | Query History | Medium | 3 | Prathith Shetty |
| FR-21 | View own query history | Query History | Medium | 3 | Prathith Shetty |
| NFR-09 | Protect user information and stored queries | Security | Medium | 3 | Prathith Shetty |

## Sprint goals

- **Sprint 0 (dry run):** repo skeleton, CI, branch protection; every member raises one practice PR.
- **Sprint 1:** working core product - register/login, ask a legal question, get a structured AI answer with category, procedure steps, lawyer recommendation and disclaimer. Deliverable: 1-minute demo video.
- **Sprint 2:** legal references, document templates, query history, feedback and admin dashboard; performance, security and quality NFRs; final documentation and deviation log. Deliverable: 2-minute demo video, development frozen.

## Workflow

1. Pick your issue on the board and move it to **In Progress**.
2. Create a branch: `git checkout -b <srs-id>-short-name` (e.g. `fr-07-ai-response`).
3. Commit and push, then open a PR with `Closes #<issue number>` in the description. The assignee raises the PR.
4. CI (`build` check) must pass and the repo owner reviews and merges the PR.
5. Merging closes the issue and moves the card to **Done**.
6. Any change from the submitted SRS/SAD/Test Plan goes in `DEVIATIONS.md`.
