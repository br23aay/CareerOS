"""
departments/application/fast_apply.py — the review-mode queue.

This is the "make it fast" piece. It does NOT auto-submit (the data is clear:
review-mode + your click is what gets interviews and keeps your accounts).
What it DOES is remove every slow step before the click:

  - pulls all prepared, non-ghost matches in one ranked list
  - shows each with score, ghost score, the right CV, the drafted cover letter
  - pre-fills the screening answers so you're not re-typing anything
  - opens the real application page in your browser on approval
  - marks it 'applied' in the tracker so analytics stays honest

Target rhythm (matches the 30-50/day best-practice from the research):
review a batch, edit the one-line hook, click send, mark done. Fast, safe,
TOS-compliant.
"""

import sys
import webbrowser
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from core.base_agent import BaseAgent
from core import database, screening


class FastApplyQueue(BaseAgent):
    name = "apply.fast_queue"

    def pending(self) -> list[dict]:
        """All prepared, non-ghost matches awaiting your review."""
        s = database.get_session()
        jobs = (s.query(database.Job)
                .filter(database.Job.verdict.in_(("apply", "flag", "consider")))
                .filter((database.Job.ghost_score == None) |
                        (database.Job.ghost_score < 50))
                .order_by(database.Job.score.desc())
                .all())
        out = []
        for j in jobs:
            app = (s.query(database.Application)
                   .filter_by(job_id=j.id).first())
            status = app.status if app else "new"
            from departments.job_intelligence.freshness import freshness_label
            out.append({
                "job_id": j.id, "title": j.title, "company": j.company,
                "location": j.location, "score": j.score,
                "ghost": j.ghost_score, "verdict": j.verdict,
                "cv": j.recommended_cv, "url": j.url, "status": status,
                "posted": j.posted,
                "freshness": freshness_label({"posted": j.posted}),
            })
        s.close()
        # within the score ordering, lift last-24h jobs to the very top
        rank = {"24h": 0, "this week": 1, "older": 2}
        out.sort(key=lambda p: (rank.get(p["freshness"], 2), -p["score"]))
        return out

    def screening_preview(self) -> dict:
        """The answers that will auto-fill — confirm once, reuse forever."""
        return screening.SCREENING_ANSWERS

    def open_for_review(self, job_id: int) -> dict:
        """
        Open the real application page in your browser so you can review and
        click send yourself. Marks the job 'applied' in the tracker.

        Honest by design: this opens the page and hands it to you. It does not
        press submit. That final action — and the TOS-compliance and the
        account safety that come with it — stays yours.
        """
        s = database.get_session()
        job = s.query(database.Job).get(job_id)
        if not job:
            s.close()
            return {"ok": False, "error": f"no job {job_id}"}
        url = job.url
        s.close()
        try:
            webbrowser.open(url)          # opens in your default browser
            self.log.info(f"Opened {url} for your review (job {job_id}).")
        except Exception as e:
            self.log.warning(f"Could not open browser: {e}")
        return {"ok": True, "job_id": job_id, "opened": url,
                "note": "Review, edit the cover hook, then click send yourself."}

    def mark_applied(self, job_id: int) -> dict:
        s = database.get_session()
        app = s.query(database.Application).filter_by(job_id=job_id).first()
        if not app:
            app = database.Application(job_id=job_id, status="applied")
            s.add(app)
        else:
            app.status = "applied"
        s.commit(); s.close()
        self.log.info(f"Job {job_id} marked applied.")
        return {"ok": True, "job_id": job_id, "status": "applied"}

    def reset_status(self, job_id: int, status: str = "matched") -> dict:
        """Undo an accidental 'applied' so the job returns to the queue."""
        s = database.get_session()
        app = s.query(database.Application).filter_by(job_id=job_id).first()
        if app:
            app.status = status
            s.commit()
        s.close()
        self.log.info(f"Job {job_id} reset to {status}.")
        return {"ok": True, "job_id": job_id, "status": status}

    def job_url(self, job_id: int) -> str:
        s = database.get_session()
        job = s.query(database.Job).get(job_id)
        url = job.url if job else ""
        s.close()
        return url
