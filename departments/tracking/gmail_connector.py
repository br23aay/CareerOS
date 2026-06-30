"""
departments/tracking/gmail_connector.py — read-only Gmail monitor.

Connects to Gmail with READ-ONLY scope, fetches recent messages, and
classifies each as interview / offer / rejection / other. It never sends,
deletes, replies to, or modifies anything — pure detection.

FIRST-TIME SETUP (one time, on your laptop):
  1. Have a Google OAuth client file 'credentials.json' in the project root.
     (From Google Cloud Console > APIs & Services > Credentials >
      OAuth client ID > Desktop app > Download JSON > rename to credentials.json)
  2. Run:  python -m departments.tracking.gmail_connector
     A browser opens; sign in and approve READ-ONLY access.
     This creates 'gmail_token.json' — the read token CareerOS uses.
  3. Set GMAIL_TOKEN_PATH to that file (or leave it in the project root).

After that, the Inbox page works automatically.
"""

import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from core.base_agent import BaseAgent
from core import config
from departments.tracking.agents import EmailMonitorAgent

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
ROOT = Path(__file__).resolve().parent.parent.parent
CREDENTIALS = ROOT / "credentials.json"
TOKEN = Path(config.GMAIL_TOKEN_PATH) if config.GMAIL_TOKEN_PATH else ROOT / "gmail_token.json"

# Job-related search across your WHOLE mailbox (no date cap) so every
# application you ever submitted is found, from the start to today.
QUERY = ('("thank you for applying" OR "application received" '
         'OR "your application" OR "thank you for your application" OR '
         '"received your application" OR "thank you for your interest" OR '
         'interview OR "next steps" OR offer OR "we regret" OR assessment OR '
         'recruiter OR hiring OR "your candidacy" OR "the role" OR "the position")')


class GmailConnector(BaseAgent):
    name = "track.gmail"

    def _service(self):
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build

        creds = None
        if TOKEN.exists():
            creds = Credentials.from_authorized_user_file(str(TOKEN), SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not CREDENTIALS.exists():
                    raise FileNotFoundError(
                        "credentials.json not found in project root. See setup "
                        "instructions at the top of gmail_connector.py.")
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(CREDENTIALS), SCOPES)
                # Port is LOCKED to 8080 to match the redirect URI you register
                # in Google: http://localhost:8080/  (must match exactly).
                print(">>> Opening browser on http://localhost:8080/ — make "
                      "sure this exact URI is in your Google client.")
                creds = flow.run_local_server(
                    host="localhost", port=8080,
                    authorization_prompt_message="",
                    open_browser=True)
            TOKEN.write_text(creds.to_json())
            self.log.info(f"Saved read token -> {TOKEN.name}")
        return build("gmail", "v1", credentials=creds)

    def connected(self) -> bool:
        return TOKEN.exists()

    def scan(self, max_results: int = 500) -> dict:
        """Fetch job-related mail across your whole history and classify each."""
        try:
            service = self._service()
        except Exception as e:
            return {"connected": False, "error": str(e), "events": []}

        monitor = EmailMonitorAgent()
        try:
            # paginate through all matching messages (Gmail returns ~100/page)
            ids, page_token, fetched = [], None, 0
            while fetched < max_results:
                resp = service.users().messages().list(
                    userId="me", q=QUERY, maxResults=100,
                    pageToken=page_token).execute()
                batch = [m["id"] for m in resp.get("messages", [])]
                ids.extend(batch)
                fetched += len(batch)
                page_token = resp.get("nextPageToken")
                if not page_token or not batch:
                    break
            ids = ids[:max_results]
            events = []
            for mid in ids:
                msg = service.users().messages().get(
                    userId="me", id=mid, format="metadata",
                    metadataHeaders=["Subject", "From", "Date"]).execute()
                headers = {h["name"]: h["value"]
                           for h in msg.get("payload", {}).get("headers", [])}
                subject = headers.get("Subject", "")
                snippet = msg.get("snippet", "")
                label = monitor.classify(subject, snippet)
                if label != "other":
                    events.append({
                        "label": label, "subject": subject,
                        "from": headers.get("From", ""),
                        "date": headers.get("Date", ""),
                        "snippet": snippet[:160]})
            self.log.info(f"Scanned {len(ids)} messages, "
                          f"{len(events)} job-relevant.")
            return {"connected": True, "scanned": len(ids), "events": events}
        except Exception as e:
            return {"connected": True, "error": str(e), "events": []}


if __name__ == "__main__":
    # Run directly to do the one-time browser authorisation.
    print("Authorising read-only Gmail access...")
    GmailConnector()._service()
    print("Done. gmail_token.json created. The Inbox page will now work.")
