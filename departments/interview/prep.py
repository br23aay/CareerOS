"""
departments/interview/prep.py — research-backed interview preparation.

For a given applied job it pulls together:
  - live company research (what they do, recent news) via the research dept
  - role/interview-process signal from the web
  - WHICH resume you actually used for that job (from the application record)
  - your CV-derived likely questions + core story

So prep is grounded in the real company and the exact CV you sent — not
generic advice.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from core.base_agent import BaseAgent
from core import database
from departments.research.web_research import ResearchAgent
from departments.interview.agents import (InterviewIntelligenceAgent,
                                          ResumeQuestionAgent)


class InterviewPrep(BaseAgent):
    name = "interview.prep"

    def __init__(self):
        super().__init__()
        self.research = ResearchAgent()
        self.intel = InterviewIntelligenceAgent()
        self.questions = ResumeQuestionAgent()

    def build(self, job_id: int) -> dict:
        s = database.get_session()
        job = s.query(database.Job).get(job_id)
        app = s.query(database.Application).filter_by(job_id=job_id).first()
        s.close()
        if not job:
            return {"error": f"no job {job_id}"}

        resume_used = (app.cv_used if app and app.cv_used
                       else "(no resume recorded for this job)")

        company_info = self.research.company(job.company)
        role_info = self.research.role(job.title, job.company)
        intel = self.intel.run({"title": job.title,
                                "description": job.description or ""})

        return {
            "company": job.company,
            "role": job.title,
            "resume_used": resume_used,
            "company_overview": company_info.get("overview", ""),
            "company_from_site": company_info.get("from_site", ""),
            "company_sources": company_info.get("sources", []),
            "interview_signal": role_info.get("interview_signal", ""),
            "likely_rounds": intel["likely_rounds"],
            "technical_topics": intel["technical_topics"],
            "behavioural": intel["behavioural"],
            "cv_questions": self.questions.run(),
            "core_story": ("Shadow Hand PPO research — problem -> approach -> "
                           "results (175 deg, >90% sensor accuracy) -> impact."),
        }
