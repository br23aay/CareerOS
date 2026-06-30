"""
core/screening.py — answer the common application questions ONCE, reuse
them across every application. This is the feature that makes review mode
fast (the thing JobCopilot/LoopCV charge for).

Edit your answers here. The FastApply queue pulls them in automatically so
you're never re-typing notice period / salary / work authorisation again.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from core import profile

# The questions almost every ATS asks, answered once in your voice.
SCREENING_ANSWERS = {
    "full_name": profile.NAME,
    "email": profile.EMAIL,
    "phone": profile.PHONE,
    "location": profile.LOCATION,
    "right_to_work": "Yes — I hold a UK Graduate Visa (PSW) with full right to "
                     "work until September 2027. I do not require sponsorship.",
    "require_sponsorship": "No",
    "notice_period": "Available immediately",
    "salary_expectation": f"£{profile.SALARY_TARGET_LOW:,}–"
                          f"£{profile.SALARY_TARGET_HIGH:,}",
    "willing_to_relocate": "Yes — open to any UK location, including relocation",
    "linkedin": profile.LINKEDIN,
    "github": profile.GITHUB,
    "portfolio": profile.PORTFOLIO,
    "years_experience": "MSc AI & Robotics graduate with published IJRES "
                        "research; early-career.",
    "why_interested": "[PER ROLE — one honest line; the writer drafts this]",
}

# Map a raw form field label to the right stored answer.
FIELD_ALIASES = {
    "name": "full_name", "first name": "full_name", "candidate name": "full_name",
    "e-mail": "email", "email address": "email",
    "telephone": "phone", "mobile": "phone", "contact number": "phone",
    "city": "location", "address": "location",
    "work authorization": "right_to_work", "work authorisation": "right_to_work",
    "eligible to work": "right_to_work", "visa status": "right_to_work",
    "sponsorship": "require_sponsorship", "require visa": "require_sponsorship",
    "notice": "notice_period", "availability": "notice_period",
    "start date": "notice_period",
    "salary": "salary_expectation", "expected salary": "salary_expectation",
    "compensation": "salary_expectation",
    "relocate": "willing_to_relocate",
    "linkedin profile": "linkedin", "github profile": "github",
    "portfolio url": "portfolio", "website": "portfolio",
}


def answer_for(field_label: str) -> str | None:
    """Given a raw form field label, return the stored answer or None."""
    key = field_label.strip().lower()
    if key in SCREENING_ANSWERS:
        return SCREENING_ANSWERS[key]
    if key in FIELD_ALIASES:
        return SCREENING_ANSWERS[FIELD_ALIASES[key]]
    # loose contains-match as a fallback
    for alias, target in FIELD_ALIASES.items():
        if alias in key:
            return SCREENING_ANSWERS[target]
    return None


def map_form(field_labels: list[str]) -> dict:
    """Map a whole form's fields to answers; flag what needs manual input."""
    mapped, manual = {}, []
    for label in field_labels:
        ans = answer_for(label)
        if ans is None or ans.startswith("[PER ROLE"):
            manual.append(label)
            mapped[label] = ans or "[REVIEW — fill manually]"
        else:
            mapped[label] = ans
    return {"mapped": mapped, "needs_manual": manual,
            "auto_filled": len(field_labels) - len(manual),
            "total": len(field_labels)}
