# Upgrades

`VERSION` at the repo root says which scaffold version you're on. Each upgrade note here is `<from>-to-<to>.md` with a matching `upgrade-<from>-to-<to>.patch` for the scaffold files (apply with `git apply`), and a Copilot prompt for any script changes. Apply them in order; never skip one. Current: 0.4-to-0.7 (no patch file — overwrite `.github/` and `docs/`).

Rule for future changes: scaffold files (docs, .github, templates) ship as a patch; D2P's OOXML/ingest scripts are never shipped — they are described in docs/d2p/bootstrap.md §2 and regenerated or edited by Copilot from that spec. The knowledge-base and tracker scripts (`scripts/README.md`, "Shipped") are the exception: plain-text and tested, they ship as files.
