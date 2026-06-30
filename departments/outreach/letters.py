"""departments/outreach/letters.py — research-backed drafts. Drafts only; you send."""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from core import master_cv as M
from departments.research.web_research import ResearchAgent

_research = ResearchAgent()


def _opening_line(company: str) -> str:
    info = _research.company(company)
    text = (info.get("overview", "") + " " + info.get("from_site", "")).strip()
    if not text or "no company" in text:
        return f"I've been following {company} and am drawn to the work your team is doing."
    sentence = text.split(". ")[0]
    if len(sentence) > 200:
        sentence = sentence[:197] + "..."
    return f"I was particularly interested to read that {sentence.strip().rstrip('.')}."


def cover_letter(job: dict, suggested_line: str | None = None) -> str:
    c = M.CONTACT
    company = job.get("company", "your company")
    title = job.get("title", "the role")
    desc = (job.get("description", "") or "").lower()
    proj = M.PROJECTS[1] if any(k in desc for k in ("llm", "rag", "prompt", "language")) else M.PROJECTS[0]
    opener = suggested_line or _opening_line(company)
    return f"""Dear Hiring Team,

I am writing to apply for the {title} position at {company}. {opener}

I hold an MSc in Artificial Intelligence and Robotics (Commendation) from the University of Hertfordshire and have peer-reviewed research published in IJRES (Impact Factor 7.52). In my {proj['title']} work, {proj['points'][0].lower()} — {proj['points'][1].lower()}. Alongside this I have built RAG pipelines and LLM workflows using Azure AI Foundry, and completed 49 Microsoft Learn AI certifications.

I am confident my combination of published research, hands-on Python and ML engineering, and practical Azure experience would let me contribute quickly at {company}.

I hold a UK Graduate Visa with full right to work until September 2027 and require no sponsorship. I am available immediately.

Kind regards,
{c['name'].title()}
{c['email']} | {c['portfolio']}"""


def referral_email(contact_name: str, job: dict, linkedin: str = "") -> dict:
    company = job.get("company", "the company")
    title = job.get("title", "the role")
    person = _research.person(contact_name, linkedin, company)
    comp = _research.company(company)
    comp_text = (comp.get("overview", "") or comp.get("from_site", "")).strip()
    comp_hook = ""
    if comp_text and "no company" not in comp_text:
        first = comp_text.split(". ")[0]
        comp_hook = f" I've been following {company}'s work — {first.strip().rstrip('.')}. "
    person_note = " I came across your profile while researching the team." if person.get("public_summary") else ""
    body = f"""Subject: {title} at {company} — a quick introduction

Hi {contact_name or 'there'},

I hope you don't mind me reaching out.{person_note} I'm applying for the {title} role at {company}.{comp_hook}

I'm an MSc AI & Robotics graduate with peer-reviewed research on PPO-based Shadow Hand manipulation (IJRES, IF 7.52), strong Python/PyTorch skills, and hands-on RAG and Azure AI experience. I hold a UK Graduate Visa — no sponsorship needed.

If you're open to it, I'd value any insight into the team, or a referral if you think I'd be a fit. My portfolio is at br23aay.github.io.

Thank you for your time,
Bharadwaj Rachuri"""
    return {"email": body, "research_used": {
        "company_sources": comp.get("sources", []),
        "person_sources": person.get("sources", []),
        "company_found": bool(comp_text and "no company" not in comp_text),
        "person_found": bool(person.get("public_summary"))}}
