# Lab 2 — Agile Backlog Creation & Sprint Simulation in Jira

**Prajwal G Devadiga** · **PES1UG24CS590**
Software Engineering — Lab 2

Backlog derived from the Lab 1 functional requirements for Problem Statement #03 —
*Campus Placement & Internship Pipeline*. Jira project key `CPIP`.

## Deliverables

| File | What it is |
|---|---|
| [`docs/01_Product_Backlog.xlsx`](docs/01_Product_Backlog.xlsx) | The Epic and its 6 User Stories in *As a / I want / So that* form, with priorities, Fibonacci story points and planning-poker rationale |
| [`docs/02_Reflection.pdf`](docs/02_Reflection.pdf) ([docx](docs/02_Reflection.docx)) | The brief document answering the four reflection questions |
| [`docs/Screenshots pdf.pdf`](docs/Screenshots%20pdf.pdf) ([docx](docs/Screenshots%20pdf.docx)) | Jira evidence — backlog, story point assignments, active sprint board, burndown chart |

## Backlog

**EPIC-1 — Drive Application & Eligibility Screening** · 34 story points · traces to FR-001, FR-002, FR-003

> Take a student from a published corporate drive to a submitted, screened application:
> publish the drive with its eligibility rule set, parse the student's resume, show them
> exactly where they stand against each rule, and let eligible students apply before the
> window closes.

| Story | Priority | Points | Sprint | Traces to |
|---|---|---|---|---|
| **US-1.1** Upload & Parse Resume | High | 8 | Sprint 1 | FR-001 |
| **US-1.2** Create a Corporate Drive | High | 5 | Sprint 1 | FR-002 |
| **US-1.3** Configure Multi-Tier Eligibility | High | 8 | Sprint 1 | FR-002 |
| **US-1.4** See Eligibility Status per Drive | Medium | 5 | Sprint 2 | FR-001, FR-003 |
| **US-1.5** Apply to an Eligible Drive | High | 5 | Sprint 2 | FR-003 |
| **US-1.6** Enforce the Application Window | Medium | 3 | Sprint 2 | FR-003 |

## Sprints

| Sprint | Goal | Stories | Points |
|---|---|---|---|
| **CPIP Sprint 1** | A placement officer can publish a drive carrying its full eligibility rule set, and a student has a parsed profile for those rules to be evaluated against. | 3 | 21 |
| **CPIP Sprint 2** | A student can see exactly where they stand against every published drive and submit an application while the window is still open. | 3 | 13 |

Sprint 1 is the dependency root: every Sprint 2 story reads either the parsed profile from
US-1.1 or the rule set from US-1.3, so none of them can be demonstrated until those land.
