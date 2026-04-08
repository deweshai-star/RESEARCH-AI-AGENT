# Detailed Plan: Research AI Agent

## Overview
A research assistant agent capable of taking a user-provided topic, autonomously searching the web for recent information, extracting key facts, evaluating source credibility, and producing a structured summary with citations.

## Tech Stack
*   **LLM Engine**: Groq API (Llama 3.3-70B)
*   **Search Engine**: Tavily Advanced Search API
*   **Web Extraction**: Jina Reader API with BeautifulSoup fallback
*   **UI Framework**: Streamlit
*   **Core Logic**: Pure Python with `requests`, `regex`, and minimal dependencies

## Agent Architecture
The agent runs a strict 5-step deterministic reasoning loop:

### Step 1: PLAN
*   **Goal**: Deconstruct the user's research topic into targeted queries.
*   **Process**: Pass the topic to the LLM to generate 5 highly targeted, distinct search queries.
*   **Prompting**: Force the LLM to return only a strict JSON array of strings to maintain pipeline integrity.

### Step 2: SEARCH
*   **Goal**: Gather initial raw data covering various angles of the topic.
*   **Process**: Iterate through the 5 queries generated in the Plan step.
*   **Tool**: Call `tavily_client.search(query, search_depth="advanced")`. Deduplicate URLs and rank by relevance score.

### Step 3: EXTRACT
*   **Goal**: Perform "deep reading" on the top sources.
*   **Process**: Select the top 5 most relevant URLs from the Search step.
*   **Tool**:
    1.  Attempt to fetch text using `r.jina.ai/[URL]` (bypasses most JS walls, produces clean markdown).
    2.  Fallback: Use direct `requests.get()` and parse with `BeautifulSoup`, stripping out navigation, headers, scripts, etc. 

### Step 4: SYNTHESIZE
*   **Goal**: Reason over the collected data.
*   **Process**: Aggregate all the extracted text from the sources, append metadata (domain, exact URL, title), and construct a massive context prompt.

### Step 5: REPORT
*   **Goal**: Output the final structured markdown report.
*   **Process**: Pass the synthesized context buffer to the Groq LLM.
*   **Format**: The output strictly follows a predefined markdown format containing:
    *   Overview
    *   Key Findings (with in-line citations)
    *   Perspectives/Debates
    *   Recent Developments
    *   Limitations & Gaps
    *   Sources table

## Future Enhancements
*   **Agentic Reflection**: Add a step where the agent reviews its own output and triggers a second round of searches if it detects "Limitations & Gaps" that could be filled.
*   **Token Budgeting**: Implement tiktoken to truncate context windows gracefully if source extraction yields excessively long content.
