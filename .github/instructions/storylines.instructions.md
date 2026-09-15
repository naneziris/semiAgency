---
applyTo: "engagements/**/storylines.md"
---
# storylines.md schema
Exactly TWO storylines, `## S1 — <name>` and `## S2 — <name>`. They tell the SAME content (the option chosen at G2 for proposals; the key messages in content.md for decks) in different ways — e.g. problem-first vs. vision-first, decision-first vs. journey, stakeholder-pain-led vs. outcome-led. They must NOT differ in what is proposed.
Each storyline has, in order:
- `**Thesis**` — the one sentence the audience should repeat afterwards
- `**Arc**` — 3–5 beats in prose (what the audience feels/learns at each beat)
- `**Slide outline**` — table `| # | kind | title | refs | source |` using only kinds from `brand/components.md`, with the ask on its own slide. `source` is `clone <file>#<n>` (existing slide reused verbatim), `rewrite <file>#<n>` (existing slide whose content must be re-expressed for this audience), or `new`.
- `**Translation**` (optional; include when the user asks for a re-targeted narrative) — table `| technical point | how we say it for this audience |`.
- `**Works well because**` (max 3 bullets, specific to THIS audience from deck meta / proposal)
- `**Risks**` (max 3 bullets: where this telling can lose them)
- `**Coverage**` — list of every H-priority N id (proposal) or every K id (deck) and the slide # that carries it (all must be present)
Then `## Comparison` — one table, S1/S2 as columns; rows: opening, where the ask lands, time to first "why should I care", strongest slide, biggest risk, fit to audience.
Then `## Recommendation` — which storyline and 3 lines why. The user decides (gate G3); do not build anything.
