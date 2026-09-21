# bench — your personal model benchmark for GitHub Copilot

Public benchmarks tell you which model wins at maths olympiads. They do not tell you which model in the Copilot picker is good at *your* work. This kit gives you that answer in about two hours, and keeps giving it every time a new model appears in the picker.

The idea (from Every's "How to create your own personal AI benchmark"): collect the tasks where AI recently failed you, run each one on several models, turn your reactions into pass/fail checks, let a judge model apply the checks, look at a side-by-side page. No scores out of 100 — a model either passes your checks or it does not.

**Copy this folder into an empty workspace.** Do not run it inside another project: whatever `copilot-instructions.md` that project has would colour every run and you would be benchmarking your instructions, not the model.

```
bench/
├── README.md                      this page
├── .github/
│   ├── copilot-instructions.md    deliberately minimal — the bench must not steer the model
│   ├── prompts/                   /bench-setup  /bench-run  /bench-feedback  /bench-judge
│   └── agents/judge.agent.md      read-only grader
├── cases/<case>/
│   ├── task/prompt.md             what you ask, exactly as you would in real life
│   ├── task/context/              files the task needs (the brief, the data, the deck to fix)
│   ├── task/notes.md              what you would tell an intern before handing it over
│   └── grading/checks.md          3–10 pass/fail checks in your words (written after you have seen outputs)
│       grading/gold/              optional: the result you were happy with, for comparison
├── runs/<case>/<model>__<date>__r<n>.md      one file per model output
├── results/<case>/<same stem>.json           the judge's verdicts
├── models.txt                     model ids for the CLI runner (see `/model` in Copilot CLI)
├── scripts/                       Python 3 standard library only
└── index.html                     generated: the matrix and the side-by-side view
```

## The loop

| step | what you do | tool |
|---|---|---|
| 1. collect | `/bench-setup` interviews you for 5–10 tasks where AI got it wrong recently and files them under `cases/` | Copilot Chat, agent mode |
| 2. run | pick a model in the picker → `/bench-run case=<name> model=<id>` → the output lands in `runs/`. Change the model, run again. Three models × all cases is ~30 invocations; do it once with coffee. | Copilot Chat |
| 2'. run (fast) | `python scripts/bench_cli.py --models claude-sonnet-4.5,gpt-5.4 --repeat 3` runs every case on every model through the Copilot CLI | terminal, needs `copilot` installed |
| 3. react | `/bench-feedback case=<name>` shows you two outputs side by side, you say what you liked and hated in plain words, it writes `grading/checks.md` | Copilot Chat |
| 4. grade | select the **judge model** (the same one every time) → `/bench-judge` grades every ungraded run; or `python scripts/bench_cli.py --judge --judge-model <id>` | Copilot Chat or terminal |
| 5. look | `python scripts/bench_report.py` → open `index.html` | terminal |

Then, whenever a new model appears in the picker: step 2 for that model only, step 4, step 5. Ten minutes.

## Rules that make the numbers mean something

- **Tasks come from failures**, not from things your daily driver already does well. A task every model passes tells you nothing ("if all you have are easy problems, a smarter model has no room to pull ahead").
- **Binary checks, 3–10 per case.** Never ask a model for a rating; it will say 7/10 to everything. "Does the title state the finding rather than the topic? PASS/FAIL" is a check. "Rate the title" is not.
- **One judge model for the whole benchmark**, recorded in every result. Judges favour their own family's writing; switching judges between runs makes results incomparable. A cheap model judges fine when the checks are concrete.
- **Run each case three times** before believing a difference. One output is a coin toss.
- **Compare across providers and across sizes** (big vs small of the same family). The interesting finding is usually "the cheap one is good enough for cases 1–6".
- **Contamination:** the model doing the task must never see `grading/`. `/bench-run` reads `task/` only; the CLI runner passes only `task/`. Do not paste checks into a run prompt.
- **It expires.** When every model passes every check, the benchmark is saturated: make the tasks harder or replace them (`/bench-setup` again). Note the date in `cases/<case>/task/notes.md` when you retire one.

## What it costs

Every run is one Copilot request (premium requests for premium models, per your plan). 10 cases × 3 models × 3 repeats = 90 requests plus 90 judge calls. Use a cheap judge and start with 1 repeat to find the cases that matter; add repeats there only.

## Where it does not reach

- The Copilot picker in VS Code is what you can test; nothing here calls model APIs directly. Model ids: `/model` in an interactive `copilot` session.
- Tasks that need tools the CLI does not have (your corporate PowerPoint template, an internal system) run in chat mode only.
- Microsoft 365 Copilot agents are chat-only and cannot be scripted; grade those by hand with the same `checks.md` discipline, do not pretend it is a benchmark.
