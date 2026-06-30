"""
Department 10 — TRACKING
  ApplicationTracker — status transitions in the DB
  EmailMonitorAgent  — watch Gmail for interview/rejection/offer signals
  CalendarAgent      — interview dates / deadlines / tasks
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from core.base_agent import BaseAgent
from core import config, database

VALID_STATUSES = ["found", "matched", "applied", "contacted",
                  "interview", "rejected", "offer", "accepted"]


class ApplicationTracker(BaseAgent):
    name = "track.applications"

    def run(self, job_id: int, status: str) -> dict:
        if status not in VALID_STATUSES:
            return {"ok": False, "error": f"invalid status {status}"}
        s = database.get_session()
        app = s.query(database.Application).filter_by(job_id=job_id).first()
        if not app:
            app = database.Application(job_id=job_id, status=status)
            s.add(app)
        else:
            app.status = status
        s.commit(); s.close()
        self.log.info(f"Job {job_id} -> {status}")
        return {"ok": True, "job_id": job_id, "status": status}

    def summary(self) -> dict:
        s = database.get_session()
        counts = {st: 0 for st in VALID_STATUSES}
        for app in s.query(database.Application).all():
            counts[app.status] = counts.get(app.status, 0) + 1
        s.close()
        return counts


class EmailMonitorAgent(BaseAgent):
    name = "track.email"

    SIGNALS = {
        "interview": ["interview", "schedule a call", "next stage", "next steps",
                      "assessment", "technical test", "online test", "phone screen",
                      "video call", "meet the team", "hiring manager",
                      "invite you to", "would like to speak"],
        "offer": ["pleased to offer", "offer of employment", "job offer",
                  "delighted to offer", "formal offer", "offer letter"],
        "rejection": ["unfortunately", "not progressing", "other candidates",
                      "decided not to proceed", "not been successful",
                      "won't be moving forward", "regret to inform",
                      "not shortlisted", "position has been filled"],
        "applied": ["thank you for applying", "thanks for applying",
                    "application received", "we have received your application",
                    "your application for", "application submitted",
                    "thank you for your application", "successfully applied",
                    "received your application", "application has been received",
                    "thank you for your interest", "we received your"],
    }

    def classify(self, subject: str, body: str) -> str:
        text = f"{subject} {body}".lower()
        for label, kws in self.SIGNALS.items():
            if any(k in text for k in kws):
                return label
        return "other"

    def run(self) -> dict:
        """
        Reuses your Tony read-only Gmail OAuth. If no token path is set,
        returns a no-op so the OS still runs. Phase 4 wires the Gmail API
        list+get calls and feeds results through classify().
        """
        if not config.GMAIL_TOKEN_PATH:
            self.log.info("No Gmail token set — monitor idle "
                          "(reuse Tony's read-only OAuth in Phase 4).")
            return {"connected": False, "events": []}
        # TODO Phase 4: fetch recent messages, classify each.
        return {"connected": True, "events": []}


class CalendarAgent(BaseAgent):
    name = "track.calendar"

    def run(self) -> list[dict]:
        # TODO Phase 4: surface interview dates + application deadlines.
        return []
