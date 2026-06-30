"""
main.py — CareerOS entry point.

    python main.py
    python main.py --where "Hertfordshire"

Runs the full Orchestrator workflow: collect -> verify -> rank -> resume ->
prepare -> track -> analytics. Applications are PREPARED and held at the
human-approval gate — nothing is submitted for you.
"""

import argparse
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))
from core import database, profile
from departments.orchestrator.agents import Orchestrator


def main():
    ap = argparse.ArgumentParser(description="CareerOS")
    ap.add_argument("--where", default="", help="UK location filter")
    args = ap.parse_args()

    database.init_db()
    result = Orchestrator().run(where=args.where)

    print(f"\n{'='*72}\nCareerOS — {profile.NAME}\n{'='*72}")
    prepared = result["prepared"]
    if not prepared:
        print("No strong, non-ghost matches this run. "
              "Adjust SEARCH_TERMS or --where.")
    for p in prepared:
        tag = "FLAG" if p["verdict"] == "flag" else "APPLY"
        print(f"\n[{tag}] {p['score']}/10  ghost:{p['ghost']}  "
              f"fit:{p['predicted_fit']}")
        print(f"  {p['title']} — {p['company']}")
        print(f"  CV: {p['cv']}   cover: {p['cover']}")
        print(f"  {p['browser_status']}")
        print(f"  Apply: {p['url']}")
        if not p["validator"]["passed"]:
            print(f"  Validator: {', '.join(p['validator']['issues'])}")

    a = result["analytics"]
    print(f"\n{'-'*72}\nFunnel: found {a['jobs_found']} | applied {a['applied']}"
          f" | interviews {a['interviews']} | offers {a['offers']}")
    print(f"{'='*72}\n")


if __name__ == "__main__":
    main()
