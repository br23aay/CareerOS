"""
review.py — interactive review-mode loop. Run after main.py has prepared jobs.

    python main.py            # find, score, verify, draft, prepare
    python review.py          # review the queue, approve, open, mark applied

This is your daily driver: a fast pass through prepared applications.
Nothing is submitted for you — review.py opens each page so YOU click send.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))
from core import database, profile
from departments.application.fast_apply import FastApplyQueue


def main():
    database.init_db()
    q = FastApplyQueue()
    pending = q.pending()

    print(f"\n{'='*68}\nCareerOS — Review Queue for {profile.NAME}\n{'='*68}")
    if not pending:
        print("Nothing prepared yet. Run  python main.py  first.")
        return

    print("\nScreening answers that auto-fill on every application:")
    for k, v in q.screening_preview().items():
        short = v if len(v) < 60 else v[:57] + "..."
        print(f"  {k:20} {short}")
    print(f"\n{len(pending)} application(s) ready to review.\n{'-'*68}")

    for i, p in enumerate(pending, 1):
        tag = "FLAG" if p["verdict"] == "flag" else "APPLY"
        print(f"\n[{i}/{len(pending)}] {tag}  {p['score']}/10  "
              f"ghost:{p['ghost']}  status:{p['status']}")
        print(f"  {p['title']} — {p['company']}  ({p['location']})")
        print(f"  CV: {p['cv']}   Apply: {p['url']}")
        choice = input("  [o]pen & apply  [s]kip  [q]uit > ").strip().lower()
        if choice == "q":
            break
        if choice == "o":
            r = q.open_for_review(p["job_id"])
            if r["ok"]:
                input("  Page opened. Review, edit hook, click SEND yourself. "
                      "Press Enter when sent...")
                q.mark_applied(p["job_id"])
                print("  ✓ marked applied")
        else:
            print("  skipped")

    print(f"\n{'='*68}\nDone. Run analytics anytime to see your funnel.\n{'='*68}")


if __name__ == "__main__":
    main()
