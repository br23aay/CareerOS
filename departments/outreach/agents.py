"""
Department 7 — OUTREACH
  ContactDiscoveryAgent     — find recruiters/managers (interface stub)
  ContactVerificationAgent  — role/company/confidence
  CRMAgent                  — store contacts in DB
  OutreachWriterAgent       — recruiter emails / networking / follow-ups
  ChannelManager            — email / LinkedIn / company forms
  FollowUpAgent             — schedule day 2 / 7 / 14
"""

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from core.base_agent import BaseAgent
from core import database, profile


class ContactDiscoveryAgent(BaseAgent):
    name = "outreach.discovery"

    def run(self, company: str) -> list[dict]:
        # TODO Phase 5: integrate a permitted source (e.g. your Lusha/Indeed
        # connectors) — no scraping of LinkedIn. Interface returns a list now.
        self.log.info(f"Discovery stub for {company} (wire a permitted source)")
        return []


class ContactVerificationAgent(BaseAgent):
    name = "outreach.verify"

    def run(self, contact: dict) -> dict:
        confidence = 0
        if contact.get("company"): confidence += 40
        if contact.get("role"): confidence += 30
        if contact.get("linkedin") or contact.get("email"): confidence += 30
        return {**contact, "confidence": confidence}


class CRMAgent(BaseAgent):
    name = "outreach.crm"

    def run(self, contact: dict) -> int:
        s = database.get_session()
        row = database.Contact(
            name=contact.get("name"), role=contact.get("role"),
            company=contact.get("company"), linkedin=contact.get("linkedin"),
            email=contact.get("email"), trust_score=contact.get("trust_score"),
            history=contact.get("history", ""))
        s.add(row); s.commit(); cid = row.id; s.close()
        self.log.info(f"Stored contact #{cid}: {contact.get('name')}")
        return cid


class OutreachWriterAgent(BaseAgent):
    name = "outreach.writer"

    def run(self, contact: dict, job: dict) -> str:
        return (
            f"Hi {contact.get('name','there')},\n\n"
            f"I came across the {job.get('title','role')} at "
            f"{job.get('company','your team')} and wanted to introduce myself. "
            f"I'm an MSc AI & Robotics graduate with peer-reviewed IJRES "
            f"research on PPO-based Shadow Hand manipulation, and I hold a "
            f"Graduate Visa with full UK right to work (no sponsorship). "
            f"Would you be open to a short conversation?\n\n"
            f"Best regards,\n{profile.NAME}\n{profile.PORTFOLIO}")


class ChannelManager(BaseAgent):
    name = "outreach.channels"
    CHANNELS = ["email", "linkedin", "company_form"]

    def run(self, message: str, channel: str) -> dict:
        # Drafts only; sending stays a manual, approved action.
        if channel not in self.CHANNELS:
            return {"ok": False, "error": f"unknown channel {channel}"}
        return {"ok": True, "channel": channel, "draft": message,
                "status": "DRAFTED — send manually after review"}


class FollowUpAgent(BaseAgent):
    name = "outreach.followup"

    def run(self, sent_on: datetime | None = None) -> list[dict]:
        base = sent_on or datetime.now(timezone.utc)
        return [{"day": d, "due": (base + timedelta(days=d)).date().isoformat()}
                for d in (2, 7, 14)]
