"""
departments/job_intelligence/sources.py — multiple legal job sources.

The single-source trickle was starving the pipeline. This pulls from several
LEGAL, key-free or free-key sources and normalises them into one schema so the
matcher/ghost/tailor stages never care where a job came from.

Sources:
  - Adzuna       (free key)  — broad UK aggregator
  - Reed         (free key)  — broad UK aggregator
  - Greenhouse   (no key)    — company career boards (Graphcore, Speechmatics...)
  - Lever        (no key)    — company career boards (Palantir...)

Greenhouse/Lever are exactly the "company career page" sources that the best
auto-apply tools use to avoid ghost jobs — the listings come straight from the
employer's own ATS.
"""

import os
import re
import sys
from pathlib import Path

import requests

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from core.base_agent import BaseAgent
from core import config

UA = {"User-Agent": "Mozilla/5.0 (CareerOS)"}
REED_KEY = os.getenv("REED_API_KEY", "")

# Curated company boards relevant to AI/ML/grad roles. Add freely.
GREENHOUSE_BOARDS = ["graphcore", "speechmatics", "monzo", "gocardless",
                     "cleo", "starlingbank", "wise", "improbable"]
LEVER_BOARDS = ["palantir"]

# Only keep roles whose title looks relevant + UK-based.
RELEVANT = re.compile(r"(machine learning|ml |ai |artificial intelligence|"
                      r"data scien|data engineer|software engineer|python|"
                      r"deep learning|nlp|research engineer|robotic|"
                      r"graduate|junior|backend|ml engineer|mlops)", re.I)
UK_HINT = re.compile(r"(uk|united kingdom|london|manchester|bristol|cambridge|"
                     r"oxford|edinburgh|leeds|remote)", re.I)


def _clean(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text or "")
    return re.sub(r"\s+", " ", text).strip()


class MultiSourceFetcher(BaseAgent):
    name = "job.sources"

    def fetch_all(self, search_terms: list[str], where: str = "") -> list[dict]:
        jobs, seen = [], set()
        for fn in (self._adzuna, self._reed, self._greenhouse, self._lever):
            try:
                for j in fn(search_terms, where):
                    key = (j["title"].lower()[:60], j["company"].lower()[:40])
                    if key not in seen and j["title"]:
                        seen.add(key)
                        jobs.append(j)
            except Exception as e:
                self.log.warning(f"{fn.__name__} failed: {e}")
        self.log.info(f"Multi-source total: {len(jobs)} unique jobs.")
        return jobs

    # --- Adzuna ---
    def _adzuna(self, terms, where):
        if not (config.ADZUNA_APP_ID and config.ADZUNA_APP_KEY):
            return []
        out = []
        for term in terms[:6]:
            url = f"{config.ADZUNA_BASE}/{config.ADZUNA_COUNTRY}/search/1"
            r = requests.get(url, params={
                "app_id": config.ADZUNA_APP_ID, "app_key": config.ADZUNA_APP_KEY,
                "results_per_page": 20, "what": term, "where": where,
                "max_days_old": 30, "content-type": "application/json"}, timeout=20)
            if r.status_code != 200:
                continue
            for raw in r.json().get("results", []):
                out.append({
                    "source": "adzuna", "source_id": str(raw.get("id", "")),
                    "title": _clean(raw.get("title", "")),
                    "company": (raw.get("company") or {}).get("display_name", ""),
                    "location": (raw.get("location") or {}).get("display_name", ""),
                    "description": _clean(raw.get("description", "")),
                    "salary_min": int(raw["salary_min"]) if raw.get("salary_min") else None,
                    "salary_max": int(raw["salary_max"]) if raw.get("salary_max") else None,
                    "url": raw.get("redirect_url", ""), "posted": raw.get("created", "")})
        return out

    # --- Reed (free key) ---
    def _reed(self, terms, where):
        if not REED_KEY:
            return []
        out = []
        for term in terms[:5]:
            r = requests.get("https://www.reed.co.uk/api/1.0/search",
                             params={"keywords": term, "locationName": where or "UK",
                                     "resultsToTake": 20},
                             auth=(REED_KEY, ""), timeout=20)
            if r.status_code != 200:
                continue
            for raw in r.json().get("results", []):
                out.append({
                    "source": "reed", "source_id": str(raw.get("jobId", "")),
                    "title": _clean(raw.get("jobTitle", "")),
                    "company": raw.get("employerName", ""),
                    "location": raw.get("locationName", ""),
                    "description": _clean(raw.get("jobDescription", "")),
                    "salary_min": int(raw["minimumSalary"]) if raw.get("minimumSalary") else None,
                    "salary_max": int(raw["maximumSalary"]) if raw.get("maximumSalary") else None,
                    "url": raw.get("jobUrl", ""), "posted": raw.get("date", "")})
        return out

    # --- Greenhouse company boards (no key) ---
    def _greenhouse(self, terms, where):
        out = []
        for board in GREENHOUSE_BOARDS:
            try:
                r = requests.get(
                    f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs",
                    params={"content": "true"}, headers=UA, timeout=12)
                if r.status_code != 200:
                    continue
                for raw in r.json().get("jobs", []):
                    title = raw.get("title", "")
                    loc = (raw.get("location") or {}).get("name", "")
                    if not RELEVANT.search(title):
                        continue
                    if not UK_HINT.search(loc):
                        continue
                    out.append({
                        "source": "greenhouse", "source_id": str(raw.get("id", "")),
                        "title": _clean(title), "company": board.title(),
                        "location": loc, "description": _clean(raw.get("content", ""))[:2000],
                        "salary_min": None, "salary_max": None,
                        "url": raw.get("absolute_url", ""),
                        "posted": raw.get("updated_at", "")})
            except Exception as e:
                self.log.warning(f"greenhouse {board}: {e}")
        return out

    # --- Lever company boards (no key) ---
    def _lever(self, terms, where):
        out = []
        for board in LEVER_BOARDS:
            try:
                r = requests.get(f"https://api.lever.co/v0/postings/{board}",
                                 params={"mode": "json"}, headers=UA, timeout=12)
                if r.status_code != 200:
                    continue
                for raw in r.json():
                    title = raw.get("text", "")
                    loc = (raw.get("categories") or {}).get("location", "")
                    if not RELEVANT.search(title):
                        continue
                    if not UK_HINT.search(loc):
                        continue
                    out.append({
                        "source": "lever", "source_id": str(raw.get("id", "")),
                        "title": _clean(title), "company": board.title(),
                        "location": loc,
                        "description": _clean(raw.get("descriptionPlain", ""))[:2000],
                        "salary_min": None, "salary_max": None,
                        "url": raw.get("hostedUrl", ""),
                        "posted": str(raw.get("createdAt", ""))})
            except Exception as e:
                self.log.warning(f"lever {board}: {e}")
        return out
