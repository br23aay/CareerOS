"""
core/base_agent.py — common base for every agent in every department.

Gives each agent a name, a logger, and a uniform run() contract so the
Orchestrator can drive them all the same way.
"""

import logging
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from core import config  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(name)-22s  %(message)s",
    handlers=[logging.StreamHandler(),
              logging.FileHandler(config.LOGS / "careeros.log")],
)


class BaseAgent:
    name = "base"

    def __init__(self):
        self.log = logging.getLogger(self.name)

    def run(self, *args, **kwargs):
        raise NotImplementedError(f"{self.name} must implement run()")
