"""
Department 5 — RESUME
  ATSAnalysisAgent   — required keywords from a JD
  ResumeStrategyAgent — what to emphasise / what to leave out
  ResumeWriterAgent  — pick CV variant + draft cover letter (honest)
  ResumeValidatorAgent — truthfulness / ATS / formatting checks
  PDFGeneratorAgent  — write resume_company.pdf
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from core.base_agent import BaseAgent
from core import config, profile


class ATSAnalysisAgent(BaseAgent):
    name = "resume.ats"

    def run(self, job_description: str) -> dict:
        text = job_description.lower()
        present = [s for s in profile.SKILLS if s in text]
        return {"required_keywords": present,
                "count": len(present)}


class ResumeStrategyAgent(BaseAgent):
    name = "resume.strategy"

    def run(self, job: dict) -> dict:
        text = f"{job.get('title','')} {job.get('description','')}".lower()
        emphasise = [s for s in profile.SKILLS if s in text][:6]
        # Honest: only flag developing skills, never instruct to fake them.
        downplay = [d for d in profile.DEVELOPING if d in text]
        return {"emphasise": emphasise,
                "developing_to_acknowledge": downplay,
                "cv_variant": profile.recommend_cv(
                    job.get("title", ""), job.get("description", ""))}


COVER_TEMPLATE = """\
Dear Hiring Team,

I am applying for the {title} role at {company}. {hook}

During my MSc in Artificial Intelligence and Robotics (Commendation,
University of Hertfordshire), I published peer-reviewed research in IJRES on
PPO-based dexterous in-hand manipulation with the Shadow Hand, achieving a
175-degree rotation (97.2% of target) over 70,000+ timesteps. {skills_line}

I hold a Graduate Visa with full right to work in the UK and am available
immediately.

Kind regards,
{name}
"""


class ResumeWriterAgent(BaseAgent):
    name = "resume.writer"

    def run(self, job: dict) -> str:
        text = f"{job.get('title','')} {job.get('description','')}".lower()
        matched = [s for s in profile.SKILLS if s in text]
        skills_line = ("My most relevant strengths here include "
                       + ", ".join(matched[:5]) + "." if matched else
                       "I would welcome the chance to discuss the fit.")
        return COVER_TEMPLATE.format(
            title=job.get("title", "the role"),
            company=job.get("company", "your company"),
            hook="[REVIEW: one honest, specific sentence on why this company.]",
            skills_line=skills_line, name=profile.NAME)


class ResumeValidatorAgent(BaseAgent):
    name = "resume.validator"

    def run(self, cover_text: str) -> dict:
        issues = []
        if "[REVIEW" in cover_text:
            issues.append("hook placeholder not yet filled in by you")
        # truthfulness guard: warn if a developing skill is claimed outright
        for d in profile.DEVELOPING:
            if f"experienced in {d}" in cover_text.lower() or \
               f"expert in {d}" in cover_text.lower():
                issues.append(f"overclaim risk on developing skill: {d}")
        return {"passed": not issues, "issues": issues}


class PDFGeneratorAgent(BaseAgent):
    name = "resume.pdf"

    def run(self, job_db_id: int, company: str, cover_text: str) -> str:
        safe = "".join(c for c in (company or "company")
                       if c.isalnum() or c in " -_").strip().replace(" ", "_")
        # Saved as .txt now; Phase 2 renders .pdf (reportlab) — interface fixed.
        path = config.COVERLETTERS / f"cover_{job_db_id}_{safe}.txt"
        path.write_text(cover_text, encoding="utf-8")
        self.log.info(f"Wrote {path.name}")
        return str(path)
