# -*- coding: utf-8 -*-
"""
Generates the repository README.md from content.py so the GitHub view and the
submitted documents can never drift apart.

    python build_readme.py
"""
import os

from content import (STUDENT, SCENARIO, REQUIREMENTS, ACTORS, USE_CASES,
                     RELATIONSHIPS, FLOW)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def esc(s):
    return s.replace("|", "\\|")


def build():
    L = []
    a = L.append

    a("# Lab 1 — Requirements Engineering & UML Use-Case Modelling")
    a("")
    a("**%s** · **%s**  " % (STUDENT["name"], STUDENT["srn"]))
    a("%s — %s  " % (STUDENT["course"], STUDENT["topic"]))
    a("%s" % STUDENT["ps"])
    a("")
    a("## Scenario")
    a("")
    a("> **%s**  " % STUDENT["system"])
    a("> %s" % SCENARIO)
    a("")
    a("## Deliverables")
    a("")
    a("| # | Deliverable | Files |")
    a("|---|---|---|")
    a("| 1 | Requirements Table — 5 FRs + 2 NFRs with ID, Type, Description, Priority, "
      "Acceptance Criteria, Rationale, Comments | [`.docx`](docs/01_Requirements_Table.docx) · "
      "[`.xlsx`](docs/01_Requirements_Table.xlsx) · [`.pdf`](docs/01_Requirements_Table.pdf) |")
    a("| 2 | UML Use-Case Diagram — 4 actors, 10 use cases, 4 `«include»` + 2 `«extend»` | "
      "[`.pdf`](docs/02_UseCase_Diagram.pdf) · [`.png`](docs/02_UseCase_Diagram.png) · "
      "[editable `.drawio`](diagram/subscription_box_usecase.drawio) |")
    a("| 3 | Use-Case Flow — %s %s, preconditions, postconditions, main success scenario, "
      "2 alternate flows | [`.docx`](docs/03_UseCase_Flow_UC-01.docx) · "
      "[`.pdf`](docs/03_UseCase_Flow_UC-01.pdf) |" % (FLOW["id"], FLOW["name"]))
    a("")
    a("---")
    a("")

    # ---------------------------------------------------------- requirements
    a("## 1. Requirements Table")
    a("")
    a("| Req ID | Type | Priority | Description (\"The system shall …\") |")
    a("|---|---|---|---|")
    for r in REQUIREMENTS:
        a("| **%s** | %s | %s | %s |" % (r["id"], esc(r["type"]), r["priority"],
                                         esc(r["description"])))
    a("")
    a("<details>")
    a("<summary><b>Acceptance criteria, rationale and peer-critique comments (click to expand)</b></summary>")
    a("")
    for r in REQUIREMENTS:
        tag = " _(given with the problem statement)_" if r.get("given") else ""
        a("#### %s — %s%s" % (r["id"], r["type"], tag))
        a("")
        a("**Description.** %s" % r["description"])
        a("")
        a("**Acceptance criteria.** %s" % r["acceptance"])
        a("")
        a("**Rationale.** %s" % r["rationale"])
        a("")
        a("**Peer critique → revision.** %s" % r["comments"])
        a("")
    a("</details>")
    a("")
    a("> FR-001 and NFR-001 are the requirements supplied with Problem Statement #35. "
      "FR-002–FR-005 and NFR-002 are student-authored. The *Comments* column records the "
      "peer-critique round (Lab step 3) and the revision each comment produced.")
    a("")
    a("---")
    a("")

    # ---------------------------------------------------------- diagram
    a("## 2. UML Use-Case Diagram")
    a("")
    a("![Use-case diagram](docs/02_UseCase_Diagram.png)")
    a("")
    a("Submit [`docs/02_UseCase_Diagram.pdf`](docs/02_UseCase_Diagram.pdf). "
      "To edit, open [`diagram/subscription_box_usecase.drawio`](diagram/subscription_box_usecase.drawio) "
      "at [app.diagrams.net](https://app.diagrams.net) via **File → Open From → Device**.")
    a("")
    a("### Actors")
    a("")
    a("| Actor | Classification | Goal in the system |")
    a("|---|---|---|")
    for name, kind, goal in ACTORS:
        a("| **%s** | %s | %s |" % (name, kind, goal))
    a("")
    a("### Use cases")
    a("")
    a("| UC ID | Use Case | Actor / relationship | Traces to |")
    a("|---|---|---|---|")
    for uid, title, actor, traces in USE_CASES:
        a("| **%s** | %s | %s | %s |" % (uid, title, actor, traces))
    a("")
    a("### `«include»` and `«extend»` relationships")
    a("")
    a("| Stereotype | From | To | Why |")
    a("|---|---|---|---|")
    for kind, src, dst, why in RELATIONSHIPS:
        a("| `«%s»` | %s | %s | %s |" % (kind, src, dst, why))
    a("")
    a("*Reading the arrows:* an `«include»` arrow points **from the base use case to the "
      "included one** (the included behaviour always runs); an `«extend»` arrow points **from "
      "the extending use case back to the base** (the behaviour runs only when its condition "
      "holds).")
    a("")
    a("---")
    a("")

    # ---------------------------------------------------------- flow
    a("## 3. Use-Case Flow — %s %s" % (FLOW["id"], FLOW["name"]))
    a("")
    for k, v in FLOW["meta"]:
        a("- **%s:** %s" % (k, v))
    a("")
    a("**Preconditions**")
    a("")
    for i, p in enumerate(FLOW["preconditions"], 1):
        a("%d. %s" % (i, p))
    a("")
    a("**Postconditions**")
    a("")
    for i, p in enumerate(FLOW["postconditions"], 1):
        a("%d. %s" % (i, p))
    a("")
    a("**Main Success Scenario**")
    a("")
    for i, s in enumerate(FLOW["main"], 1):
        a("%d. %s" % (i, s))
    a("")
    a("**Alternate Flows**")
    a("")
    for alt in FLOW["alternates"]:
        a("*%s*" % alt["title"])
        a("")
        for s in alt["steps"]:
            a("- %s" % s)
        a("")
    a("**Exception Flow**")
    a("")
    a("- %s" % FLOW["exception"])
    a("")
    a("---")
    a("")

    # ---------------------------------------------------------- repo
    a("## Repository layout")
    a("")
    a("```")
    a("docs/     final deliverables (submit these)")
    a("diagram/  editable draw.io source for the use-case diagram")
    a("build/    scripts that generate everything in docs/ from content.py")
    a("```")
    a("")
    a("## Regenerating the deliverables")
    a("")
    a("`build/content.py` is the single source of truth — every table, diagram label and flow "
      "step is written once there. Edit it, then:")
    a("")
    a("```bash")
    a("pip install python-docx openpyxl reportlab matplotlib")
    a("cd build")
    a("python build_diagram.py   # docs/02_UseCase_Diagram.pdf + .png, diagram/*.drawio")
    a("python build_docs.py      # docs/01_*.docx/.xlsx/.pdf, docs/03_*.docx/.pdf")
    a("python build_readme.py    # this README")
    a("```")
    a("")

    with open(os.path.join(ROOT, "README.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L))
    print("wrote README.md")


if __name__ == "__main__":
    build()
