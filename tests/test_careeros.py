"""
tests/test_careeros.py — verifies the decision logic, not just that it runs.

Run from the project root:
    python -m pytest tests/ -v       (if you have pytest)
    python tests/test_careeros.py    (plain, no dependencies)

Covers the parts that make real decisions: reject rules, flag rules, salary
floor, ghost detection, validator honesty checks, and the two safety gates.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

from core import config, profile
from departments.orchestrator.matcher import match, hard_reject
from departments.verification.agents import GhostJobDetector
from departments.salary.agents import CompensationAgent
from departments.resume.agents import ResumeWriterAgent, ResumeValidatorAgent
from departments.application.agents import BrowserAgent, ErrorRecoveryAgent
from departments.job_intelligence.agents import JobCategorizerAgent


# --- tiny test harness (no external deps needed) ---------------------------
_passed, _failed = 0, 0


def check(label, condition):
    global _passed, _failed
    if condition:
        _passed += 1
        print(f"  PASS  {label}")
    else:
        _failed += 1
        print(f"  FAIL  {label}")


def J(**kw):
    """Build a job dict with sensible defaults."""
    base = {"title": "", "company": "", "location": "UK", "description": "",
            "salary_min": None, "salary_max": None, "url": "https://x.com/1",
            "posted": "2026-06-22"}
    base.update(kw)
    return base


# === MATCHER: reject rules =================================================
def test_reject_rules():
    print("\n[MATCHER — reject rules]")
    check("rejects SC clearance",
          hard_reject(J(title="AI Engineer",
                        description="SC clearance required")) is not None)
    check("rejects senior titles",
          hard_reject(J(title="Senior ML Engineer")) is not None)
    check("rejects 3+ years experience",
          hard_reject(J(description="minimum 5 years experience")) is not None)
    check("rejects PhD-required",
          hard_reject(J(description="PhD required for this role")) is not None)
    check("rejects non-UK (Dublin)",
          hard_reject(J(location="Dublin, Ireland")) is not None)
    check("rejects below salary floor",
          hard_reject(J(salary_max=22000)) is not None)
    check("does NOT reject a clean graduate role",
          hard_reject(J(title="Graduate AI Engineer", location="London",
                        salary_max=35000, description="python pytorch")) is None)


# === MATCHER: scoring & flags ==============================================
def test_scoring():
    print("\n[MATCHER — scoring & flags]")
    flagged = match(J(title="Robotics Software Engineer",
                      company="Shadow Robot Company",
                      location="London (Remote UK)", salary_max=50000,
                      description="reinforcement learning mujoco ppo robotics"))
    check("Shadow Robot flagged", flagged["verdict"] == "flag")
    check("flag role scores high", flagged["score"] >= 7.0)
    check("recommends ShadowRobot_v2 CV",
          flagged["recommended_cv"] == "ShadowRobot_v2")

    weak = match(J(title="Graduate Data Analyst", location="Leeds",
                   salary_max=28000, description="excel reporting"))
    check("weak role not 'apply'", weak["verdict"] in ("consider", "reject"))

    rejected = match(J(title="Senior Engineer", description="sc clearance"))
    check("rejected role scores 0", rejected["score"] == 0.0)
    check("every verdict has reasons", len(flagged["reasons"]) > 0)


# === VERIFICATION: ghost detector ==========================================
def test_ghost():
    print("\n[VERIFICATION — ghost detector]")
    g = GhostJobDetector()
    clean = g.run(J(title="Graduate AI Engineer", company="Tesco",
                    salary_max=38000,
                    description="Python, PyTorch, machine learning, RAG, "
                                "FastAPI deployment at graduate level."))
    check("clean job scores low", clean["ghost_score"] < 30)

    ghost = g.run(J(title="AI Engineer", company="",
                    description="We are always hiring! Register your interest "
                                "to build a talent pool.",
                    salary_max=None, posted="2026-01-01"))
    check("evergreen+stale+no-salary flagged", ghost["ghost_score"] >= 50)
    check("ghost verdict reported",
          ghost["verdict"] in ("suspicious", "likely ghost"))
    check("signals are explained", len(ghost["signals"]) > 0)


# === SALARY: floor protection ==============================================
def test_salary():
    print("\n[SALARY — floor protection]")
    c = CompensationAgent()
    low = c.run({"base": 22000})
    check("flags base below floor", low["below_floor"] is True)
    check("low offer carries a warning", "warning" in low)

    good = c.run({"base": 40000, "bonus": 4000, "pension_pct": 5})
    check("good offer not below floor", good["below_floor"] is False)
    check("total comp adds pension+bonus", good["total_comp"] > 40000)


# === RESUME: writer + validator honesty ====================================
def test_resume():
    print("\n[RESUME — writer & validator]")
    job = J(title="Graduate AI Engineer", company="Tesco",
            description="python pytorch rag llm")
    cover = ResumeWriterAgent().run(job)
    check("cover names the company", "Tesco" in cover)
    check("cover includes right-to-work line", "Graduate Visa" in cover)
    check("cover does NOT fabricate (no 'expert in langchain')",
          "expert in langchain" not in cover.lower())

    v = ResumeValidatorAgent()
    check("validator catches unfilled hook",
          v.run(cover)["passed"] is False)
    fake = "I am an expert in langchain and kubernetes."
    check("validator flags overclaim on developing skills",
          len(v.run(fake)["issues"]) > 0)


# === SAFETY GATES (the two non-negotiables) ================================
def test_safety_gates():
    print("\n[SAFETY — gates must hold]")
    check("human-approval flag is ON", config.REQUIRE_HUMAN_APPROVAL is True)
    check("captcha-bypass flag is OFF", config.ALLOW_CAPTCHA_BYPASS is False)

    prepared = BrowserAgent().run(J(title="x"), "cv.pdf", "cover.txt")
    check("browser never auto-submits", prepared["submitted"] is False)
    check("browser holds at approval gate",
          "approval" in prepared["status"].lower())

    recovery = ErrorRecoveryAgent().run("captcha")
    check("captcha is NOT auto-solved", recovery["auto_solve"] is False)
    check("captcha routes to manual step",
          "manual" in recovery["action"].lower())


# === CATEGORIZER ===========================================================
def test_categorizer():
    print("\n[JOB INTELLIGENCE — categorizer]")
    cat = JobCategorizerAgent()
    check("AI role -> ai",
          cat.run(J(title="Machine Learning Engineer")) == "ai")
    check("robotics role -> robotics",
          cat.run(J(title="Robotics Engineer", description="mujoco ros")) ==
          "robotics")
    check("support role -> it_support",
          cat.run(J(title="IT Support Analyst",
                    description="helpdesk service desk")) == "it_support")


def main():
    print("=" * 60)
    print("CareerOS test suite")
    print("=" * 60)
    for fn in (test_reject_rules, test_scoring, test_ghost, test_salary,
               test_resume, test_safety_gates, test_categorizer):
        fn()
    print("\n" + "=" * 60)
    print(f"RESULT: {_passed} passed, {_failed} failed")
    print("=" * 60)
    return 1 if _failed else 0


if __name__ == "__main__":
    sys.exit(main())
