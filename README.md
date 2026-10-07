# PA 6: The Activation Record

Full assignment: `PA_06_The_Activation_Record.md`.

## Setup
Paste your own completed `lexer.py`/`parser.py`/`symtable.py` in
first (bundled for the `Environment` class; see the note at the top
of `frames.py` for why this PA's test harness doesn't parse real
USILang function syntax).

## Run
```bash
python test_frames.py
```
Complete `ActivationRecord` and `CallStack` in `frames.py`. The
harness simulates `factorial(5)`/`factorial(4)` and a nested-function
call sequence, checking max stack depth, `dynamic_link` correctness,
and that `static_link` differs from `dynamic_link` for the nested
case. Prints the literal string `ACTIVATION_RECORD_VERIFIED` (not a
generated token, per the assignment) once every check passes.

## Submit
1. `PA6_Theory.pdf` (or `.md`)
2. `frames.py` (and your working `lexer.py`/`parser.py`/`symtable.py`)
3. Terminal output/screenshot showing `ACTIVATION_RECORD_VERIFIED`
