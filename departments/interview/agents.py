"""
Department 8 — INTERVIEW (activated when an interview is detected)
  ResearchAgent            — company website/products/news/leadership
  InterviewIntelligenceAgent — process/rounds/expected questions
  ResumeQuestionAgent      — questions generated from your own CV
  InterviewGuideGenerator  — Company_Report + Interview_Guide files
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from core.base_agent import BaseAgent
from core import config, profile


class ResearchAgent(BaseAgent):
    name = "interview.research"

    def run(self, company: str) -> dict:
        # TODO Phase 6: fetch official site + public articles (web_fetch style).
        return {"company": company,
                "sections": ["products", "news", "competitors",
                             "leadership", "tech_stack"],
                "note": "interface stub — wire permitted web research"}


class InterviewIntelligenceAgent(BaseAgent):
    name = "interview.intelligence"

    def run(self, job: dict) -> dict:
        return {"likely_rounds": ["recruiter screen", "technical",
                                  "behavioural", "final"],
                "technical_topics": ["PPO / RL fundamentals", "MuJoCo & "
                                     "sim-to-real", "PyTorch training loop",
                                     "RAG pipelines", "reward hacking"],
                "behavioural": ["why this company", "a hard bug you solved",
                                "working under deadline"]}


class ResumeQuestionAgent(BaseAgent):
    name = "interview.resume_questions"

    def run(self) -> list[str]:
        return [
            "Walk me through your IJRES Shadow Hand PPO research end to end.",
            "How did you mitigate reward hacking in the manipulation task?",
            "Explain PPO to a non-specialist.",
            "Tell me about the Swayam ML/AI work and what you delivered.",
            "What was the hardest debugging problem in your projects?",
        ]


class InterviewGuideGenerator(BaseAgent):
    name = "interview.guide"

    def run(self, job: dict) -> dict:
        company = job.get("company", "company")
        safe = company.replace(" ", "_")
        report = config.INTERVIEWS / f"Company_Report_{safe}.txt"
        guide = config.INTERVIEWS / f"Interview_Guide_{safe}.txt"
        report.write_text(f"Company report — {company}\n(Research pending "
                          f"Phase 6 web integration.)\n", encoding="utf-8")
        guide.write_text(
            "Interview Guide\n\nCore story: Shadow Hand PPO research.\n"
            "Always ready: problem -> approach -> results -> impact.\n"
            f"Right to work: {profile.VISA}\n", encoding="utf-8")
        self.log.info(f"Wrote interview guide for {company}")
        return {"company_report": str(report), "guide": str(guide)}
