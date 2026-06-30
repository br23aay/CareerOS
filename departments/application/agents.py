"""
Department 6 — APPLICATION
  FormAnalysisAgent   — read a form's fields/questions
  BrowserAgent        — Playwright automation, prepares then STOPS at submit
  SessionRefreshAgent — fresh session each run (visit -> learn -> prepare)
  ErrorRecoveryAgent  — timeouts/broken forms (CAPTCHA: NOT bypassed)

IMPORTANT DESIGN NOTE
---------------------
The blueprint asked the BrowserAgent to "Submit Application" and the
ErrorRecoveryAgent to "Handle Captcha". Two deliberate limits are baked in:

  1. config.REQUIRE_HUMAN_APPROVAL gates the final submit. The agent fills
     and prepares everything, then hands control back to you for the click.
  2. config.ALLOW_CAPTCHA_BYPASS is False and there is no solver. CAPTCHA is
     detected and surfaced to you, never auto-defeated.

Why: auto-submitting violates most platforms' terms and gets accounts and IPs
banned mid-search — the fastest way to lose your real LinkedIn/Indeed logins.
Preparing the application is 95% of the grind; you keep the final action.
Flip these flags only if you fully own the consequences on a given site.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from core.base_agent import BaseAgent
from core import config


class FormAnalysisAgent(BaseAgent):
    name = "apply.form_analysis"

    def run(self, fields: list[str]) -> dict:
        """Map raw form fields to known profile answers where possible."""
        from core import profile
        answers = {
            "name": profile.NAME, "email": profile.EMAIL,
            "phone": profile.PHONE, "location": profile.LOCATION,
            "right to work": "Yes — Graduate Visa, no sponsorship required",
            "sponsorship": "Not required",
            "salary": f"£{profile.SALARY_TARGET_LOW:,}–"
                      f"£{profile.SALARY_TARGET_HIGH:,}",
            "availability": "Immediately",
        }
        mapped = {f: answers.get(f.lower().strip(), "[REVIEW: fill manually]")
                  for f in fields}
        return {"mapped": mapped,
                "needs_review": [f for f, v in mapped.items()
                                 if "[REVIEW" in v]}


class SessionRefreshAgent(BaseAgent):
    name = "apply.session_refresh"

    def run(self, url: str) -> dict:
        """
        Each run starts a fresh session and re-learns the page, per your
        requirement to never rely only on old memory.
        Stub: Phase 2 drives a real Playwright context here.
        """
        self.log.info(f"Fresh session -> visit -> learn structure: {url}")
        return {"session": "fresh", "url": url, "structure": "relearned"}


class BrowserAgent(BaseAgent):
    name = "apply.browser"

    def run(self, job: dict, cv_path: str, cover_path: str) -> dict:
        """
        Prepare an application end-to-end, then STOP at the submit gate.
        Phase 2 wires Playwright for open/upload/fill. The submit step is
        intentionally not transmitted while REQUIRE_HUMAN_APPROVAL is True.
        """
        prepared = {
            "url": job.get("url"), "cv": cv_path, "cover": cover_path,
            "steps_ready": ["open_site", "upload_cv", "fill_form"],
            "submitted": False,
        }
        if config.REQUIRE_HUMAN_APPROVAL:
            prepared["status"] = "PREPARED — awaiting your approval to submit"
            self.log.info("Application prepared; held at human-approval gate.")
        else:
            prepared["status"] = "auto-submit flag on — still requires Phase 2 "
            self.log.warning("REQUIRE_HUMAN_APPROVAL is off — review your ToS.")
        return prepared


class ErrorRecoveryAgent(BaseAgent):
    name = "apply.error_recovery"

    def run(self, error_type: str) -> dict:
        handlers = {
            "timeout": "retry with backoff (max 3)",
            "broken_form": "log, screenshot, skip and flag for manual apply",
        }
        if error_type == "captcha":
            # Detected, never solved.
            return {"action": "STOP — CAPTCHA detected. Manual step required.",
                    "auto_solve": False}
        return {"action": handlers.get(error_type, "log and flag for review")}
