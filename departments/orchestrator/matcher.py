"""
departments/orchestrator/matcher.py — central, explainable scoring engine.

Deterministic and auditable: every score carries reasons. Encodes the
REJECT / FLAG / salary / UK-only rules straight from your profile.
"""

import re
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from core import config, profile


def _text(job: dict) -> str:
    return (f"{job.get('title','')} {job.get('description','')} "
            f"{job.get('location','')} {job.get('company','')}").lower()


def _looks_remote(text: str) -> bool:
    return any(k in text for k in ("remote uk", "uk remote", "fully remote",
                                   "remote (uk)", "work from home"))


def hard_reject(job: dict):
    text = _text(job)
    title = job.get("title", "").lower()
    location = job.get("location", "").lower()
    for phrase in profile.REJECT_PHRASES:
        if phrase in text:
            return f"Reject phrase: '{phrase}'"
    for phrase in profile.SENIOR_PHRASES:
        if phrase in title:
            return f"Seniority mismatch: '{phrase.strip()}'"
    years = re.findall(r"(\d+)\+?\s*years?", text)
    if years and max(int(y) for y in years) >= profile.MIN_YEARS_REJECT:
        return f"Requires {max(int(y) for y in years)}+ years"
    if not _looks_remote(text):
        for marker in profile.NON_UK_MARKERS:
            if marker in location:
                return f"Outside UK: '{marker}'"
    smax = job.get("salary_max") or job.get("salary_min")
    if smax and smax < profile.SALARY_FLOOR:
        return f"Salary £{int(smax):,} < floor £{profile.SALARY_FLOOR:,}"
    return None


def _skill_score(job: dict):
    text = _text(job)
    matched, weight = [], 0
    for skill, w in profile.SKILLS.items():
        if skill in text:
            matched.append(skill); weight += w
    # Real adverts mention ~4-6 of your skills (raw weight ~8-11), not 18.
    # Cap at 10 so a genuine strong overlap reaches full marks; the matcher
    # still separates strong from weak because thin adverts score 1-3.
    return round(min(weight, 10) / 10 * 6, 2), matched


def _flag_bonus(job: dict):
    text = _text(job)
    hits = [c for c in profile.FLAG_COMPANIES if c in text]
    hits += [k for k in profile.FLAG_KEYWORDS if k in text]
    return (2.0 if hits else 0.0), hits


def _salary_bonus(job: dict):
    smax = job.get("salary_max") or job.get("salary_min") or 0
    if smax >= profile.SALARY_TARGET_LOW:
        return 1.0
    if smax >= profile.SALARY_FLOOR:
        return 0.5
    return 0.0


def match(job: dict) -> dict:
    reject = hard_reject(job)
    if reject:
        return {"score": 0.0, "verdict": "reject", "reasons": [reject],
                "matched_skills": [], "recommended_cv": None}
    skill_pts, matched = _skill_score(job)
    flag_pts, flag_hits = _flag_bonus(job)
    salary_pts = _salary_bonus(job)
    score = round(min(skill_pts + flag_pts + salary_pts, 10.0), 2)
    reasons = [f"Skill match {skill_pts}/6 "
               f"({', '.join(matched) if matched else 'none'})"]
    if flag_hits:
        reasons.append(f"HIGH-PRIORITY flag: {', '.join(flag_hits)} (+{flag_pts})")
    if salary_pts:
        reasons.append(f"Salary in range (+{salary_pts})")
    verdict = ("flag" if flag_hits else
               "apply" if score >= config.SCORE_APPLY else
               "consider" if score >= config.SCORE_CONSIDER else "reject")
    return {"score": score, "verdict": verdict, "reasons": reasons,
            "matched_skills": matched,
            "recommended_cv": profile.recommend_cv(
                job.get("title", ""), job.get("description", ""))}
