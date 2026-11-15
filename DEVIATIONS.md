# Deviations from Submitted Documents

Record every change from the submitted SRS, SAD and Test Plan here as it happens. This is explained during the final demo.

| ID | Date | Document | Section / ID | Planned (as submitted) | Actual (as built) | Reason | Raised by |
|---|---|---|---|---|---|---|---|
| D-01 | 2026-10-09 | SRS | 5.6 Query History (FR-20, FR-21) | Registered users can store and view previous queries | Each saved query is shown as a "case" that the user can mark Open or Resolved; the history page is called "My cases" with status filters | Lets users track which legal problems are still pending, matching the team's "User & Case Management" module. FR-20 and FR-21 are still fully met. | Prathith Shetty |
| D-02 | 2026-10-09 | SRS | 3.1 User Interfaces | Home/dashboard page; no profile page listed | Added a personal dashboard (case counts, recent cases, cases by legal area) and a profile page (edit name, change password) | Improves usability for registered users (NFR-12). No existing requirement changed. | Prathith Shetty |
| D-03 | 2026-10-29 | SRS | EX-03 / Issue #49 | Case progress tracking and document checklist were not specified in the submitted SRS. | Added per-case procedure-step tracking, persistent document checklist, progress indicators, and ownership checks. | Additional Sprint 2 backlog requirement to improve case management and usability. | Nidhi |
| D-04 | 2026-11-15 | Sprint backlog | EX-04 / Issue #50 | Admin analytics, reports and user management (extra feature, not in the SRS) | Not implemented. The admin dashboard shows user, query and feedback counts only. | Not completed within Sprint 2; EX-04 was an optional extra beyond the SRS, so the SRS requirements (FR-24, FR-25) were finished first. | Prarthana D Acharya |
| D-05 | 2026-11-15 | Sprint plan | Sprint 1 and Sprint 2 dates | Sprint 1 merged 19-23 Oct; Sprint 2 merged 26-30 Oct | Sprint 1 PRs merged 28 Oct; Sprint 2 PRs merged 29 Oct, admin Sprint 2 (FR-24, FR-25, NFR-10) submitted 15 Nov | Team started Sprint 1 late; the merge order (each module builds on the previous one) carried the delay forward. | Prarthana D Acharya |
