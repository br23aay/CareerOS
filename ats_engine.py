"""
departments/resume_factory/ats_engine.py — a real ATS-style scorer.

Mirrors what actual ATS (Workday/Greenhouse/Lever-style) do: extract the
keywords a job description emphasises, then score how well a CV covers them —
by presence, frequency, and section placement — and list what's missing.

It is honest: the score is computed from real overlap, not invented. A high
score means genuine coverage; a low score tells you exactly what to add.
"""

import re
import sys
from collections import Counter
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from core import master_cv as M

# Common ATS "noise" words to ignore when ranking JD keywords.
STOP = set("""a an the and or of to in for with on at by from as is are be this
that you your we our will must should role job work team using able strong
including etc per across into out over under more most can may also which who
what when where how new high low good great years year experience skills
ability working knowledge understanding required preferred responsibilities
about they them their it its he she his her have has had do does""".split())

# A curated skill/tech vocabulary so we score real competencies, not filler.
TECH_VOCAB = set("""python pytorch tensorflow keras scikit-learn sklearn numpy
pandas mujoco ppo reinforcement learning rl robotics ros mlflow docker
kubernetes azure aws gcp fastapi flask django rest api sql nosql postgres
mongodb spark hadoop airflow llm llms rag nlp transformers bert gpt llama
mistral embeddings vector fine-tuning prompt engineering computer vision
opencv cnn rnn lstm gan classification regression clustering deployment
ci/cd git github linux bash java c# c++ r matlab tableau powerbi statistics
machine deep neural networks data pipelines etl feature engineering
model evaluation benchmarking responsible guardrails""".split())


def extract_jd_keywords(jd: str) -> list:
    """Rank the keywords a JD emphasises (tech vocab + repeated salient terms)."""
    text = jd.lower()
    tokens = re.findall(r"[a-z][a-z+#./-]{1,}", text)
    bigrams = [f"{tokens[i]} {tokens[i+1]}" for i in range(len(tokens) - 1)]

    counts = Counter()
    for tok in tokens:
        if tok in STOP or len(tok) < 2:
            continue
        weight = 3 if tok in TECH_VOCAB else 1
        counts[tok] += weight
    for bg in bigrams:
        if bg in ("machine learning", "deep learning", "computer vision",
                  "reinforcement learning", "data science", "prompt engineering",
                  "neural networks", "natural language", "data pipelines"):
            counts[bg] += 4

    # keep meaningful ones, ranked
    ranked = [w for w, _ in counts.most_common(40)
              if w in TECH_VOCAB or " " in w or counts[w] >= 2]
    return ranked[:25]


def score_cv(jd: str, cv_text: str) -> dict:
    """
    Score a CV against a JD the way an ATS would: keyword coverage weighted by
    importance, with a placement bonus for keywords in a 'skills' section.
    Returns score 0-100, matched, missing, and per-keyword detail.
    """
    jd_kw = extract_jd_keywords(jd)
    if not jd_kw:
        return {"score": 0, "matched": [], "missing": [],
                "detail": [], "note": "JD too short to extract keywords"}

    cv_low = cv_text.lower()
    # crude 'skills section' slice for placement scoring
    skills_zone = ""
    m = re.search(r"(skills|technical)(.{0,1200})", cv_low, flags=re.S)
    if m:
        skills_zone = m.group(2)

    matched, missing, detail = [], [], []
    got_weight = 0.0
    total_weight = 0.0
    for kw in jd_kw:
        important = kw in TECH_VOCAB or " " in kw
        w = 2.0 if important else 1.0
        total_weight += w
        present = kw in cv_low
        if present:
            matched.append(kw)
            bonus = 0.3 if kw in skills_zone else 0.0  # placement bonus
            got_weight += w + bonus
            detail.append({"kw": kw, "status": "matched",
                           "in_skills": kw in skills_zone})
        else:
            missing.append(kw)
            detail.append({"kw": kw, "status": "missing", "important": important})

    score = round(min(100, got_weight / total_weight * 100)) if total_weight else 0
    band = ("strong" if score >= 75 else "moderate" if score >= 50 else "weak")
    return {"score": score, "band": band, "matched": matched,
            "missing": missing, "detail": detail,
            "jd_keywords": jd_kw}


def cv_text_from_master() -> str:
    """Flatten your master CV to text for scoring (no file needed)."""
    parts = [M.SUMMARY_BASE]
    parts.append("skills technical")
    for grp in M.SKILL_GROUPS.values():
        parts += grp
    for proj in M.PROJECTS:
        parts += proj["points"]
    for e in M.EDUCATION:
        parts += e["points"]
    return " ".join(parts).lower()
