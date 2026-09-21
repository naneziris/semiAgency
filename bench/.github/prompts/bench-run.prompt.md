---
mode: agent
description: "Do one bench case with the currently selected model and save the output to runs/"
---
Case: `${input:case}`. Model id currently selected in the picker (I typed it, you cannot know it): `${input:model}`.
If either is empty, stop and ask for it; the model id is what the report groups by, so it must be exact and consistent across runs (e.g. `claude-sonnet-4.5`, not "Sonnet").

1. Run `python scripts/bench_new_run.py ${input:case} ${input:model}` in the terminal. It prints the path of a new run file with its header already written. Use exactly that path.
2. Read `cases/${input:case}/task/prompt.md` and `cases/${input:case}/task/notes.md`, and the files in `cases/${input:case}/task/context/` that the prompt refers to. Read **nothing else** in the repo: not `grading/`, not `results/`, not other files under `runs/`.
3. Do the task, exactly as if `prompt.md` were a message from a user who gave you `notes.md` as background. Do your best work; do not mention the benchmark in the output.
4. Append your complete answer below the header of the run file. If the task produces files (a deck, a script, a dashboard), create them in a folder next to the run file with the same stem (`runs/<case>/<stem>/`) and list them at the end of the run file.
5. Reply with one line: the run file path. Nothing else — no self-assessment.
