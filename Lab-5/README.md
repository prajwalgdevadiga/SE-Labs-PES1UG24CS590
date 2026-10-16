# Lab 5 — Static Code Analysis

**Prajwal G Devadiga** · **PES1UG24CS590**
Software Engineering — Lab 5 · PES University, Dept. of CSE

**Forked repo:** https://github.com/prajwalgdevadiga/L5_41_library_catalog_system
Upstream: [SETAPESU26/L5_41_library_catalog_system](https://github.com/SETAPESU26/L5_41_library_catalog_system)

## Contents

| Path | What it is |
|---|---|
| [`issues.md`](issues.md) | The issues table — every finding, its severity, and how it was fixed |
| [`reflection.md`](reflection.md) | Answers to the reflection questions |
| `code/library_catalog_system.py` | The cleaned script |
| `reports/before/` | `pylint_report.txt`, `bandit_report.txt`, `flake8_report.txt` — first run |
| `reports/after/` | The same three, after the fixes |

## Results

| Tool | Before | After |
|---|---|---|
| Pylint | 5.32/10, 22 messages | **10.00/10**, 0 messages |
| Bandit | 5 issues — 2 high, 1 medium, 2 low | **0 issues** |
| Flake8 | 6 issues | **0 issues** |

The handout asks for a Pylint score above 9.5, all Bandit findings handled and
all Flake8 formatting issues cleared. All three are met.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install pylint bandit flake8
```

## Running the analysis

```bash
cd code
pylint library_catalog_system.py > ../reports/after/pylint_report.txt
bandit -r library_catalog_system.py > ../reports/after/bandit_report.txt
flake8 library_catalog_system.py > ../reports/after/flake8_report.txt
```

## Commits

One per tool, as the handout requires:

| Commit | Scope |
|---|---|
| `Lab 5: add assigned script and baseline static analysis reports` | The unmodified script and the first run of all three tools |
| `Lab 5: fix Bandit security findings` | `eval`, MD5, `os.system`, insecure PRNG, `try/except/pass`, hardcoded token |
| `Lab 5: fix Pylint code quality findings` | Naming, mutable default argument, docstrings, f-string, `with`/encoding, `__main__` guard |
| `Lab 5: fix Flake8 style findings` | Unused import, unused locals, `== None`, missing final newline |

## The most interesting findings

**A bug no linter would phrase as a bug.** `issueBook(book_id, patron, active_issues=[])`
builds that list once at definition time, so every call shares it and issue
records pile up across unrelated calls. Pylint calls it W0102; it reads as a
style nit and is actually the worst defect in the file.

**A credential Bandit missed.** `librarian_key = "MASTER_LIB_ACCESS_TOKEN_2026"`
is exactly what Bandit's B105 exists to catch, but B105 matches on variable
*names* containing password/token/secret — and this one is called
`librarian_key`. The giveaway was in the value. Moved to an environment variable
regardless.

**A bug all three tools are silent about.** Even at 10.00/10 with zero findings,
`return_book("B02")` adds a copy of a book that was never issued — B02 goes from
1 copy to 2 out of nowhere. The code does exactly what it says, so nothing flags
it. That is the boundary of static analysis, and the reason Lab 6's coverage work
is the complement to it.
