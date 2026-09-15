---
mode: agent
description: Interview me about a topic and write its interest profile — workflow #6, one-time per topic
---
Topic: `${input:topic}` (slug, e.g. `ai`). Use `@interviewer`.
1. If `kb/topics/${input:topic}/profile.md` exists, stop and say so: use `/refine-topic` instead.
2. If `kb/topics/${input:topic}/links/` has files, read the newest one first — use 3–5 real links from it as examples during the interview ("would you want this flagged? why?").
3. Run the interview per your agent instructions: one question at a time, 8–12 questions, reflect candidate lines back before writing.
4. Write `kb/topics/${input:topic}/profile.md` per `.github/instructions/profile.instructions.md`. Set `interviewed:` and `last updated:` to today.
5. Stop. Show the profile and tell the user the daily step is `/triage-topic topic=${input:topic}`.
