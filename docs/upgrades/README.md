# Upgrades

`VERSION` at the repo root says which scaffold version you're on. Each upgrade note here is `<from>-to-<to>.md` with a matching `upgrade-<from>-to-<to>.patch` for the scaffold files (apply with `git apply`), and a Copilot prompt for any script changes. Patches apply in order, never skipping one; the manual upgrade below can jump several versions at once. Current: 0.10-to-0.11 (map only). Both `upgrade-0.9-to-0.10.patch` and `upgrade-0.10-to-0.11.patch` include pictures, so apply them with `--binary`. Easiest route: the manual upgrade below. The patches are there if you prefer to apply changes in place.

Rule for future changes: scaffold files (docs, .github, templates) ship as a patch; D2P's OOXML/ingest scripts are never shipped — they are described in docs/d2p/bootstrap.md §2 and regenerated or edited by Copilot from that spec. The scripts listed as "Shipped" in `scripts/README.md` are the exception: plain-text and tested, they ship as files.

## Manual upgrade: new ZIP + your own files

The simplest way to upgrade, with no patches: take the new version from the GitHub ZIP, then carry over what is yours from the old folder.

1. Old folder: commit everything, then `git tag pre-upgrade`. Close VS Code and rename the folder to `semiAgency-old`.
2. Unzip the GitHub ZIP (**Code → Download ZIP**) as `semiAgency`, at the same path.
3. Copy these from `semiAgency-old` into `semiAgency`. Everything else comes from the ZIP.

| Keep from the old version | Why |
|---|---|
| `.git/` (hidden folder) | your history; `git status` then shows what the upgrade changed |
| `engagements/` (all of it, including `CURRENT`) | your engagements |
| `brand/` (all of it) | `components.pptx`, `components.md` / `.json`, `examples/*.json`, your `voice.md` |
| `tracker/` (all of it) | `actions.csv`, your real tasks |
| `scripts/`: every file that is not in the new ZIP's `scripts/` | the scripts Copilot built on your machine: `ooxml.py`, `ingest.py`, `validate.py`, `status.py`, `followup_agenda.py`, `inspect_components.py`, `skeletonize_deck.py`, `build_deck.py`, `storyboard.py`, `lint_deck.py`, `timing.py`, and any other it added |
| `tests/fixtures/`: every file except `README.md` | test files created during setup |
| `.vscode/`, if you have it | your editor settings |
| `bench/cases/`, `bench/runs/`, `bench/results/`, only if you ran bench inside this folder | your benchmark cases and results |

4. In `semiAgency`: `git status`.
   - **deleted:** something from the table you forgot to copy. Bring it back with `git checkout -- <path>`.
   - **modified:** the upgrade, or a local edit it replaced. Local edits to prompts, agents, instructions or READMEs are replaced by the public version; `git diff <path>` shows which, and you re-add your lines by hand.
   - **new:** new features.

   If almost every file shows as modified, it's Windows line endings: `git diff --ignore-cr-at-eol --stat` shows the real changes.
5. Read the note of every version you jumped over (`<from>-to-<to>.md` in this folder) and do only its script step, if it has one. Those are the kept scripts that must change; for 0.9 → 0.10, that is the `validate.py` prompt. Then run `python scripts/selftest_all.py` and `python scripts/build_city.py --check`.
6. Commit. `VERSION` came from the ZIP. Keep `semiAgency-old` for a week, then delete it.

**Rule for future versions:** every upgrade note says whether a kept script needs a change. If it says nothing, the steps above are the whole upgrade.
