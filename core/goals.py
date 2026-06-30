"""
core/goals.py — weekly application goal + this-week tracker counts.

Stores a simple weekly goal and reports progress for the current week,
mirroring Simplify/LoopCV's "applications this week / weekly goal" panel.
"""

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from core import config, database

_GOAL_FILE = config.DATA_DIR / "goal.json"


def get_goal() -> int | None:
    if _GOAL_FILE.exists():
        try:
            return json.loads(_GOAL_FILE.read_text()).get("weekly_goal")
        except Exception:
            return None
    return None


def set_goal(n: int):
    _GOAL_FILE.write_text(json.dumps({"weekly_goal": int(n)}))


def week_bounds(today: datetime | None = None):
    today = today or datetime.now(timezone.utc)
    monday = today - timedelta(days=today.weekday())
    monday = monday.replace(hour=0, minute=0, second=0, microsecond=0)
    sunday = monday + timedelta(days=6, hours=23, minutes=59)
    return monday, sunday


def this_week() -> dict:
    """Count applications/interviews/saved within the current week."""
    monday, sunday = week_bounds()
    s = database.get_session()
    apps = s.query(database.Application).all()
    s.close()

    def in_week(dt):
        if dt is None:
            return False
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return monday <= dt <= sunday

    applied = sum(1 for a in apps
                  if a.status == "applied" and in_week(a.updated_at))
    interviews = sum(1 for a in apps
                     if a.status == "interview" and in_week(a.updated_at))
    saved = sum(1 for a in apps
                if a.status in ("matched", "found") and in_week(a.updated_at))
    return {"applied": applied, "interviews": interviews, "saved": saved,
            "week_start": monday.strftime("%d/%m/%Y"),
            "week_end": sunday.strftime("%d/%m/%Y")}
