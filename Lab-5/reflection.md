# Lab 5 — Reflection

**Prajwal G Devadiga** · **PES1UG24CS590**

> The handout asks for "answers to the reflection questions provided in the lab"
> without listing them, so these are the four implied by the stated learning
> outcomes. Swap in the exact wording if your section was given different ones.

## 1. Which tool surfaced the most serious problems, and why?

Bandit, clearly — but only because of what it is looking for. It found the two
genuinely dangerous things in the file: the `eval()` in `calculate_fine`, which
hands a caller-supplied string straight to the interpreter, and the
`os.system("echo ... " + filename)` in `export_catalog`, which builds a shell
command by concatenation. Either one turns a filename or a fine expression into
arbitrary code execution.

What is worth noticing is that Pylint also flagged the `eval` (W0123) and said
nothing about `os.system`. Pylint judges the code as code; Bandit judges it as
an attack surface. The same line gets a shrug from one tool and a High from the
other.

## 2. Were there findings you disagreed with, or that the tools missed?

Two of each.

Bandit's B311 (`random.randint` for PINs) reads as a low-severity nitpick until
you notice those PINs authenticate patrons — then it is real, and the fix costs
one import. I changed it. B110 (`try/except/pass`) is reported as a security
issue, which felt like a stretch; it is really a correctness bug, since the bare
`except` also swallows `KeyboardInterrupt`. I fixed it anyway, for the
correctness reason rather than the security one.

More interesting is what no tool caught. `librarian_key = "MASTER_LIB_ACCESS_TOKEN_2026"`
is a credential committed to source. Bandit has a check for exactly this (B105,
hardcoded_password_string), but it did not fire — B105 matches on *variable
names* containing password/token/secret, and this one is called `librarian_key`.
The giveaway was in the value, not the name. I moved it to an environment
variable regardless. The lesson is that a clean Bandit report means "none of my
patterns matched", not "this code is secure".

The second miss is structural: `main()` was called at module level, so importing
the file for any reason runs the program and writes a file to disk. No tool
objected. Pylint has no rule for it because it is legal Python.

## 3. How did the three tools differ in what they caught?

They overlap more than their descriptions suggest, but each owns a region:

- **Bandit alone** caught `os.system`, MD5, and the insecure PRNG — all
  dangerous-API questions that say nothing about style or structure.
- **Pylint alone** caught the mutable default argument `active_issues=[]`, which
  was the most interesting defect in the file. It is not a style problem and not
  a security problem; it is a latent bug that only shows up on the second call,
  when the list from the first call is still there.
- **Flake8 alone** caught the missing newline at end of file. Trivial, but it is
  the kind of thing nobody notices by eye.
- **All three** caught the bare `except` — as E722, W0702 and B110 respectively,
  each framing it as a different category of problem.

Running one tool and assuming the others would agree would have missed something
in every direction.

## 4. What does static analysis contribute to quality and maintainability?

The honest answer is that it is cheap and shallow, and that combination is what
makes it worth running. It cost nothing to go from 5.32/10 to 10.00/10, and the
mutable-default bug it found is the sort that survives code review because the
line looks perfectly ordinary.

But "10.00/10, no issues" is not a claim that the code is correct. After all the
fixes, `return_book("B02")` still adds a copy of a book that was never issued —
the catalog gains a book out of nowhere, and every tool is silent, because the
code does precisely what it says. Static analysis checks the properties it can
check without running anything: shapes, names, known-dangerous calls. The
coverage work in Lab 6 is the complement — it asks whether the behaviour is
actually exercised, which no amount of linting can tell you.

Where it earns its keep is as a floor rather than a ceiling. Wired into CI, it
stops the whole category of defect it understands from ever reaching review,
which leaves review free for the things a tool cannot see.
