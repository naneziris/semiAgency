---
mode: agent
description: "Show me two outputs of a case side by side, take my reactions, turn them into pass/fail checks"
---
Case: `${input:case}` (if empty, list the folders under `cases/` that have runs but no `grading/checks.md` yet, and ask which one).

1. List the run files in `runs/${input:case}/`. If fewer than two, stop and say which `/bench-run` to do first. Otherwise pick two from **different models** (the most recent per model) and show them to me side by side: a two-column markdown table is fine for short outputs; for long ones, show each in full one after the other with the model name as heading. Do not comment on them.
2. Ask me, one question at a time, waiting each time:
   - "What did you like in either one? Be specific — quote if you can."
   - "What annoyed you? What would you have had to fix before sending it?"
   - "Which would you send, and what is the single thing that decided it?"
   - "Anything a good version must always contain, or must never contain?"
   Keep asking "anything else?" until I say no. The more opinions the better; my taste is the product here.
3. Turn what I said into `cases/${input:case}/grading/checks.md` in the format of `cases/_example/grading/checks.md`: header, one judge instruction line, then 3–10 checks `- C<n>: <one sentence a stranger could verify by reading the output>`. Rules:
   - Every check is answerable PASS/FAIL from the output alone (plus `task/context/` and `task/notes.md` if a fact must be verified). No "is it good", no scales.
   - Keep my words where they are precise ("buried the ask in paragraph four" → "The decision appears in the first sentence").
   - If `grading/checks.md` already exists, merge: keep existing ids, add new ones, mark checks I now contradict as `~~C3~~ (retired <month>)`.
   - Prefer checks that would have separated the two outputs I just saw. A check both pass and both would always pass is filler; say so and leave it out.
4. Show me the file and ask for corrections. Then end with: "Next: select your judge model in the picker and run `/bench-judge judge_model=<id>`. Use the same judge model every time."
