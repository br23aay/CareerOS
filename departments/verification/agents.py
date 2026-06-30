"""
Department 4 — VERIFICATION (the highest-value department)
  GhostJobDetector         — score how likely a posting is fake/stale/farming
  CompanyVerificationAgent — does the company actually exist + hire?
  RecruiterVerificationAgent — trust score 0-100 for a recruiter
"""

import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from core.base_agent import BaseAgent


class GhostJobDetector(BaseAgent):
    name = "verify.ghost"

    # Phrases and patterns correlated with low-quality / ghost postings.
    RED_FLAGS = [
        "always hiring", "ongoing recruitment", "build a talent pool",
        "future opportunities", "no specific start date", "register your interest",
        "we are constantly looking", "evergreen",
    ]

    def run(self, job: dict) -> dict:
        """Return {ghost_score 0-100, signals[]}. Higher = more suspicious."""
        score, signals = 0, []
        text = f"{job.get('title','')} {job.get('description','')}".lower()

        # 1. Evergreen / talent-pool language
        for flag in self.RED_FLAGS:
            if flag in text:
                score += 20; signals.append(f"evergreen language: '{flag}'")

        # 2. Age of posting — stale reposts are a classic ghost signal
        posted = job.get("posted", "")
        try:
            dt = datetime.fromisoformat(posted.replace("Z", "+00:00"))
            age = (datetime.now(timezone.utc) - dt).days
            if age > 45:
                score += 25; signals.append(f"stale posting ({age} days old)")
            elif age > 30:
                score += 10; signals.append(f"ageing posting ({age} days old)")
        except Exception:
            pass

        # 3. Vague description (very short = low effort / placeholder)
        if len(job.get("description", "")) < 120:
            score += 15; signals.append("unusually short description")

        # 4. No salary AND no company name = low signal advert
        if not (job.get("salary_min") or job.get("salary_max")):
            score += 10; signals.append("no salary disclosed")
        if not job.get("company"):
            score += 15; signals.append("no company name")

        # 5. Missing apply URL
        if not job.get("url"):
            score += 15; signals.append("no application link")

        score = min(score, 100)
        verdict = ("likely ghost" if score >= 50 else
                   "suspicious" if score >= 30 else "looks genuine")
        self.log.info(f"Ghost score {score} ({verdict}): "
                      f"{job.get('title','?')}")
        return {"ghost_score": score, "verdict": verdict, "signals": signals}


class CompanyVerificationAgent(BaseAgent):
    name = "verify.company"

    def run(self, company: str) -> dict:
        """
        Stub with a working interface. Phase 2 wires a real existence check
        (Companies House API is free for UK firms; or a website HEAD request).
        Returns a structured result now so downstream code is stable.
        """
        if not company:
            return {"verified": False, "confidence": 0,
                    "note": "no company name to verify"}
        # TODO Phase 2: query Companies House API / fetch official site.
        return {"verified": True, "confidence": 50,
                "note": "interface stub — wire Companies House API for real check"}


class RecruiterVerificationAgent(BaseAgent):
    name = "verify.recruiter"

    def run(self, contact: dict) -> dict:
        """Assign a 0-100 trust score from available signals."""
        score = 0
        if contact.get("linkedin"):
            score += 35
        if contact.get("email", "").split("@")[-1] not in (
                "gmail.com", "outlook.com", "yahoo.com", ""):
            score += 35  # corporate domain
        if contact.get("company"):
            score += 30
        return {"trust_score": min(score, 100)}
