---
mode: agent
description: Write the one-page morning brief from the collected inputs — workflow #7
---
Date: `${input:date}` (default today). Use `@librarian`.
1. Run `python scripts/brief_collect.py --date ${input:date}` in the terminal and read `kb/briefs/${input:date}.inputs.md`. If it reports warnings, keep them for section 5.
2. For each 1-1 today, read the KB file it points at. For each engagement waiting at a gate, read nothing more — the gate name is enough.
3. Write `kb/briefs/${input:date}.md` per `.github/instructions/brief.instructions.md`. The Top 3 is your judgement: deadlines and people waiting outrank everything; a gate on the most important engagement (D2P proposals) outranks routine tasks; a focus slot before a clash is worth pointing out. Say why in one clause each.
4. Stop. Print the Top 3 in the chat and list what inputs were missing (gate B1: the user decides whether to fetch them and re-run).
