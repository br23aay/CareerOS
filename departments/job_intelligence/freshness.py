"""
departments/job_intelligence/freshness.py — recency ranking + NHS source.

  freshness_hours(job)  -> age of posting in hours (or None)
  freshness_label(job)  -> "24h" / "this week" / "older"
  sort_fresh(jobs)      -> freshest first, last-24h prioritised
  fetch_nhs(terms)      -> NHS Jobs via Adzuna 'healthcare' + NHS filter
"""

import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from core import config


def freshness_hours(job: dict):
    posted = job.get("posted", "")
    if not posted:
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S%z",
                "%Y-%m-%dT%H:%M:%S.%f%z", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(posted[:19] if "T" in posted else posted,
                                   fmt.replace("Z", "") if fmt.endswith("Z") else fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return (datetime.now(timezone.utc) - dt).total_seconds() / 3600
        except Exception:
            continue
    try:
        dt = datetime.fromisoformat(posted.replace("Z", "+00:00"))
        return (datetime.now(timezone.utc) - dt).total_seconds() / 3600
    except Exception:
        return None


def freshness_label(job: dict) -> str:
    h = freshness_hours(job)
    if h is None:
        return "older"
    if h <= 24:
        return "24h"
    if h <= 24 * 7:
        return "this week"
    return "older"


def sort_fresh(jobs: list[dict]) -> list[dict]:
    """Freshest first; unknown dates go last."""
    def key(j):
        h = freshness_hours(j)
        return h if h is not None else 1e9
    return sorted(jobs, key=key)


def fetch_nhs(search_terms: list[str], max_days_old: int = 7) -> list[dict]:
    """
    NHS roles via Adzuna, filtered to NHS/healthcare employers AND to roles in
    your field (data / AI / ML / analyst / engineer) — not clinical, nursing or
    admin posts. Falls back to empty list with no keys.
    """
    if not (config.ADZUNA_APP_ID and config.ADZUNA_APP_KEY):
        return []

    import re
    # only keep titles that match your field
    RELEVANT = re.compile(
        r"(data scientist|data analyst|data engineer|machine learning|"
        r"\bml\b|\bai\b|artificial intelligence|python|software engineer|"
        r"developer|analytics|informatics|research|statistician|bi |"
        r"business intelligence|deep learning|nlp)", re.I)
    # explicitly drop clinical / non-tech NHS roles even if they slip through
    EXCLUDE = re.compile(
        r"(nurse|nursing|midwif|doctor|consultant physician|clinical|"
        r"healthcare assistant|porter|receptionist|ward|pharmac|radiograph|"
        r"physiotherap|occupational therap|paramedic|surgeon|care assistant|"
        r"support worker|administrat|secretary|cleaner|catering)", re.I)

    out, seen = [], set()
    nhs_terms = ["NHS data scientist", "NHS data analyst", "NHS machine learning",
                 "NHS data engineer", "NHS informatics analyst", "NHS AI"]
    for term in nhs_terms:
        try:
            url = f"{config.ADZUNA_BASE}/{config.ADZUNA_COUNTRY}/search/1"
            r = requests.get(url, params={
                "app_id": config.ADZUNA_APP_ID, "app_key": config.ADZUNA_APP_KEY,
                "results_per_page": 20, "what": term, "max_days_old": max_days_old,
                "sort_by": "date", "content-type": "application/json"}, timeout=20)
            if r.status_code != 200:
                continue
            for raw in r.json().get("results", []):
                company = (raw.get("company") or {}).get("display_name", "")
                desc = raw.get("description", "")
                title = raw.get("title", "")
                # must be NHS/healthcare
                if "nhs" not in f"{company} {desc}".lower():
                    continue
                # must be in your field, and not a clinical/admin role
                if not RELEVANT.search(title):
                    continue
                if EXCLUDE.search(title):
                    continue
                sid = str(raw.get("id", ""))
                if sid in seen:
                    continue
                seen.add(sid)
                out.append({
                    "source": "nhs", "source_id": sid, "title": title,
                    "company": company,
                    "location": (raw.get("location") or {}).get("display_name", ""),
                    "description": desc,
                    "salary_min": int(raw["salary_min"]) if raw.get("salary_min") else None,
                    "salary_max": int(raw["salary_max"]) if raw.get("salary_max") else None,
                    "url": raw.get("redirect_url", ""), "posted": raw.get("created", "")})
        except Exception:
            continue
    return out
