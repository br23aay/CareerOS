"""
departments/research/web_research.py — CareerOS's own eyes on the web.

This is the "little brother" research engine: it searches and reads live web
pages itself, so referral emails and interview prep are grounded in REAL
current information, not templates.

Two routes, auto-selected:
  - FREE (default): DuckDuckGo HTML search + direct page fetch. No key.
  - BETTER (optional): a search API if SERPER_API_KEY is set in the env.

Honest limits: this reads PUBLIC pages (company sites, news, public profiles).
It does not log into anything or scrape behind authentication. Results are
summarised heuristically; quality depends on what's publicly available.
"""

import os
import re
import sys
from pathlib import Path

import requests

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from core.base_agent import BaseAgent

UA = {"User-Agent": "Mozilla/5.0 (CareerOS research agent)"}
SERPER_KEY = os.getenv("SERPER_API_KEY", "")


def _clean(html: str) -> str:
    html = re.sub(r"<script.*?</script>", " ", html, flags=re.S)
    html = re.sub(r"<style.*?</style>", " ", html, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"&[a-z]+;", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def search(query: str, n: int = 6) -> list[dict]:
    """Return [{title, url, snippet}]. Uses Serper if keyed, else DuckDuckGo."""
    if SERPER_KEY:
        try:
            r = requests.post("https://google.serper.dev/search",
                              json={"q": query, "num": n},
                              headers={"X-API-KEY": SERPER_KEY}, timeout=15)
            data = r.json().get("organic", [])
            return [{"title": d.get("title", ""), "url": d.get("link", ""),
                     "snippet": d.get("snippet", "")} for d in data[:n]]
        except Exception:
            pass  # fall through to free route
    # Free DuckDuckGo HTML route
    try:
        r = requests.post("https://html.duckduckgo.com/html/",
                          data={"q": query}, headers=UA, timeout=15)
        results = []
        blocks = re.findall(
            r'result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>.*?'
            r'result__snippet[^>]*>(.*?)</a>', r.text, flags=re.S)
        for url, title, snip in blocks[:n]:
            results.append({"url": url, "title": _clean(title),
                            "snippet": _clean(snip)})
        return results
    except Exception as e:
        return [{"title": "search failed", "url": "", "snippet": str(e)}]


def fetch_page(url: str, limit: int = 4000) -> str:
    try:
        r = requests.get(url, headers=UA, timeout=15)
        return _clean(r.text)[:limit]
    except Exception as e:
        return f"(could not fetch {url}: {e})"


class ResearchAgent(BaseAgent):
    name = "research.web"

    def company(self, name: str) -> dict:
        """A–Z snapshot of a company from live public sources."""
        if not name:
            return {"company": "", "summary": "no company given", "sources": []}
        self.log.info(f"Researching company: {name}")
        results = search(f"{name} company what they do products news", n=6)
        # try to read the company's own site (first non-aggregator result)
        site_text = ""
        for r in results:
            if r["url"] and not any(x in r["url"] for x in
                                    ("linkedin.", "glassdoor.", "indeed.")):
                site_text = fetch_page(r["url"], 2500)
                break
        snippets = " ".join(r["snippet"] for r in results if r["snippet"])
        return {
            "company": name,
            "overview": snippets[:800],
            "from_site": site_text[:800],
            "sources": [r["url"] for r in results if r["url"]][:5],
        }

    def person(self, name: str, linkedin: str = "", company: str = "") -> dict:
        """Public-profile snapshot of a contact for a personalised email."""
        if not name:
            return {"name": "", "summary": "no name given", "sources": []}
        self.log.info(f"Researching contact: {name} ({company})")
        q = f"{name} {company} linkedin".strip()
        results = search(q, n=5)
        prof = ""
        if linkedin:
            prof = fetch_page(linkedin, 1500)  # public part only
        snippets = " ".join(r["snippet"] for r in results if r["snippet"])
        return {
            "name": name, "company": company,
            "public_summary": snippets[:600],
            "profile_excerpt": prof[:400],
            "sources": [r["url"] for r in results if r["url"]][:4],
        }

    def role(self, title: str, company: str) -> dict:
        """What this role typically involves + interview signal."""
        self.log.info(f"Researching role: {title} @ {company}")
        results = search(f"{title} {company} interview process questions", n=5)
        snippets = " ".join(r["snippet"] for r in results if r["snippet"])
        return {"title": title, "company": company,
                "interview_signal": snippets[:700],
                "sources": [r["url"] for r in results if r["url"]][:4]}
