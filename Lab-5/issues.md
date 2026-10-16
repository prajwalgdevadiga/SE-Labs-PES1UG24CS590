# Lab 5 — Static Analysis Issues Table

**Prajwal G Devadiga** · **PES1UG24CS590**
File analysed: `library_catalog_system.py` (from SETAPESU26/L5_41_library_catalog_system)

Line numbers refer to the **original** file. Ordered high severity first, as the
handout asks.

## Security issues (Bandit)

| Issue | Type | Line(s) | Description | Fix Approach |
|---|---|---|---|---|
| Weak MD5 hash | Security — **High** (B324) | 47 | `hashlib.md5()` used to hash patron IDs. MD5 is collision-broken and unfit for anything security-adjacent. | Switched to `hashlib.sha256()`. |
| Shell command injection | Security — **High** (B605) | 58 | `os.system("echo ... " + filename)` builds a shell command by string concatenation; a crafted filename would execute arbitrary commands. | The call only echoed a message, so it was replaced with `print()`. No shell is spawned at all. |
| Use of `eval` | Security — **Medium** (B307) | 42 | `calculate_fine` took a string expression and `eval`'d it. Any caller-supplied string would execute as Python. | Changed the signature to take a numeric `rate_per_day` and compute `days_overdue * rate_per_day`. Same result, no interpreter. |
| Insecure random for PIN | Security — Low (B311) | 51 | `random.randint()` is a Mersenne Twister PRNG — predictable, and these PINs authenticate patrons. | Replaced with `secrets.randbelow(9000) + 1000`. |
| `try`/`except`/`pass` | Security — Low (B110) | 26–27 | A bare `except: pass` swallows every error, hiding real failures including `KeyboardInterrupt` and `SystemExit`. | Narrowed to `except KeyError` and the function now returns `True`/`False` to report what happened. |
| Hardcoded credential | Security (not flagged) | 62 | `librarian_key = "MASTER_LIB_ACCESS_TOKEN_2026"` — a secret committed in source. Bandit's B105 did not fire because the variable name does not match its heuristics, but it is the same class of defect. | Read from the `LIBRARIAN_KEY` environment variable with a safe default. |

## Code quality issues (Pylint)

| Issue | Type | Line(s) | Description | Fix Approach |
|---|---|---|---|---|
| Mutable default argument | Bug (W0102) | 15 | `active_issues=[]` is created once at definition time and shared by every call, so issue records accumulate across unrelated calls. | Default to `None`, build a fresh list inside the function. |
| Non-conforming function name | Convention (C0103) | 15 | `issueBook` is camelCase; PEP 8 wants snake_case. | Renamed to `issue_book`. |
| Missing docstrings | Convention (C0116) | 15, 23, 30, 40, 46, 50, 54, 61 | None of the eight functions documented what they did or returned. | Docstring added to each, stating the return value. |
| `%` string formatting | Convention (C0209) | 19 | Old-style `%` formatting where an f-string is clearer. | Converted to an f-string. |
| Simplifiable if/else return | Refactor (R1703, R1705) | 34–37 | `if cond: return True else: return False` — the comparison is already a bool. | Returns the comparison directly. |
| File handle not closed on error | Refactor (R1732) | 55–57 | `open()` without a `with` block leaks the handle if the write raises. | Wrapped in `with open(...) as handle:`. |
| Unspecified encoding | Warning (W1514) | 55 | `open()` without `encoding=` uses the platform default, so output differs between machines. | Added `encoding="utf-8"`. |
| Module executes on import | Design | 73 | `main()` is called at module level, so merely importing the file runs the whole program and writes a file. | Guarded with `if __name__ == "__main__":`. |

## Style issues (Flake8)

| Issue | Type | Line(s) | Description | Fix Approach |
|---|---|---|---|---|
| Unused import | Style (F401 / W0611) | 6 | `import csv` was never used. | Removed. |
| Unused local variable | Style (F841 / W0612) | 31 | `late_fee = 1.50` assigned in `check_availability` and never read — dead code that implies a feature that is not there. | Removed. |
| Comparison to `None` with `==` | Style (E711 / C0121) | 32 | `catalog.get(book_id) == None` relies on `__eq__`; identity is what is meant. | Changed to `is None`. |
| Unused local variable | Style (F841 / W0612) | 41 | `days = days_overdue` existed only to give `eval` a name to bind. | Removed along with the `eval`. |
| Bare `except` | Style (E722 / W0702) | 26 | Catches everything, including control-flow exceptions. | Narrowed to `except KeyError` (same fix as B110 above). |
| No newline at end of file | Style (W292 / C0304) | 73 | POSIX text files end with a newline; diffs are noisier without it. | Added. |

## Results

| Tool | Before | After |
|---|---|---|
| Pylint | 5.32/10, 22 messages | **10.00/10**, 0 messages |
| Bandit | 5 issues (2 high, 1 medium, 2 low) | **0 issues** |
| Flake8 | 6 issues | **0 issues** |

The program's behaviour is unchanged apart from two deliberate differences: the
patron hash is now a SHA-256 digest rather than MD5, and the librarian key is
read from the environment instead of being printed from a literal in the source.
