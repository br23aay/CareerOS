"""
Department 12 — ANALYTICS
  AnalyticsAgent — funnel counts + interview/offer/response rates
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from core.base_agent import BaseAgent
from core import database


class AnalyticsAgent(BaseAgent):
    name = "analytics.dashboard"

    def run(self) -> dict:
        s = database.get_session()
        total_jobs = s.query(database.Job).count()
        apps = s.query(database.Application).all()
        s.close()

        def count(status):
            return sum(1 for a in apps if a.status == status)

        applied = count("applied")
        contacted = count("contacted")
        interview = count("interview")
        offer = count("offer")

        def rate(n, d):
            return round(n / d, 3) if d else 0.0

        return {
            "jobs_found": total_jobs,
            "applied": applied,
            "contacted": contacted,
            "interviews": interview,
            "offers": offer,
            "interview_rate": rate(interview, applied),
            "offer_rate": rate(offer, applied),
            "response_rate": rate(contacted, applied),
        }
