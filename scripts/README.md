# scripts/

Stdlib only. Every script has `--selftest`; `python scripts/selftest_all.py` runs them all.

Shipped: `append_tasks.py` (tasks.json → `tracker/actions.csv`, deduplicated; `--init` creates the tracker).

Built by Copilot on the corporate machine, because they need the corporate `.pptx` fixtures and the real transcript shape: `ooxml.py`, `new_engagement.py`, `ingest.py`, `validate.py`, `status.py`, `followup_agenda.py`, `inspect_components.py`, `skeletonize_deck.py`, `build_deck.py`, `storyboard.py`, `lint_deck.py`, `timing.py`. Specifications: `docs/bootstrap.md` §2; implementation prompts: §3.
