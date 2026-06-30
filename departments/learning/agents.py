"""
Department 11 — LEARNING (most important long-term)
  ResumeLearningAgent   — CV version -> interview/offer rate
  OutreachLearningAgent — message -> reply rate
  JobSourceLearningAgent — best/worst sources
  SuccessPredictionAgent — which jobs are worth applying to

All learn from the Outcome table — real results, not guesses.
"""

import sys
from collections import defaultdict
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from core.base_agent import BaseAgent
from core import database, profile


def _rates(rows, key):
    agg = defaultdict(lambda: {"applied": 0, "interviewed": 0, "offered": 0,
                               "replied": 0})
    for r in rows:
        k = getattr(r, key) or "unknown"
        agg[k]["applied"] += int(r.applied)
        agg[k]["interviewed"] += int(r.interviewed)
        agg[k]["offered"] += int(r.offered)
        agg[k]["replied"] += int(r.replied)
    out = {}
    for k, c in agg.items():
        a = c["applied"] or 1
        out[k] = {"applied": c["applied"],
                  "interview_rate": round(c["interviewed"] / a, 3),
                  "offer_rate": round(c["offered"] / a, 3),
                  "reply_rate": round(c["replied"] / a, 3)}
    return out


class ResumeLearningAgent(BaseAgent):
    name = "learn.resume"

    def run(self) -> dict:
        s = database.get_session()
        rows = s.query(database.Outcome).all(); s.close()
        return _rates(rows, "cv_version")


class OutreachLearningAgent(BaseAgent):
    name = "learn.outreach"

    def run(self) -> dict:
        s = database.get_session()
        rows = s.query(database.Outcome).all(); s.close()
        total = len(rows) or 1
        replied = sum(int(r.replied) for r in rows)
        return {"reply_rate": round(replied / total, 3), "samples": len(rows)}


class JobSourceLearningAgent(BaseAgent):
    name = "learn.sources"

    def run(self) -> dict:
        s = database.get_session()
        rows = s.query(database.Outcome).all(); s.close()
        return _rates(rows, "job_source")


class SuccessPredictionAgent(BaseAgent):
    name = "learn.predict"

    def run(self, job: dict, score: float) -> dict:
        """
        Simple, honest heuristic until enough outcomes exist to train on.
        Blends matcher score with skill density; upgrade to a fitted model
        once the Outcome table has real history.
        """
        text = f"{job.get('title','')} {job.get('description','')}".lower()
        density = sum(1 for sk in profile.SKILLS if sk in text)
        prob = min(0.95, 0.05 + score / 20 + density / 40)
        return {"worth_applying": prob >= 0.4, "predicted_fit": round(prob, 2)}
