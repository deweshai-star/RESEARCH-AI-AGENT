"""
tools.py — Core tool implementations for the Research Agent.
Provides: web_search(), extract_content()
"""

import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
from typing import Optional


# ─────────────────────────────────────────────────────────────────────────────
# TOOL 1 ─ Web Search via Tavily
# ─────────────────────────────────────────────────────────────────────────────

def web_search(query: str, tavily_client: TavilyClient, max_results: int = 6) -> list[dict]:
    """
    Search the web using Tavily and return structured results.

    Returns a list of dicts with keys:
      title, url, content (snippet), score
    """
    try:
        response = tavily_client.search(
            query=query,
            search_depth="advanced",
            max_results=max_results,
            include_answer=False,
            include_raw_content=False,
        )
        results = response.get("results", [])
        return results
    except Exception as e:
        print(f"   ⚠️  Search failed for query '{query}': {e}")
        return []


# ─────────────────────────────────────────────────────────────────────────────
# TOOL 2 ─ Content Extraction from URLs
# ─────────────────────────────────────────────────────────────────────────────

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def _extract_via_jina(url: str) -> Optional[str]:
    """Use Jina Reader to extract clean text (best quality, no JS issues)."""
    try:
        jina_url = f"https://r.jina.ai/{url}"
        resp = requests.get(jina_url, headers={"Accept": "text/plain"}, timeout=15)
        if resp.status_code == 200 and len(resp.text) > 200:
            return resp.text
    except Exception:
        pass
    return None


def _extract_via_requests(url: str) -> Optional[str]:
    """Fallback: direct HTTP fetch + BeautifulSoup parsing."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=12, allow_redirects=True)
        if resp.status_code != 200:
            return None

        soup = BeautifulSoup(resp.text, "lxml")

        # Remove noisy tags
        for tag in soup(["script", "style", "nav", "footer", "header",
                          "aside", "form", "noscript", "iframe"]):
            tag.decompose()

        # Prefer <article>, then <main>, then <body>
        for selector in ["article", "main", "body"]:
            element = soup.find(selector)
            if element:
                text = element.get_text(separator=" ", strip=True)
                if len(text) > 300:
                    return text

        return soup.get_text(separator=" ", strip=True)
    except Exception:
        return None


def extract_content(url: str, max_chars: int = 3500) -> str:
    """
    Extract readable content from a URL.
    Strategy: Jina Reader → BeautifulSoup fallback.
    Returns cleaned text, capped at max_chars.
    """
    content = _extract_via_jina(url)

    if not content or len(content) < 200:
        content = _extract_via_requests(url)

    if not content:
        return "[Content extraction failed — using snippet only]"

    # Normalize whitespace
    content = " ".join(content.split())
    return content[:max_chars]
