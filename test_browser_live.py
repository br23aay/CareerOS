"""
test_browser_live.py — watch CareerOS drive a real Chrome window.

This is the honest "Chrome control" demo:
  - launches a VISIBLE Chrome (headless=False) so you see every action
  - opens a real page
  - reads the form fields
  - types your details in, slowly enough to watch
  - STOPS before submit and hands control to you

It drives a FRESH browser, not your logged-in LinkedIn/Indeed. That is the
line that keeps your real accounts safe. Auto-submitting on your own logged-in
accounts is what gets them suspended — so this prepares, then you click.

SETUP (one time, in PowerShell from K:\Projects\CareerOS):
    pip install playwright
    playwright install chromium

RUN:
    python test_browser_live.py
"""

import sys
import time
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))
from core import profile

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("Playwright not installed. Run:\n"
          "    pip install playwright\n"
          "    playwright install chromium")
    sys.exit(1)


# A safe public test form to prove control end-to-end without touching any
# real job site or any account. Swap this URL for a real job application page
# once you've watched it work here.
DEMO_URL = "https://httpbin.org/forms/post"

# What CareerOS would fill, drawn from your profile (ground truth).
ANSWERS = {
    "custname": profile.NAME,
    "custtel": profile.PHONE,
    "custemail": profile.EMAIL,
    "comments": (f"MSc AI & Robotics graduate. Published IJRES research on "
                 f"PPO Shadow Hand manipulation. {profile.VISA}. "
                 f"Available immediately."),
}


def run():
    print("\n=== CareerOS — live Chrome control demo ===")
    print(f"Applying as: {profile.NAME}\n")

    with sync_playwright() as p:
        # headless=False -> a real Chrome window opens and you watch it.
        # slow_mo adds a pause between actions so it's visible, not a blur.
        browser = p.chromium.launch(headless=False, slow_mo=600)
        page = browser.new_page()

        print(f"1. Opening page: {DEMO_URL}")
        page.goto(DEMO_URL)
        time.sleep(1)

        print("2. Reading the form fields on the page...")
        fields = page.query_selector_all("input, textarea")
        print(f"   Found {len(fields)} input fields.")

        print("3. Filling in your details (watch the window)...")
        for name, value in ANSWERS.items():
            selector = f'[name="{name}"]'
            if page.query_selector(selector):
                page.fill(selector, value)
                print(f"   · {name} -> filled")
                time.sleep(0.4)

        print("\n4. STOP. Form is filled. Submit is YOURS to click.")
        print("   The agent does not press submit. That is by design.")
        print("\n   Look at the Chrome window — your details are in the form.")
        print("   Press Enter here when you're done looking (closes browser).")
        input()

        browser.close()
        print("Browser closed. That's CareerOS Chrome control — prepare, "
              "then you approve.")


if __name__ == "__main__":
    run()
