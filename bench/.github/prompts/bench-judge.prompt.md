---
mode: agent
description: "Grade every ungraded run against its case's checks (use @judge, same judge model every time)"
---
Judge model currently selected in the picker (I typed it): `${input:judge_model}`. Optional case filter: `${input:case}`.
If `judge_model` is empty, stop and ask — every result must record which model judged it, and it must be the same one across the whole benchmark. Agent: `@judge`.

1. Run `python scripts/bench_report.py --pending` in the terminal. It lists run files that have no matching `results/` JSON (filtered to the case if given), and warns about cases without `grading/checks.md`. Skip those cases and tell me which ones need `/bench-feedback` first.
2. For each pending run, in order: read `cases/<case>/grading/checks.md`, then the run file, grade per the judge rules, write the results JSON. One run at a time; do not let one run's verdicts leak into the next.
3. When done, run `python scripts/bench_report.py` and reply with its summary line plus: "Open `index.html`."
