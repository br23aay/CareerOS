"""
Department 2 — USER INTELLIGENCE
  ResumeParserAgent  — extract skills/experience/education from a CV
  CareerProfileAgent — build the structured profile
  SkillGapAgent      — current vs missing vs market skills
"""

import re
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from core.base_agent import BaseAgent
from core import profile


class ResumeParserAgent(BaseAgent):
    name = "user.resume_parser"

    def run(self, cv_text: str) -> dict:
        """Lightweight extraction. For .docx/.pdf, feed in extracted text."""
        text = cv_text.lower()
        skills = [s for s in profile.SKILLS if s in text]
        self.log.info(f"Parsed {len(skills)} known skills from CV.")
        return {
            "skills": skills,
            "has_publication": "ijres" in text or "shadow hand" in text,
            "education": re.findall(r"(msc|b\.?tech|bachelor|master)[^\n]{0,60}",
                                    text),
        }


class CareerProfileAgent(BaseAgent):
    name = "user.career_profile"

    def run(self) -> dict:
        return {
            "experience": "MSc AI & Robotics + published IJRES research",
            "minimum_salary": profile.MINIMUM_SALARY,
            "target_salary": profile.TARGET_SALARY,
            "locations": ["UK"],
            "roles": ["Graduate AI Engineer", "Junior ML Engineer",
                      "Graduate Robotics Engineer"],
            "visa": profile.VISA,
        }


class SkillGapAgent(BaseAgent):
    name = "user.skill_gap"

    def run(self, job_description: str) -> dict:
        text = job_description.lower()
        have = [s for s in profile.SKILLS if s in text]
        gaps = [d for d in profile.DEVELOPING if d in text]
        return {"current_skills": have, "missing_skills": gaps,
                "note": "missing = developing; never claim as production"}
