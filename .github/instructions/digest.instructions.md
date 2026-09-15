---
applyTo: "kb/topics/*/digests/*.md"
---
# kb/topics/<topic>/digests/<date>.md schema — one day's triage of one topic
Header: `# <topic> — <date>` then `profile: kb/topics/<topic>/profile.md (updated <date>)` and `links: <n> seen, <k> flagged`.
1. `## Flagged` — numbered, most important first, max 7. Each: `1. **<title>** — <url>` then one line *why* naming the criteria (`C1, C4`) and one line *what to do* (read / forward to <person> / try / note for <engagement>). Nothing here without a criterion.
2. `## Worth a glance` — bullets, max 10, one line each with the url; items that match a normal-weight criterion or a high-interest sub-area only partially.
3. `## Skipped` — a single table `| title | url | matched skip rule |` for everything else. Every link from the day's `links/<date>.md` appears exactly once in this file.
4. `## Feedback` — literally: `Reply with 👍/👎 and the item number, or "why not <title>", then run /refine-topic topic=<topic> date=<date>.`
Rules: judge only from title, one-line summary and source in the links file; never fetch or assume content. If two links are the same story, flag once and list the other under it. Under 500 words.
