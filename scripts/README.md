# scripts/

Stdlib only. Every script has `--selftest`. `python scripts/selftest_all.py` runs them all.

**Shipped (ready to run):** the knowledge-base and tracker scripts — plain text and a deliberately tiny xlsx appender, tested outside the corporate machine.

| script | does |
|---|---|
| `xlsxlite.py` | create / read / append a one-sheet .xlsx (helper, no CLI use beyond `--dump`) |
| `tracker_init.py` | create `tracker/actions.xlsx` with the fixed columns (run once) |
| `append_tasks.py` | reviewed `tasks.json` (of an engagement, or any tasks file) → tracker, deduplicated; lock → `tasks.pending.csv` |
| `kb_ingest.py` | `kb/inbox/*` handoffs (topic-links, meeting, note) → routed into `kb/`; refuses email/calendar/1-1 content (docs/handoff-format.md) |
| `kb_index.py` | rebuild `kb/index.md` and `kb/topics/<t>/links.md` |

**Built by Copilot on the corporate machine** (they need the corporate `.pptx` fixtures and the real transcript shape): the D2P scripts — `ooxml.py`, `new_engagement.py`, `ingest.py`, `validate.py`, `status.py`, `followup_agenda.py`, `inspect_components.py`, `skeletonize_deck.py`, `build_deck.py`, `storyboard.py`, `lint_deck.py`, `timing.py`. Specifications: `docs/d2p/bootstrap.md` §2; implementation prompts: §3. Note Phase 5 there is now "verify" rather than "build", because `append_tasks.py` ships.
