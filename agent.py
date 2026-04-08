"""
agent.py — Core ResearchAgent implementing the 5-step reasoning workflow:
  STEP 1: PLAN   → Generate diverse search queries via LLM
  STEP 2: SEARCH → Execute queries via Tavily
  STEP 3: EXTRACT → Pull full content from top URLs
  STEP 4: SYNTHESIZE → Rank and deduplicate findings
  STEP 5: REPORT  → Generate structured markdown report via LLM
"""

import json
import re
import time
from datetime import datetime
from dataclasses import dataclass, field
from typing import Callable, Optional

from groq import Groq
from tavily import TavilyClient

from tools import web_search, extract_content


# ─────────────────────────────────────────────────────────────────────────────
# Data Models
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str
    score: float = 0.0


@dataclass
class ExtractedSource:
    title: str
    url: str
    snippet: str
    content: str
    domain: str = ""

    def __post_init__(self):
        # Extract domain for credibility heuristic
        match = re.search(r"https?://(?:www\.)?([^/]+)", self.url)
        self.domain = match.group(1) if match else self.url


@dataclass
class ResearchState:
    topic: str
    queries: list[str] = field(default_factory=list)
    raw_results: list[SearchResult] = field(default_factory=list)
    sources: list[ExtractedSource] = field(default_factory=list)
    report: str = ""
    logs: list[str] = field(default_factory=list)

    def log(self, msg: str):
        self.logs.append(msg)
        print(msg)


# ─────────────────────────────────────────────────────────────────────────────
# ResearchAgent
# ─────────────────────────────────────────────────────────────────────────────

