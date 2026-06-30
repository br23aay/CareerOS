"""
Department 13 — ORCHESTRATOR (the CEO agent)

Drives the blueprint workflow:
  Profile -> Jobs Collected -> Verified -> Ranked -> Resume -> Prepared
  -> Outreach drafted -> Tracked -> (Interview prep) -> Learning updated

Implemented as a plain Python pipeline — right-sized for one user on a laptop.
The LangGraph/Temporal version noted in README is a Phase-7 upgrade; doing it
later in LangGraph also turns "developing" agentic experience on your CV into
something real and demonstrable.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from core.base_agent import BaseAgent
from core import config, database, profile

from departments.job_intelligence.agents import (
    JobCollectorAgent, JobCleanerAgent, JobCategorizerAgent)
from departments.verification.agents import (
    GhostJobDetector, CompanyVerificationAgent)
from departments.resume.agents import (
    ResumeStrategyAgent, ResumeWriterAgent, ResumeValidatorAgent,
    PDFGeneratorAgent)
from departments.application.agents import BrowserAgent
from departments.resume_factory.tailor import ResumeFactory
from departments.tracking.agents import ApplicationTracker
from departments.learning.agents import SuccessPredictionAgent
from departments.analytics.agents import AnalyticsAgent

# matcher lives here to keep the scoring logic central
from departments.orchestrator.matcher import match

# Broader, single-concept terms return far more Adzuna results than long
# exact phrases. The matcher does the precision filtering afterwards, so cast
# a wide net here and let scoring/reject-rules sort it.
SEARCH_TERMS = [
    "machine learning engineer", "AI engineer", "data scientist",
    "python developer", "graduate software engineer", "ML engineer",
    "robotics engineer", "deep learning", "data analyst",
    "research engineer",
]


class Orchestrator(BaseAgent):
    name = "orchestrator.ceo"

    def __init__(self):
        super().__init__()
        self.collector = JobCollectorAgent()
        self.cleaner = JobCleanerAgent()
        self.categorizer = JobCategorizerAgent()
        self.ghost = GhostJobDetector()
        self.company_verify = CompanyVerificationAgent()
        self.strategy = ResumeStrategyAgent()
        self.writer = ResumeWriterAgent()
        self.validator = ResumeValidatorAgent()
        self.pdf = PDFGeneratorAgent()
        self.factory = ResumeFactory()
        self.browser = BrowserAgent()
        self.tracker = ApplicationTracker()
        self.predict = SuccessPredictionAgent()
        self.analytics = AnalyticsAgent()

    def run(self, where: str = "") -> dict:
        database.init_db()
        self.log.info(f"=== CareerOS run — {profile.NAME} ===")

        # 1. Collect -> clean -> store + score + verify
        raw = self.collector.run(SEARCH_TERMS, where=where)
        jobs = self.cleaner.run(raw)
        prepared = []

        s = database.get_session()
        for j in jobs:
            if s.query(database.Job).filter_by(
                    source=j["source"], source_id=j["source_id"]).first():
                continue
            verdict = match(j)
            ghost = self.ghost.run(j)
            company = self.company_verify.run(j.get("company", ""))
            category = self.categorizer.run(j)

            row = database.Job(
                source=j["source"], source_id=j["source_id"], title=j["title"],
                company=j["company"], location=j["location"],
                description=j["description"], salary_min=j["salary_min"],
                salary_max=j["salary_max"], url=j["url"], posted=j["posted"],
                category=category, score=verdict["score"],
                verdict=verdict["verdict"],
                reasons="\n".join(verdict["reasons"]),
                matched_skills=", ".join(verdict["matched_skills"]),
                recommended_cv=verdict["recommended_cv"],
                ghost_score=ghost["ghost_score"],
                company_verified=company["verified"])
            s.add(row); s.commit()

            # 2. For strong, non-ghost matches: prepare an application
            if verdict["verdict"] in ("apply", "flag", "consider") and \
                    ghost["ghost_score"] < 50:
                cover = self.writer.run(j)
                check = self.validator.run(cover)
                cover_path = self.pdf.run(row.id, j["company"], cover)
                # Fresh, ATS-safe resume tailored to THIS job's description.
                tailored = self.factory.build(j)
                row.recommended_cv = Path(tailored["docx"]).name
                s.commit()
                browser = self.browser.run(j, cv_path=tailored["docx"],
                                           cover_path=cover_path)
                self.tracker.run(row.id, "matched")
                pred = self.predict.run(j, verdict["score"])
                prepared.append({
                    "job_id": row.id, "title": j["title"],
                    "company": j["company"], "score": verdict["score"],
                    "verdict": verdict["verdict"], "ghost": ghost["ghost_score"],
                    "cv": Path(tailored["docx"]).name, "cover": cover_path,
                    "resume": tailored["docx"], "ats_covered": tailored["ats_covered"],
                    "validator": check, "predicted_fit": pred["predicted_fit"],
                    "browser_status": browser["status"], "url": j["url"]})
        s.close()

        self.log.info(f"Prepared {len(prepared)} applications "
                      f"(held at approval gate).")
        return {"prepared": prepared, "analytics": self.analytics.run()}
