# scripts/

Stdlib only. Every script has `--selftest`; `python scripts/selftest_all.py` runs them all. Every script that works on an engagement takes its dir as an optional argument and otherwise uses the name in `engagements/CURRENT`.

Shipped:
- `new_engagement.py` — run with no arguments after a meeting: asks kind, subject, name, stakeholders, audience, minutes; creates the folder and `state.json`; sets `engagements/CURRENT`; waits while you fill `inputs/`, lists what it found, prints the first Copilot prompt. `--check` re-runs the inputs check, `--use <name>` switches the current engagement, `--kind/--name/…` and `--no-wait` for scripting.
- `append_tasks.py` — reviewed `tasks.json` → `tracker/actions.csv`, deduplicated; shows the rows, then offers to pass gate G5 (`--pass-g5` to skip the question; `--init` creates the tracker).

Built by Copilot on the corporate machine, because they need the corporate `.pptx` fixtures and the real transcript shape: `ooxml.py`, `ingest.py`, `validate.py`, `status.py` (`--pass` with no gate passes the next one, interactively), `followup_agenda.py`, `inspect_components.py`, `skeletonize_deck.py`, `build_deck.py` (lints after building; `--notes-only` runs the timing check first), `storyboard.py`, `lint_deck.py`, `timing.py`. Specifications: `docs/bootstrap.md` §2; implementation prompts: §3.