class ResearchAgent:
    """
    A 5-step agentic research pipeline using Groq (LLM) + Tavily (search).
    """

    MODEL = "llama-3.3-70b-versatile"
    MAX_SOURCES = 5

    def __init__(self, groq_api_key: str, tavily_api_key: str):
        self.groq = Groq(api_key=groq_api_key, timeout=60.0)
        self.tavily = TavilyClient(api_key=tavily_api_key)

    # ── LLM Helper ────────────────────────────────────────────────────────────

    def _llm(self, prompt: str, temperature: float = 0.3, max_tokens: int = 4096) -> str:
        """Call Groq LLM with retry logic for transient network errors."""
        max_retries = 3
        for attempt in range(1, max_retries + 1):
            try:
                response = self.groq.chat.completions.create(
                    model=self.MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                if attempt == max_retries:
                    raise ConnectionError(
                        f"Groq API failed after {max_retries} attempts: {e}"
                    ) from e
                wait = 2 ** attempt
                print(f"   ⚠️  LLM call failed (attempt {attempt}/{max_retries}): {e}. Retrying in {wait}s...")
                time.sleep(wait)

    # ── STEP 1: PLAN ──────────────────────────────────────────────────────────

    def plan(self, state: ResearchState, on_progress: Optional[Callable] = None) -> ResearchState:
        state.log("📐 STEP 1 — Planning search queries...")

        prompt = f"""You are a senior research analyst. Your task is to generate 5 highly targeted, DISTINCT search queries to comprehensively research the topic below.

TOPIC: "{state.topic}"

Rules for generating queries:
- Each query must target a DIFFERENT angle (e.g., statistics, recent news, expert opinion, geographic/policy differences, impact/applications)
- Queries must be specific enough to return high-quality results — NOT vague
- Prefer queries that would surface recent (2024-2025) information
- Do NOT create 5 variations of the same query

Return ONLY a valid JSON array of exactly 5 query strings. No explanation, no markdown, just the JSON array.

Example format:
["query one", "query two", "query three", "query four", "query five"]"""

        raw = self._llm(prompt, temperature=0.4)

        # Robustly extract JSON array
        match = re.search(r"\[.*?\]", raw, re.DOTALL)
        if not match:
            raise ValueError(f"LLM did not return valid JSON array. Got:\n{raw}")

        queries = json.loads(match.group())
        state.queries = queries

        for i, q in enumerate(queries, 1):
            state.log(f"   Query {i}: {q}")

        if on_progress:
            on_progress("plan", queries)

        return state

    # ── STEP 2: SEARCH ────────────────────────────────────────────────────────

    def search(self, state: ResearchState, on_progress: Optional[Callable] = None) -> ResearchState:
        state.log("\n🔍 STEP 2 — Executing web searches...")

        seen_urls: set[str] = set()
        all_results: list[SearchResult] = []

        for i, query in enumerate(state.queries, 1):
            state.log(f"   Searching [{i}/{len(state.queries)}]: {query}")
            raw = web_search(query, self.tavily, max_results=5)

            for r in raw:
                url = r.get("url", "")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    all_results.append(SearchResult(
                        title=r.get("title", "Untitled"),
                        url=url,
                        snippet=r.get("content", ""),
                        score=r.get("score", 0.0),
                    ))

        # Sort by Tavily relevance score
        all_results.sort(key=lambda r: r.score, reverse=True)
        state.raw_results = all_results
        state.log(f"   ✓ Found {len(all_results)} unique URLs across all queries")

        if on_progress:
            on_progress("search", all_results)

        return state

    # ── STEP 3: EXTRACT ───────────────────────────────────────────────────────

    def extract(self, state: ResearchState, on_progress: Optional[Callable] = None) -> ResearchState:
        state.log(f"\n📄 STEP 3 — Extracting content from top {self.MAX_SOURCES} sources...")

        top = state.raw_results[:self.MAX_SOURCES]
        extracted: list[ExtractedSource] = []

        for i, result in enumerate(top, 1):
            state.log(f"   Extracting [{i}/{len(top)}]: {result.url[:70]}...")
            content = extract_content(result.url)

            source = ExtractedSource(
                title=result.title,
                url=result.url,
                snippet=result.snippet,
                content=content,
            )
            extracted.append(source)

            if on_progress:
                on_progress("extract", {"index": i, "total": len(top), "source": source})

        state.sources = extracted
        state.log(f"   ✓ Extracted content from {len(extracted)} sources")

        return state

    # ── STEP 4 + 5: SYNTHESIZE + REPORT ──────────────────────────────────────

    def synthesize_and_report(
        self, state: ResearchState, on_progress: Optional[Callable] = None
    ) -> ResearchState:
        state.log("\n🧠 STEP 4-5 — Synthesizing findings and generating report...")

        # Build source context for the LLM
        context_parts = []
        for i, src in enumerate(state.sources, 1):
            context_parts.append(
                f"--- SOURCE {i} ---\n"
                f"Title: {src.title}\n"
                f"URL: {src.url}\n"
                f"Domain: {src.domain}\n"
                f"Content:\n{src.content}\n"
            )
        context = "\n".join(context_parts)

        today = datetime.now().strftime("%B %d, %Y")
        n_sources = len(state.sources)

        prompt = f"""You are ResearchBot, a world-class research synthesis AI. Using ONLY the sources provided below, generate a comprehensive, accurate research report.

TOPIC: {state.topic}
DATE: {today}
SOURCES AVAILABLE: {n_sources}

═══════════════════════════════════════
SOURCE CONTENT:
{context}
═══════════════════════════════════════

Generate the report in EXACTLY this markdown format. Fill in every section thoroughly.

## 📋 Research Summary: {state.topic}
**Generated on:** {today}
**Sources consulted:** {n_sources} web pages

---

### 🔍 Overview
[Write 3-4 sentences: What is this topic? Why does it matter right now? What is the current state?]

---

### 📌 Key Findings

1. **[Specific, Informative Finding Title]**
   [2-3 sentences with specific data, statistics, or facts from the sources. Be precise.]
   *Source: [Exact Source Title] — [Full URL]*

2. **[Specific, Informative Finding Title]**
   [2-3 sentences...]
   *Source: [Exact Source Title] — [Full URL]*

3. **[Specific, Informative Finding Title]**
   [2-3 sentences...]
   *Source: [Exact Source Title] — [Full URL]*

4. **[Specific, Informative Finding Title]**
   [2-3 sentences...]
   *Source: [Exact Source Title] — [Full URL]*

5. **[Specific, Informative Finding Title]**
   [2-3 sentences...]
   *Source: [Exact Source Title] — [Full URL]*

[Add findings 6 and 7 if there is enough content from the sources]

---

### 🌐 Different Perspectives / Debates
[Summarize any conflicting claims, opposing viewpoints, or ongoing debates found across the sources. If there is broad consensus, state that clearly and explain what the consensus is.]

---

### 📈 Recent Developments
[Describe the most recent news, announcements, or developments found in the sources. Include specific dates, names, and numbers wherever possible.]

---

### ⚠️ Limitations & Gaps
[Be honest: What information was NOT found in these sources? What questions remain unanswered? What topics need more research? List 3-5 specific gaps.]

---

### 📚 Sources
| # | Title | Domain | URL | Relevance |
|---|-------|--------|-----|-----------|
[Fill in one row per source used]

---

### 🏷️ Tags
[List 6-8 specific, relevant keywords/tags separated by · ]

═══════════════════════════════════════
STRICT RULES YOU MUST FOLLOW:
- ❌ NEVER fabricate statistics, quotes, or facts not present in the sources above
- ❌ NEVER cite a source URL that is not explicitly listed in the sources above
- ❌ NEVER repeat the same fact as multiple separate findings
- ✅ ALWAYS ground every claim in a specific source
- ✅ ALWAYS note when something is "reportedly" vs confirmed
- ✅ ALWAYS flag gaps and missing information honestly
═══════════════════════════════════════"""

        report = self._llm(prompt, temperature=0.2, max_tokens=4000)
        state.report = report
        state.log("   ✓ Report generated successfully")

        if on_progress:
            on_progress("report", report)

        return state

    # ── Main Entry ─────────────────────────────────────────────────────────────

    def research(
        self,
        topic: str,
        on_progress: Optional[Callable] = None,
    ) -> ResearchState:
        """
        Run the full 5-step research pipeline.
        Returns a ResearchState with the final report and all intermediate data.
        """
        state = ResearchState(topic=topic)
        state.log(f"\n{'='*60}")
        state.log(f"🔬 ResearchBot — Starting research on: {topic}")
        state.log(f"{'='*60}")

        state = self.plan(state, on_progress)
        state = self.search(state, on_progress)
        state = self.extract(state, on_progress)
        state = self.synthesize_and_report(state, on_progress)

        state.log(f"\n{'='*60}")
        state.log("✅ Research complete!")
        state.log(f"{'='*60}\n")

        return state
