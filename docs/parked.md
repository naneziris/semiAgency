# Parked — the other workflow candidates, and why they are not in this repo

Written 2026-09-15 after two build iterations. The handoff listed eight candidates; this repo keeps #1 (Discovery2Presentation) and #3 (meeting write-ups, the `meeting` kind). This page records what was tried for the rest so the reasoning isn't repeated.

## What was built and removed

- **Email triage (#2), morning brief (#7)** — first as a Microsoft 365 Agent Builder "exporter" whose output was pasted into a local knowledge base for GitHub Copilot to classify; then, when it was decided that email content must not reach local Copilot, as a single Agent Builder agent doing triage and brief in chat.
- **Topic news triage (#6)** — an interview prompt writing a per-topic interest profile, a daily digest prompt flagging links against it, and a feedback prompt refining the profile; links arrived by pasting a sanitized table from the M365 side.
- **Team 1-1s (#4)** — an Agent Builder agent meant to read OneNote 1-1 reports and produce the prep + agenda, with a Power Automate flow checking the invite's agenda the day before.
- **Knowledge base (#8)** — `kb/` with an ingest/route script, index generation, and a stdlib xlsx appender for a shared tracker.

## Why it came out

1. **Agent Builder cannot read OneNote in this tenant.** That kills #4 outright; the fallback (copy three OneNote pages into Copilot Chat) is not an improvement over reading them.
2. **Agent Builder cannot run itself and cannot write.** No schedule, no trigger, no To Do or calendar writes. So #2 and #7 reduce to "click a starter prompt each morning and read the answer" — which plain Copilot Chat in Work mode already does with a typed sentence. A custom agent added a fixed output format and nothing else.
3. **Email content must not reach local Copilot.** That removed the one thing the local side could have added to #2/#7: context from engagements, the tracker and past decisions. Without it, the local side was a paste target.
4. **The net effect was a longer routine, not automation.** Every "daily" workflow was a manual export, a paste, a script run and a prompt — more steps than the manual practice it replaced, and a workspace where the useful part (D2P) was hard to find.

## What would change the answer

- **Copilot Studio (paid, credit-metered).** Scheduled runs, event triggers, and actions (create To Do task, update event body). With it, #2/#7 become a brief that arrives at 07:00 and actions that land in To Do without a paste; #4 becomes automatic once OneNote is a supported knowledge source or the reports move to a SharePoint page library. The instruction texts written for Agent Builder would carry over unchanged.
- **OneNote as a knowledge source** in Agent Builder (or moving 1-1 reports to a OneDrive folder of `.md`/`.docx` files, which Agent Builder does index). #4 then works as designed: prep in chat, agenda pasted into the invite, Power Automate pinging when it's empty.
- **A policy that allows email-derived todos locally.** Then a To Do → CSV export (Power Automate, standard connector) could merge email actions into `tracker/actions.csv` and `status.py` could show one list.

## What #6 needs if you want it back

The interest-profile idea is sound; what it lacked was a cheap link source. If newsletters can be forwarded to a folder that a Power Automate flow dumps as a `.csv` of links into OneDrive synced to the corporate machine, the local `/interview-topic` → `/triage-topic` → `/refine-topic` prompts (in git history, v0.6.0) work unchanged with no paste. Without that, it's a paste a day for a digest you could get by asking Copilot Chat "what's new in AI in my newsletters this week".

## What replaced them

`m365/` — build sheets for the three cases that matter (daily brief, meeting filing + evening prep, email drafts) plus the 1-1 agenda check, designed around what runs unattended for free: scheduled prompts in Copilot Chat for the model step, standard Power Automate connectors for the filing, Agent Builder over a SharePoint library for on-demand work. Storing meeting material in SharePoint (not OneNote) is what makes the agent able to read it.

## Git history

`v0.5.0` — all eight candidates, local knowledge base, Agent Builder exporter. `v0.6.0` — M365-side triage/brief, sanitized links only. `v0.7.0` — D2P only, CSV tracker, runbooks. `v0.8.0` — adds `m365/` build sheets. `v0.9.0` — `new_engagement.py` ships and asks its questions, `engagements/CURRENT`, `docs/after-meeting.md`, fewer commands per step.
