# bench — repo conventions

This workspace is a personal model benchmark. It is kept deliberately small so that it does not steer the models being tested.

- When a prompt asks you to *do a task* (`/bench-run`), read only `cases/<case>/task/`. Never open `cases/<case>/grading/`, `results/` or other models' files under `runs/` while doing a task. Do the task as you would for a real user; the run file header is the only bench-specific thing you add.
- When a prompt asks you to *grade* (`/bench-judge`, `@judge`), you read `grading/checks.md` and one run file at a time, and you never edit the run file.
- Scripts are Python 3 standard library only. Never install or suggest packages.
- Do not modify anything under `cases/*/task/context/` — those are the user's real files.
- File naming for runs: `runs/<case>/<model>__<YYYYMMDD-HHMM>__r<n>.md`, always created via `python scripts/bench_new_run.py <case> <model>`; never invent the path yourself.
