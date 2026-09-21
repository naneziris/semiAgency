# Upgrades

`VERSION` at the repo root says which scaffold version you're on. Each upgrade note here is `<from>-to-<to>.md` with a matching `upgrade-<from>-to-<to>.patch` for the scaffold files (apply with `git apply`), and a Copilot prompt for any script changes. Apply them in order; never skip one. Current: 0.9-to-0.10 (no patch file — copy `bench/` and the README section).

Rule for future changes: scaffold files (docs, .github, templates) ship as a patch; D2P's OOXML/ingest scripts are never shipped — they are described in docs/d2p/bootstrap.md §2 and regenerated or edited by Copilot from that spec. The scripts listed as "Shipped" in `scripts/README.md` are the exception: plain-text and tested, they ship as files.
