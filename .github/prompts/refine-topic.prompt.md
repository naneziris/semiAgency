---
mode: agent
description: Apply my 👍/👎 feedback on a digest to the topic's interest profile — workflow #6
---
Topic: `${input:topic}`. Digest date: `${input:date}`. Feedback: `${input:feedback}` (e.g. `👍 2, 👎 1, why not "Agent eval harness"`). Use `@librarian`.
1. Read `kb/topics/${input:topic}/profile.md` and `kb/topics/${input:topic}/digests/${input:date}.md`.
2. For each piece of feedback, identify the item and the criterion that fired (or should have). Propose the smallest profile change that would have produced the user's verdict: sharpen a criterion, add a skip rule, adjust a sub-area or source trust, or add the item to `## Examples`. Show the proposed diff as a list and ask for confirmation before editing. One question, then wait.
3. On confirmation, edit `profile.md` in place: never delete a criterion (mark `(retired <date>)`), append one row per change to `## Feedback log`, bump `last updated:`.
4. Stop. Say what changed and what will be judged differently tomorrow.
