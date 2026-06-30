"""
core/config.py — central settings for CareerOS.

Local-first. No secrets hard-coded; keys come from environment variables.
Right-sized for a single user on a Windows laptop: SQLite, not Postgres;
plain Python, not Celery. The blueprint's Postgres/pgvector/Redis/Temporal
stack is noted in README under "scale-up path" for if this ever becomes a
multi-user product.

PowerShell, per session:
    $env:ADZUNA_APP_ID  = "your_id"
    $env:ADZUNA_APP_KEY = "your_key"
"""

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
STORAGE = ROOT / "storage"
LOGS = ROOT / "logs"
for _p in (DATA_DIR, STORAGE, LOGS):
    _p.mkdir(exist_ok=True)

RESUMES = STORAGE / "resumes"
COVERLETTERS = STORAGE / "coverletters"
INTERVIEWS = STORAGE / "interviews"
REPORTS = STORAGE / "reports"
for _p in (RESUMES, COVERLETTERS, INTERVIEWS, REPORTS):
    _p.mkdir(exist_ok=True)

DB_PATH = DATA_DIR / "careeros.db"
DB_URL = f"sqlite:///{DB_PATH}"

# --- Job source (Adzuna, free + legal) ------------------------------------
ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID", "")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY", "")
ADZUNA_COUNTRY = "gb"
ADZUNA_BASE = "https://api.adzuna.com/v1/api/jobs"
USE_MOCK_IF_NO_KEYS = True

# --- Local LLM (optional, reuses your Tony/Ollama Phi-3 setup) -------------
USE_LLM = False
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "phi3"

# --- Gmail monitor (reuses Tony's read-only OAuth token) -------------------
GMAIL_TOKEN_PATH = os.getenv("GMAIL_TOKEN_PATH", "")

# --- Matching thresholds ---------------------------------------------------
SCORE_APPLY = 6.0      # strong real matches reach the queue (was 7.0 — too
                       # strict on live data, where good roles rarely carry a
                       # high-priority company flag)
SCORE_CONSIDER = 4.5

# --- SAFETY GATES (do not disable) -----------------------------------------
# Applications are never transmitted without an explicit human approval.
REQUIRE_HUMAN_APPROVAL = True
# CAPTCHA solving / bot-detection bypass is intentionally NOT implemented.
ALLOW_CAPTCHA_BYPASS = False
