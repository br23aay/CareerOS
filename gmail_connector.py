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

# job-related search so we only scan relevant mail, not your whole inbox
QUERY = ('newer_than:30d (interview OR application OR "your application" OR '
         'offer OR "we regret" OR assessment OR "next steps" OR recruiter OR '
         'hiring OR position OR role)')


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

    def scan(self, max_results: int = 25) -> dict:
        """Fetch recent job-related mail and classify each message."""
        try:
            service = self._service()
        except Exception as e:
            return {"connected": False, "error": str(e), "events": []}

        monitor = EmailMonitorAgent()
        try:
            resp = service.users().messages().list(
                userId="me", q=QUERY, maxResults=max_results).execute()
            ids = [m["id"] for m in resp.get("messages", [])]
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
