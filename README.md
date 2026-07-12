# CareerOS

A local-first, multi-agent system that runs a UK AI/ML graduate job search end to end: collecting and cleaning listings, filtering out ghost jobs, ranking real matches, drafting tailored applications, and tracking outcomes — with a human required at every irreversible step.

[![CI](https://github.com/br23aay/CareerOS/actions/workflows/ci.yml/badge.svg)](https://github.com/br23aay/CareerOS/actions)

---

## Problem

Searching for a graduate AI/ML role in the UK means wading through job boards full of expired listings, "evergreen" ghost postings that never close, and roles that quietly require clearance, 3+ years' experience, or a PhD despite being labelled "graduate." Doing this by hand for dozens of roles a week, then hand-writing a tailored cover letter for each one, doesn't scale — but fully automating the *submission* step is both risky (it can get real accounts and IPs banned) and not something a serious candidate should want to auto-pilot.

## Solution

CareerOS automates everything up to the point of submission and stops there on purpose. Thirteen department modules each own one part of the pipeline — collection, cleaning, categorisation, ghost-job detection, matching against a candidate profile, resume/cover-letter drafting, salary-floor checking, outreach prep, interview prep, and outcome tracking — coordinated by a central orchestrator. Two flags in `core/config.py` are the only deliberate departures from full automation, and they're load-bearing, not decorative:

- `REQUIRE_HUMAN_APPROVAL = True` — the Application department prepares everything (opens the form, uploads the CV, fills the fields) but stops at submit. You click.
- `ALLOW_CAPTCHA_BYPASS = False` — CAPTCHA is detected and handed back to you, never auto-solved.

## Architecture

```
core/            config, profile (ground truth), database, base agent
departments/
  user_intelligence/   resume parser, career profile, skill gap
  job_intelligence/    collector (Adzuna), cleaner, categorizer
  verification/        ghost-job detector, company + recruiter verify
  resume/              ATS, strategy, writer, validator, PDF
  application/         form analysis, browser (gated), session, errors
  outreach/            discovery, verify, CRM, writer, channels, follow-up
  interview/           research, intelligence, resume-questions, guide
  salary/              compensation + floor protection
  tracking/            application tracker, Gmail monitor, calendar
  learning/            resume/outreach/source learning, success prediction
  analytics/           funnel + rates dashboard
  orchestrator/        the CEO agent + central matcher
```

Everything reads/writes through a local SQLite database — no external services required to run the pipeline end to end on mock data.

## Run

```bash
pip install -r requirements.txt
python main.py
python main.py --where "Hertfordshire"
```

Runs fully on mock data with no setup. For live job data, get free keys at [developer.adzuna.com](https://developer.adzuna.com/), then (PowerShell):

```powershell
$env:ADZUNA_APP_ID = "your_id"
$env:ADZUNA_APP_KEY = "your_key"
```

## What's Live vs Stubbed

**Live now:** collection, cleaning, categorisation, ghost detection, matching, resume strategy/writer/validator, salary, tracking transitions, learning rates, analytics, the full orchestrator pipeline.

**Interface stubs** (structured returns, marked `TODO Phase N`): company existence check (Companies House API), Playwright browser steps, Gmail monitor, contact discovery, web research. These have working signatures so nothing downstream breaks — filling in the real integration is the next step, not a claim that it's already done.

## Technology Choices

**SQLite + plain Python over the original Postgres/Redis/Celery/Next.js/Temporal blueprint** — that stack is built for a multi-user, always-on service; this is a single-user tool running on one laptop. Running the heavier stack here would fight the hardware for no real benefit. The scale-up path is explicit rather than pretended-away: swap `DB_URL` for Postgres and lift the orchestrator into LangGraph *if* this ever becomes multi-user.

**Rule-based matching and ghost detection over an LLM-judged pipeline** — reject rules (clearance required, seniority, years of experience, location, salary floor) and ghost-job signals (evergreen language, missing salary, staleness) are deterministic and explainable. Every verdict in the test suite asserts *why* a job was rejected or flagged, not just a black-box score.

**Human approval gate over full automation** — this is a product decision, not a technical limitation. Auto-submitting applications at scale risks account/IP bans and produces low-quality, unreviewed applications. The Application department does all the preparation work and stops one click before submission.

## Testing

`tests/test_careeros.py` is a dependency-free test suite (runs with plain `python`, no pytest required) that checks decision logic rather than just import success: the matcher's reject rules (clearance, seniority, experience, location, salary floor), scoring and flagging, the ghost-job detector's signal thresholds, salary floor protection, resume writer/validator honesty (the validator is checked to catch unfilled template hooks and overclaimed skills), the categorizer, and — importantly — that both safety gates (`REQUIRE_HUMAN_APPROVAL`, `ALLOW_CAPTCHA_BYPASS`) hold and that the browser agent never auto-submits.

## CI/CD

GitHub Actions installs dependencies and runs the full test suite on every push — see the [Actions tab](https://github.com/br23aay/CareerOS/actions). This is the first CI this repository has had; previously the tests existed but only ran locally.

## Security

No credentials are committed; Adzuna API keys are read from environment variables. The Gmail monitor integration is designed to reuse read-only OAuth rather than full mailbox access. The two safety gates described above exist specifically to prevent unsupervised actions against real third-party systems.

## Limitations

- **Commit history does not yet reflect incremental development.** This repository was pushed as a small number of large commits rather than the atomic, feature-by-feature history the rest of my repos use — the code was developed and tested locally first. Going forward, changes to this repo (like the CI workflow added here) follow one-change-per-commit.
- **Several departments are interface stubs**, not full implementations — see "What's Live vs Stubbed" above. The signatures are real; the integrations behind them (Companies House, Playwright, Gmail OAuth) are not yet wired up.
- **Designed for a single user on a single machine.** It is explicitly not built for concurrent multi-user use in its current form.

## Roadmap

1. Profile, parsing, DB, dashboard
2. Collection, verification, matching
3. Resume factory, ATS
4. Application prep, tracking, Gmail monitor
5. Outreach, CRM
6. Interview + salary intelligence
7. Learning loop, analytics, self-improvement (LangGraph orchestrator)

## Author

**Bharadwaj Rachuri**
[br23aay.github.io](https://br23aay.github.io) · [GitHub](https://github.com/br23aay)
