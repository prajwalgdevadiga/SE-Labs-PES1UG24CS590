# Software Engineering — Lab Submissions

**Prajwal G Devadiga** · **PES1UG24CS590**
PES University, Dept. of CSE

| Lab | Topic | Deliverables |
|---|---|---|
| [**Lab 1**](Lab1/) | Requirements Engineering & UML Use-Case Modelling | [Requirements table](Lab1/docs/01_Requirements_Table.pdf) · [Use-case diagram](Lab1/docs/02_UseCase_Diagram.pdf) · [Use-case flow](Lab1/docs/03_UseCase_Flow_UC-01.pdf) |
| [**Lab 2**](Lab2/) | Agile Backlog Creation & Sprint Simulation in Jira | [Product backlog](Lab2/docs/01_Product_Backlog.xlsx) · [Sprint reflection](Lab2/docs/02_Reflection.pdf) · [Jira evidence](Lab2/docs/Screenshots%20pdf.pdf) |
| [**Lab 3**](Lab3/) | Component Modelling & Architectural Pattern Selection | [Component diagram](Lab3/docs/01_Component_Diagram.pdf) · [Architecture justification](Lab3/docs/02_Architecture_Justification.pdf) · [draw.io source](Lab3/diagram/subscription_box_component.drawio) |
| [**Lab 4**](Lab-4/) | Vibe Coding | [Before video](Lab-4/videos/before%20video.mp4) · [After video](Lab-4/videos/after%20video.mp4) · [Updated code](Lab-4/code/) · [Chat history](Lab-4/chat/Lab4_chat_history.pdf) |
| [**Lab 5**](Lab-5/) | Static Code Analysis | [Issues table](Lab-5/issues.md) · [Reflection](Lab-5/reflection.md) · [Before reports](Lab-5/reports/before/) · [After reports](Lab-5/reports/after/) |
| [**Lab 6**](Lab-6/) | Code and Branch Coverage Analysis | [Code coverage tests](Lab-6/CodeCoverageTest_41_laundry_service.py) · [Branch coverage tests](Lab-6/BranchCoverageTest_41_laundry_service.py) · [Coverage reports](Lab-6/screenshots/) |
| [**Lab 7**](Lab-7/) | Fuzz Testing for Input Validation Bugs | [Screenshots PDF](Lab-7/Lab7_FuzzTesting_Screenshots.pdf) · [Hardened code](Lab-7/code/laundry_service.py) · [Hypothesis suite](Lab-7/code/test_laundry_service.py) |

## Labs 1–3 — Problem Statement #35 | Retail, E-Commerce & Finance

***Customizable Subscription Box Scheduler***

> A subscription box portal where subscribers customize monthly product selections
> (books, coffee, snacks) based on preference tags, with support for pausing or
> skipping billing cycles.

These three build on each other. The functional requirements written in Lab 1 become the
Epic and User Stories of the Lab 2 product backlog, and drive the component boundaries and
the Microservices decision in Lab 3 — every story and every component carries a *Traces to*
line back to the FR or NFR it implements.

## Lab 5 — Static Code Analysis

Assigned repo: [SETAPESU26/L5_41_library_catalog_system](https://github.com/SETAPESU26/L5_41_library_catalog_system),
forked to [prajwalgdevadiga/L5_41_library_catalog_system](https://github.com/prajwalgdevadiga/L5_41_library_catalog_system).
Pylint, Bandit and Flake8 run against a library catalog script: **5.32/10 to 10.00/10**,
all five Bandit findings cleared including an `eval` and a shell injection, and every
Flake8 issue fixed. One commit per tool.

## Lab 6 — Code and Branch Coverage Analysis

Assigned repo: [SETAPESU26/L6_L7_41_laundry_service](https://github.com/SETAPESU26/L6_L7_41_laundry_service),
a laundry-service pricing module. Two test suites written against it: a statement suite
reaching 100% line coverage, and a branch suite reaching 100% branch coverage. The gap
between them is the point — the statement suite hits every line while still leaving one
decision only ever taken one way.

## Lab 7 — Fuzz Testing for Input Validation Bugs

Same repo as Lab 6, `Lab 7/` folder. Three string-parsing functions fuzzed with
Hypothesis: **5 of 9 properties failed** against the original code, all 9 pass after
hardening. The pick of the findings is `payable_charge("nan|0")` returning `nan` — the
closing `max(total, 0)` looks like it guarantees a non-negative charge, but every
comparison with `nan` is False, so the guard silently does nothing.

## Lab 4 — Vibe Coding

A separate assignment on a different codebase: [SETAPESU26/41_fruit-ninja](https://github.com/SETAPESU26/41_fruit-ninja),
a Pygame *Fruit Ninja* clone. Four tasks completed through prompting — fixing fast-swipe
collision detection, adding a game-over screen, replay with difficulty selection, and
generated sound effects — each in its own commit, with before/after gameplay videos and the
full chat history.

---

Each lab folder holds its deliverables and has its own README with the detail.
