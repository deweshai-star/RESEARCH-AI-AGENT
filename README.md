# 🔬 ResearchBot — AI Research Agent

An autonomous AI research assistant that takes a topic, searches the web for recent information, extracts key facts, and produces a structured summary report with citations.

> **Built to demonstrate all 3 pillars of agent behavior:**
> - 🧠 **Reasoning** — decides what to search, evaluates results
> - 🔧 **Tool Use** — web search + content extraction
> - 📋 **Structured Output** — formatted research report with sources

---

## ✨ Features

- **5-Step Agentic Pipeline**: Plan → Search → Extract → Synthesize → Report
- **Multi-Query Search**: LLM generates 5 diverse search queries per topic
- **Smart Extraction**: Jina Reader API with BeautifulSoup fallback
- **Grounded Reports**: Every claim is cited with a verifiable source URL
- **Beautiful Streamlit UI**: Dark-themed, real-time progress tracking
- **CLI Support**: Run research from the command line
- **Export**: Download reports as Markdown files

---

## 🏗️ Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   User Input │────▶│  STEP 1:     │────▶│  STEP 2:     │
│   (Topic)    │     │  PLAN        │     │  SEARCH      │
│              │     │  (Groq LLM)  │     │  (Tavily)    │
└──────────────┘     └──────────────┘     └──────────────┘
                                                │
                     ┌──────────────┐     ┌─────▼────────┐
                     │  STEP 4+5:   │◀────│  STEP 3:     │
                     │  SYNTHESIZE  │     │  EXTRACT     │
                     │  + REPORT    │     │  (Jina/BS4)  │
                     │  (Groq LLM)  │     └──────────────┘
                     └──────┬───────┘
                            │
                     ┌──────▼───────┐
                     │  Structured  │
                     │  Markdown    │
                     │  Report      │
                     └──────────────┘
```

---

## 🛠️ Tech Stack

| Component       | Technology                    |
|-----------------|-------------------------------|
| **LLM**         | Groq API (Llama 3.3-70B)      |
| **Web Search**  | Tavily Advanced Search API    |
| **Extraction**  | Jina Reader + BeautifulSoup   |
| **Frontend**    | Streamlit                     |
| **Language**    | Python 3.10+                  |

---

## 🚀 Quick Start

### 1. Clone the repo
```bash
git clone https://github.com/deweshai-star/RESEARCH-AI-AGENT.git
cd RESEARCH-AI-AGENT
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up API keys
Create a `.env` file in the project root:
```env
GROQ_API_KEY=your_groq_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

> 🔑 Get your keys:
> - **Groq**: [console.groq.com](https://console.groq.com)
> - **Tavily**: [tavily.com](https://tavily.com)

### 4. Run the app

**Streamlit UI (recommended):**
```bash
python -m streamlit run app.py
```

**Command Line:**
```bash
python main.py "Quantum computing breakthroughs in 2025"
```

---

## 📄 Project Structure

```
RESEARCH-AI-AGENT/
├── agent.py           # Core 5-step research agent pipeline
├── tools.py           # Web search & content extraction tools
├── app.py             # Streamlit web UI
├── main.py            # CLI entry point
├── plan.md            # Detailed architecture plan
├── requirements.txt   # Python dependencies
├── .streamlit/
│   └── config.toml    # Streamlit dark theme config
├── .env               # API keys (not committed)
└── .gitignore
```

---

## 📋 Report Format

Every generated report includes:
- **Overview** — What the topic is and why it matters
- **Key Findings** — 5-7 grounded facts with source citations
- **Perspectives & Debates** — Conflicting viewpoints if any
- **Recent Developments** — Latest news with dates
- **Limitations & Gaps** — Honest assessment of missing info
- **Sources Table** — All URLs used, organized by relevance
- **Tags** — Keywords for the topic

---

## ⚠️ Guardrails

The agent follows strict rules to ensure quality:
- ❌ Never fabricates statistics or quotes
- ❌ Never cites a URL it hasn't actually read
- ✅ Prefers recent sources (last 12 months)
- ✅ Prioritizes .gov, .edu, and established outlets
- ✅ Flags gaps and missing information honestly

---

## 📜 License

MIT License — feel free to use, modify, and distribute.

---

<p align="center">
  Built with ❤️ using Groq + Tavily + Streamlit
</p>
