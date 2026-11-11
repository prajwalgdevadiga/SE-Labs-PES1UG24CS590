# Lab 7 — Fuzzing for Input Validation Bugs

**Prajwal G Devadiga** · **PES1UG24CS590**
Software Engineering — Lab 7 · PES University, Dept. of CSE

Assigned repo: [SETAPESU26/L6_L7_41_laundry_service](https://github.com/SETAPESU26/L6_L7_41_laundry_service)
(`Lab 7/`) — order parsing, weight averaging and charge calculation.
Fuzzed with [Hypothesis](https://hypothesis.readthedocs.io/).

## Deliverables

| Path | What it is |
|---|---|
| [`Lab7_FuzzTesting_Screenshots.pdf`](Lab7_FuzzTesting_Screenshots.pdf) | The four required screenshots with commentary |
| `code/laundry_service.py` | The hardened application |
| `code/test_laundry_service.py` | The completed Hypothesis suite |
| `screenshots/` | The four terminal screenshots, one per required step |

## Results

| Stage | Outcome |
|---|---|
| Buggy app, valid input | Works |
| Buggy app, `regular` (no colon) | **Crashes** — unhandled `ValueError` |
| Hypothesis suite vs buggy code | **5 failed**, 4 passed |
| Hardened app, same malformed input | Reported and skipped |
| Hypothesis suite vs hardened code | **9 passed** |

## What Hypothesis found

Three functions, each parsing a string by splitting it and calling `float()` or
`int()` on the pieces. Hypothesis minimised every failure to a tiny input:

| Function | Input | Failure |
|---|---|---|
| `parse_order` | `''` | `ValueError: not enough values to unpack` — no `:` present |
| `parse_order` | `None` | `AttributeError: 'NoneType' has no attribute 'split'` |
| `parse_order` | `'a:b:c'` | too many values to unpack |
| `weight_average` | `''` | `ValueError: invalid literal for int()` |
| `payable_charge` | `'0'` | unpack failure — no `|` separator |
| `payable_charge` | `'nan\|0'` | returns `nan`, because `max(nan, 0)` is `nan` |

That last one is the interesting one. `payable_charge` ends with
`return max(total, 0)`, which looks like it guarantees a non-negative charge.
It does not: every comparison involving `nan` is False, so `max` returns the
`nan` unchanged and the caller gets a bill of `nan`. No crash, no error — just a
wrong answer that propagates. A hand-written test would have to think of `nan`
to find it; Hypothesis generates it as a matter of course.

## The contract after hardening

Each function returns a result, or returns `None`. It never raises. Callers
check for `None` rather than wrapping parser calls in `try`/`except`.

Rejected: wrong type, wrong number of separators, empty garment name,
non-numeric fields, `nan`/`inf`, and negative weights or charges.

One behaviour change beyond validation: `weight_average` used `//`, which floors
and therefore biases every inexact average downward — `[0, 1, 1]` averages to
`0` rather than `1`, and `[2, 3, 3]` to `2` rather than `3`. It now rounds to
nearest. For the sample input `3,5,8` both give `5`, so the demo output is
unchanged.

This one is **not** something the fuzzing found. Hypothesis cannot see it,
because flooring never actually breaks the min/max property — the true mean is
at least the minimum, and the minimum is an integer, so `floor(mean)` can never
drop below it. `test_weight_average_lies_between_min_and_max` passes against the
original code too. The bias is a correctness judgement made by reading the
function, not a bug a property test surfaced.

## Running it

```bash
pip install hypothesis pytest
cd code
python laundry_service.py
pytest test_laundry_service.py
```

## The suite

Nine properties across the three functions. Three are the handout's "must not
crash" check driven by a strategy covering text, `None`, integers, floats,
booleans, lists and raw bytes. The other six are stronger, because a function
that always returned `None` would pass a crash test while being useless:

- `parse_order` returns a non-empty name and a finite weight at or above zero.
- Well-formed orders still parse — hardening must not reject everything.
- `weight_average` lands between the minimum and maximum of its inputs.
- The average of one value is that value.
- `payable_charge` is never negative, `nan` or infinite.
- Valid input still computes `charge × 1.18 − discount`, floored at zero.
