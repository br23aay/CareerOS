# CareerOS

A local-first AI Career Operating System. Finds UK graduate AI/ML roles,
verifies them, ranks them against your profile, drafts tailored applications,
prepares outreach and interview material, tracks outcomes, and learns over time.

Built to run on one Windows laptop, at zero cost.

## The 13 departments

```
core/                         config, profile (ground truth), database, base agent
departments/
  user_intelligence/          resume parser, career profile, skill gap
  job_intelligence/           collector (Adzuna), cleaner, categorizer
  verification/               ghost-job detector, company + recruiter verify
  resume/                     ATS, strategy, writer, validator, PDF
  application/                form analysis, browser (gated), session, errors
  outreach/                   discovery, verify, CRM, writer, channels, follow-up
  interview/                  research, intelligence, resume-questions, guide
  salary/                     compensation + floor protection
  tracking/                   application tracker, Gmail monitor, calendar
  learning/                   resume/outreach/source learning, success prediction
  analytics/                  funnel + rates dashboard
  orchestrator/               the CEO agent + central matcher
```

## Run

```bash
pip install -r requirements.txt
python main.py
python main.py --where "Hertfordshire"
```

Runs fully on mock data with no setup. For live jobs, free keys at
https://developer.adzuna.com/ then (PowerShell):

```powershell
$env:ADZUNA_APP_ID  = "your_id"
$env:ADZUNA_APP_KEY = "your_key"
```

## Two deliberate safety limits

These are the only two places the build departs from the blueprint, and the
flags live in `core/config.py`:

- `REQUIRE_HUMAN_APPROVAL = True` — the Application department *prepares*
  everything (opens, uploads, fills) but stops at submit. You click. Auto-blasting
  applications violates most platforms' terms and gets real accounts/IPs banned
  mid-search.
- `ALLOW_CAPTCHA_BYPASS = False` — CAPTCHA is detected and handed back to you,
  never auto-solved.

Everything else is built exactly as specified.

## What's live vs stubbed

Live now: collection, cleaning, categorisation, ghost detection, matching,
resume strategy/writer/validator, salary, tracking transitions, learning rates,
analytics, the full orchestrator pipeline.

Interface stubs (structured returns, marked `TODO Phase N`): company existence
check (Companies House API), Playwright browser steps, Gmail monitor (reuse
Tony's read-only OAuth), contact discovery, web research. These have working
signatures so nothing downstream breaks — you fill the integration.

## Scale-up path (only if this ever becomes multi-user)

The blueprint's Postgres + pgvector + Redis + Celery + Next.js + Temporal stack
is overkill for one user on a laptop and would fight your hardware. SQLite +
plain Python + (later) Streamlit do everything at this scale. Swap the
`DB_URL` for Postgres and lift the orchestrator into LangGraph when, and only
when, you outgrow this. Doing the LangGraph version later also turns "agentic /
LangGraph (developing)" on your CV into real, demonstrable experience.

## Roadmap (your phases, intact)

1. Profile, parsing, DB, dashboard
2. Collection, verification, matching
3. Resume factory, ATS
4. Application prep, tracking, Gmail monitor
5. Outreach, CRM
6. Interview + salary intelligence
7. Learning loop, analytics, self-improvement (LangGraph orchestrator)
```
```
