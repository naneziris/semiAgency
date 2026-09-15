---
mode: agent
description: Flag the day's links for a topic against my interest profile and write the digest — workflow #6, daily
---
Topic: `${input:topic}`. Date: `${input:date}` (default today). Use `@librarian`.
1. Read `kb/topics/${input:topic}/profile.md`. If missing, stop: `/interview-topic topic=${input:topic}` first.
2. Read `kb/topics/${input:topic}/links/${input:date}.md`. If missing, stop and say the Daily Brief agent's **Topic links** starter has not been run/ingested for that date. The file carries only url, title and one-line — that is all you get; never ask for the source email.
3. Read `kb/topics/${input:topic}/links.md` (all links ever) to spot repeats: an item already flagged on an earlier day is not flagged again — list it under Skipped with `matched skip rule = seen <date>`.
4. Judge every link only from its title, one-line summary and source, against the criteria `C…`, skip rules `X…`, sub-areas and source trust in the profile. Write `kb/topics/${input:topic}/digests/${input:date}.md` per `.github/instructions/digest.instructions.md`.
5. Run `python scripts/kb_index.py`. Stop. Tell the user how many were flagged and which criterion fired most; remind them of the feedback line at the end of the digest (gate T2).
