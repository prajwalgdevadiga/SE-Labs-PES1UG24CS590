# Lab 6 — Code and Branch Coverage Analysis

**Prajwal G Devadiga** · **PES1UG24CS590**
Software Engineering — Lab 6 · PES University, Dept. of CSE

Assigned repo: [SETAPESU26/L6_L7_41_laundry_service](https://github.com/SETAPESU26/L6_L7_41_laundry_service) —
a small laundry-service pricing module.

## Files

| File | What it is |
|---|---|
| `laundry_service.py` | The module under test (unchanged from the assigned repo) |
| `test_laundry_service.py` | The two starter tests shipped with the repo |
| `CodeCoverageTest_41_laundry_service.py` | Statement-coverage suite — 12 tests |
| `BranchCoverageTest_41_laundry_service.py` | Branch-coverage suite — 36 tests |
| `screenshots/` | Terminal output for each run |

## Results

| Suite | Tests | Statement | Branch | Partial branches |
|---|---|---|---|---|
| Starter (`test_laundry_service.py`) | 2 | 38% | 32% | 6 |
| `CodeCoverageTest_41_laundry_service.py` | 12 | **100%** | 98% | 1 (`21->23`) |
| `BranchCoverageTest_41_laundry_service.py` | 36 | **100%** | **100%** | 0 |

Both suites clear the 90% threshold the handout asks for.

## Commands

```bash
pip install coverage pytest
```

Statement coverage:

```bash
coverage run -m pytest CodeCoverageTest_41_laundry_service.py
coverage report -m
```

Branch coverage:

```bash
coverage run --branch -m pytest BranchCoverageTest_41_laundry_service.py
coverage report -m
```

## Analysis — where line coverage lied

The statement suite reaches **100% line coverage**. Re-measured with `--branch`,
the same suite drops to **98%**, with one partial branch reported as `21->23`:

```
Name                 Stmts   Miss Branch BrPart  Cover   Missing
laundry_service.py      37      0     26      1    98%   21->23
```

Lines 19–23 of `laundry_service.py`:

```python
if extra > 10:
    rate = rate + 15
    if speed == "express":    # line 21
        rate += 10
return extra * rate           # line 23
```

`if speed == "express"` was only ever evaluated **True**. Its False path falls
straight through to line 23, which the True path already reaches — so every line
counted as covered while that decision had only been taken one way. The order
that exposes it is more than 10 kg over the allowance at *standard* speed:

```python
extra_weight_charge("regular", 20, "standard", False)   # 15 kg × (30 + 15) = 675
```

**Why this is the only gap possible here.** Every other decision in the module
sends its two outcomes to different lines, so covering all the lines forces both
sides of those decisions anyway. Line 21 is the single place where one outcome
adds a statement and the other adds nothing — which is exactly the shape of
decision that line coverage cannot see.

## Branch suite design

Beyond closing that gap, the branch suite drives each decision from both sides
and pins the comparisons at their boundaries:

- `is_member and garment_type != "bedding"` — a compound condition, so each
  operand is falsified on its own (non-member; member with bedding).
- `extra <= 0` at exactly 0 and at 1.
- `extra > 10` at exactly 10 and at 11.
- `speed` checked as standard, express, and a third value, since the `else` is a
  catch-all rather than an express-only path.
- `items <= 5` at 5 and 6; `weight_kg > 25` at 25 and 26; `items <= 40` at 40 and 41.
- `dropoff_status` at the cutoff, one minute inside it, at the grace floor
  (`cutoff - 20`) and one minute below it, for each cutoff the flags produce.
