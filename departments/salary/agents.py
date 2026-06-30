"""
Department 9 — SALARY
  CompensationAgent — total-comp calc + floor protection

Rule from blueprint: never suggest below the floor unless manually approved.
The blueprint hard-coded £34,000 as current salary; profile.py sets it to
None because you are between roles (Swayam ended Jun 2026). The agent uses
MINIMUM_SALARY as the protective floor and warns on anything beneath it.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from core.base_agent import BaseAgent
from core import profile


class CompensationAgent(BaseAgent):
    name = "salary.compensation"

    def run(self, offer: dict) -> dict:
        """
        offer = {base, bonus?, pension_pct?, benefits_value?, remote_days?}
        Returns total comp + a floor check.
        """
        base = offer.get("base", 0)
        bonus = offer.get("bonus", 0)
        pension = base * offer.get("pension_pct", 0) / 100
        benefits = offer.get("benefits_value", 0)
        remote_value = offer.get("remote_days", 0) * 1000  # rough proxy
        total = base + bonus + pension + benefits + remote_value

        floor = profile.MINIMUM_SALARY
        below_floor = base < floor
        result = {
            "base": base, "bonus": bonus, "pension": round(pension),
            "benefits": benefits, "remote_value": remote_value,
            "total_comp": round(total),
            "floor": floor, "below_floor": below_floor,
            "target_range": [profile.SALARY_TARGET_LOW,
                             profile.SALARY_TARGET_HIGH],
        }
        if below_floor:
            result["warning"] = (f"Base £{base:,} is below your floor "
                                 f"£{floor:,} — needs manual approval.")
            self.log.warning(result["warning"])
        return result
