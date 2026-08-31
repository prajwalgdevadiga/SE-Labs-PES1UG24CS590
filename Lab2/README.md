# Lab 2 — Agile Backlog Creation & Sprint Simulation in Jira

**Prajwal G Devadiga** · **PES1UG24CS590**
Software Engineering — Lab 2 · PES University, Dept. of CSE

Problem Statement #35 | Retail, E-Commerce & Finance — *Customizable Subscription Box Scheduler*
Jira project key `SBOX`. Backlog derived from the Lab 1 functional requirements.

> A subscription box portal where subscribers customize monthly product selections
> (books, coffee, snacks) based on preference tags, with support for pausing or
> skipping billing cycles.

## Deliverables

| File | What it is |
|---|---|
| [`docs/01_Product_Backlog.xlsx`](docs/01_Product_Backlog.xlsx) | The Epic and its 6 User Stories in *As a / I want / So that* form, with priorities, Fibonacci story points, planning-poker rationale and the two-sprint plan |
| [`docs/02_Reflection.pdf`](docs/02_Reflection.pdf) | The brief document answering the four reflection questions |
| [`docs/Screenshots pdf.pdf`](docs/Screenshots%20pdf.pdf) | Jira evidence — backlog with Epic and stories, story point assignments, Active Sprint board, burndown chart |

## Backlog

**EPIC-1 — Box Customization & Billing Cycle Control** · 34 story points · traces to FR-001–FR-005, NFR-001

> Take a subscriber from a personalised monthly box to a correctly billed and shipped one:
> capture preference tags, let them swap items or pause and skip a cycle before the 48-hour
> cut-off, then bill the locked box and hand the warehouse its manifest.

| Story | Priority | Points | Sprint | Traces to |
|---|---|---|---|---|
| **US-1.1** Manage Preference Tags | High | 5 | Sprint 1 | FR-002 |
| **US-1.2** Swap Items in the Next Box | High | 8 | Sprint 1 | FR-001 |
| **US-1.3** Enforce the 48-Hour Cut-Off | Medium | 5 | Sprint 1 | FR-001 |
| **US-1.4** Pause or Skip a Billing Cycle | High | 5 | Sprint 2 | FR-001, FR-003 |
| **US-1.5** Bill the Locked Box on Renewal | High | 8 | Sprint 2 | FR-004 |
| **US-1.6** Generate the Fulfillment Manifest | Medium | 3 | Sprint 2 | FR-005, NFR-001 |

## Sprints

| Sprint | Goal | Stories | Points |
|---|---|---|---|
| **SBOX Sprint 1** | A subscriber can express their preferences and change the contents of their next box, with the 48-hour cut-off protecting the warehouse. | 3 | 18 |
| **SBOX Sprint 2** | A subscriber can pause or skip a cycle, the locked box is billed on renewal, and the warehouse receives its manifest. | 3 | 16 |

Sprint 1 is the dependency root — preference tags must exist before a box can be recommended,
and a box must be customisable before a cut-off means anything. Sprint 2 consumes everything
Sprint 1 produced. Both sprints were run to completion in Jira and the burndown chart for each
is included in the evidence PDF.

## Estimation

Story points use the Fibonacci scale, assigned by planning poker. The two 8-point stories
(US-1.2, US-1.5) each drew a 5 / 8 / 13 spread, with the high estimates driven by uncertainty
rather than code volume — re-picking a box whose stock is already reserved, and bounded
payment retries across a suspension state. The per-story rationale is in the *Planning Poker*
column of the backlog spreadsheet.
