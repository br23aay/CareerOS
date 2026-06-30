"""
Department 3 — JOB INTELLIGENCE
  JobCollectorAgent   — pull from Adzuna API (legal), mock fallback
  JobCleanerAgent     — drop duplicates / broken / expired
  JobCategorizerAgent — classify into IT/Backend/AI/Data/etc.
"""

import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from core.base_agent import BaseAgent
from core import config


def _normalise_adzuna(raw: dict) -> dict:
    return {
        "source": "adzuna", "source_id": str(raw.get("id", "")),
        "title": raw.get("title", "").replace("<strong>", "").replace(
            "</strong>", ""),
        "company": (raw.get("company") or {}).get("display_name", ""),
        "location": (raw.get("location") or {}).get("display_name", ""),
        "description": raw.get("description", ""),
        "salary_min": int(raw["salary_min"]) if raw.get("salary_min") else None,
        "salary_max": int(raw["salary_max"]) if raw.get("salary_max") else None,
        "url": raw.get("redirect_url", ""), "posted": raw.get("created", ""),
    }


class JobCollectorAgent(BaseAgent):
    name = "job.collector"

    def run(self, search_terms: list[str], where: str = "") -> list[dict]:
        if not (config.ADZUNA_APP_ID and config.ADZUNA_APP_KEY):
            if config.USE_MOCK_IF_NO_KEYS:
                self.log.info("No Adzuna keys — using mock jobs.")
                return self._mock()
            raise RuntimeError("No Adzuna keys configured.")
        seen, jobs = set(), []
        for term in search_terms:
            try:
                url = f"{config.ADZUNA_BASE}/{config.ADZUNA_COUNTRY}/search/1"
                params = {"app_id": config.ADZUNA_APP_ID,
                          "app_key": config.ADZUNA_APP_KEY,
                          "results_per_page": 20, "what": term,
                          "where": where, "max_days_old": 7,
                          "sort_by": "date",
                          "content-type": "application/json"}
                r = requests.get(url, params=params, timeout=30)
                r.raise_for_status()
                for raw in r.json().get("results", []):
                    job = _normalise_adzuna(raw)
                    key = (job["source"], job["source_id"])
                    if key not in seen:
                        seen.add(key); jobs.append(job)
            except Exception as e:
                self.log.warning(f"'{term}' failed: {e}")
        self.log.info(f"Collected {len(jobs)} jobs.")
        return jobs

    def _mock(self) -> list[dict]:
        return [
            {"source": "mock", "source_id": "1", "title": "Graduate AI Engineer",
             "company": "Tesco Technology",
             "location": "Welwyn Garden City, Hertfordshire",
             "description": "Python, PyTorch, machine learning, RAG and LLM "
                            "pipelines, FastAPI. Graduate level.",
             "salary_min": 32000, "salary_max": 38000,
             "url": "https://example.com/1", "posted": "2026-06-20"},
            {"source": "mock", "source_id": "2",
             "title": "Robotics Software Engineer",
             "company": "Shadow Robot Company", "location": "London (Remote UK)",
             "description": "Reinforcement learning, MuJoCo, PPO, robotics, "
                            "dexterous manipulation, Python.",
             "salary_min": 40000, "salary_max": 50000,
             "url": "https://example.com/2", "posted": "2026-06-22"},
            {"source": "mock", "source_id": "3",
             "title": "Senior Machine Learning Engineer", "company": "BigCorp",
             "location": "London",
             "description": "5+ years, Kubernetes, Spark, leadership.",
             "salary_min": 90000, "salary_max": 110000,
             "url": "https://example.com/3", "posted": "2026-06-18"},
            {"source": "mock", "source_id": "4",
             "title": "AI Engineer (SC Clearance required)",
             "company": "DefenceCo", "location": "Bristol",
             "description": "Security clearance required. Python, ML.",
             "salary_min": 45000, "salary_max": 55000,
             "url": "https://example.com/4", "posted": "2026-06-19"},
            {"source": "mock", "source_id": "5", "title": "Junior Data Scientist",
             "company": "StartupX", "location": "Dublin, Ireland",
             "description": "Python, scikit-learn, pandas. Graduate welcome.",
             "salary_min": 30000, "salary_max": 35000,
             "url": "https://example.com/5", "posted": "2026-06-21"},
        ]


class JobCleanerAgent(BaseAgent):
    name = "job.cleaner"

    def run(self, jobs: list[dict]) -> list[dict]:
        seen, cleaned = set(), []
        for j in jobs:
            key = (j.get("title", "").lower(), j.get("company", "").lower())
            if key in seen:
                continue
            if not j.get("url"):
                continue
            seen.add(key); cleaned.append(j)
        self.log.info(f"Cleaned: {len(cleaned)}/{len(jobs)} kept.")
        return cleaned


class JobCategorizerAgent(BaseAgent):
    name = "job.categorizer"
    BUCKETS = {
        "ai": ["ai", "machine learning", "ml ", "llm", "nlp", "deep learning"],
        "data": ["data scientist", "data engineer", "data analyst"],
        "backend": ["backend", "api", "fastapi", "django", "flask"],
        "frontend": ["frontend", "react", "angular", "vue"],
        "devops": ["devops", "kubernetes", "terraform", "ci/cd"],
        "cloud": ["cloud", "azure", "aws", "gcp"],
        "robotics": ["robotics", "mujoco", "ros", "manipulation"],
        "it_support": ["it support", "helpdesk", "service desk"],
        "cybersecurity": ["security", "soc analyst", "penetration"],
    }

    def run(self, job: dict) -> str:
        text = f"{job.get('title','')} {job.get('description','')}".lower()
        for bucket, kws in self.BUCKETS.items():
            if any(k in text for k in kws):
                return bucket
        return "other"
