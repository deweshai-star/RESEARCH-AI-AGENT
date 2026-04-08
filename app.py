"""
app.py — Streamlit Web UI for the ResearchBot Agent.
Run with: streamlit run app.py
"""

import os
import time
from datetime import datetime
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from agent import ResearchAgent

# ─────────────────────────────────────────────────────────────────────────────
# Page Config
# ─────────────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="ResearchBot — AI Research Assistant",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# Custom CSS
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

  /* Base */
  html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
  }

  /* Main background */
  .stApp {
    background: linear-gradient(135deg, #0a0a1a 0%, #0d1b2a 50%, #0a0a1a 100%);
    min-height: 100vh;
  }

  /* Sidebar */
  [data-testid="stSidebar"] {
    background: rgba(15, 20, 40, 0.95);
    border-right: 1px solid rgba(99, 179, 237, 0.15);
  }

  /* Hero header */
  .hero-header {
    text-align: center;
    padding: 2.5rem 1rem 1.5rem;
    background: linear-gradient(135deg, rgba(99,179,237,0.08) 0%, rgba(139,92,246,0.08) 100%);
    border-radius: 20px;
    border: 1px solid rgba(99,179,237,0.15);
    margin-bottom: 2rem;
    backdrop-filter: blur(10px);
  }

  .hero-title {
    font-size: 3rem;
    font-weight: 700;
    background: linear-gradient(135deg, #63b3ed, #8b5cf6, #ec4899);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.5rem;
    letter-spacing: -1px;
  }

  .hero-subtitle {
    color: rgba(200, 215, 240, 0.7);
    font-size: 1.1rem;
    font-weight: 300;
    letter-spacing: 0.5px;
  }

  /* Step tracker */
  .step-container {
    display: flex;
    gap: 0.5rem;
    margin: 1rem 0;
    flex-wrap: wrap;
  }

  .step-badge {
    padding: 0.3rem 0.9rem;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.5px;
    border: 1px solid;
  }

  .step-waiting {
    background: rgba(255,255,255,0.04);
    border-color: rgba(255,255,255,0.1);
    color: rgba(255,255,255,0.35);
  }

  .step-active {
    background: rgba(139,92,246,0.2);
    border-color: rgba(139,92,246,0.6);
    color: #c4b5fd;
    animation: pulse 1.5s infinite;
  }

  .step-done {
    background: rgba(52,211,153,0.15);
    border-color: rgba(52,211,153,0.5);
    color: #6ee7b7;
  }

  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.6; }
  }

  /* Query pill */
  .query-pill {
    display: inline-block;
    background: rgba(99,179,237,0.1);
    border: 1px solid rgba(99,179,237,0.3);
    color: #93c5fd;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.82rem;
    margin: 0.2rem;
    font-family: 'JetBrains Mono', monospace;
  }

  /* Source card */
  .source-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 10px;
    padding: 0.75rem 1rem;
    margin: 0.4rem 0;
    transition: border-color 0.2s;
  }

  .source-card:hover {
    border-color: rgba(99,179,237,0.3);
  }

  .source-domain {
    font-size: 0.75rem;
    color: #6ee7b7;
    font-weight: 600;
    font-family: 'JetBrains Mono', monospace;
  }

  .source-title {
    font-size: 0.88rem;
    color: rgba(220,230,255,0.85);
    margin-top: 0.15rem;
  }

  /* Report area */
  .report-container {
    background: rgba(10, 15, 35, 0.8);
    border: 1px solid rgba(99,179,237,0.2);
    border-radius: 16px;
    padding: 2rem;
    backdrop-filter: blur(10px);
  }

  /* Input styling */
  div[data-baseweb="input"] input,
  div[data-baseweb="textarea"] textarea,
  .stTextInput input,
  .stTextArea textarea {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(99,179,237,0.25) !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
    font-family: 'Inter', sans-serif !important;
  }

  .stTextInput > div > div > input:focus,
  .stTextArea > div > div > textarea:focus {
    border-color: rgba(139,92,246,0.6) !important;
    box-shadow: 0 0 0 3px rgba(139,92,246,0.15) !important;
  }

  /* Button */
  .stButton > button {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    padding: 0.6rem 1.8rem !important;
    letter-spacing: 0.3px !important;
    transition: all 0.2s !important;
    width: 100% !important;
  }

  .stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 25px rgba(139,92,246,0.35) !important;
  }

  /* Download button */
  .stDownloadButton > button {
    background: rgba(52,211,153,0.15) !important;
    color: #6ee7b7 !important;
    border: 1px solid rgba(52,211,153,0.4) !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    width: 100% !important;
  }

  /* Stat metric */
  .stat-box {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 1rem;
    text-align: center;
  }

  .stat-number {
    font-size: 2rem;
    font-weight: 700;
    color: #8b5cf6;
  }

  .stat-label {
    font-size: 0.78rem;
    color: rgba(200,215,240,0.5);
    letter-spacing: 0.5px;
    margin-top: 0.2rem;
  }

  /* Log output */
  .log-line {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    color: rgba(200,230,200,0.75);
    padding: 0.1rem 0;
  }

  /* Divider */
  hr {
    border-color: rgba(255,255,255,0.06) !important;
  }

  /* Expander */
  .streamlit-expanderHeader {
    background: rgba(255,255,255,0.03) !important;
    border-radius: 8px !important;
    color: rgba(200,215,240,0.7) !important;
  }

  /* Success / info / warning */
  .stAlert {
    border-radius: 10px !important;
  }

  /* Scrollbar */
  ::-webkit-scrollbar { width: 4px; }
  ::-webkit-scrollbar-track { background: transparent; }
  ::-webkit-scrollbar-thumb { background: rgba(99,179,237,0.3); border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# Session State Init
# ─────────────────────────────────────────────────────────────────────────────

for key, default in {
    "report": None,
    "state": None,
    "running": False,
    "step": "idle",
    "queries": [],
    "sources": [],
    "logs": [],
    "elapsed": 0.0,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ─────────────────────────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    st.markdown("---")

    groq_key = st.text_input(
        "Groq API Key",
        value=os.getenv("GROQ_API_KEY", ""),
        type="password",
        help="Get your key at console.groq.com",
    )
    tavily_key = st.text_input(
        "Tavily API Key",
        value=os.getenv("TAVILY_API_KEY", ""),
        type="password",
        help="Get your key at tavily.com",
    )

    st.markdown("---")
    st.markdown("### 🤖 Model Info")
    st.markdown("""
    <div style='font-size:0.82rem; color:rgba(200,215,240,0.6); line-height:1.8'>
    <b style='color:#c4b5fd'>LLM:</b> Llama 3.3-70B<br>
    <b style='color:#93c5fd'>Search:</b> Tavily Advanced<br>
    <b style='color:#6ee7b7'>Extract:</b> Jina Reader + BS4<br>
    <b style='color:#f9a8d4'>Queries:</b> 5 per topic<br>
    <b style='color:#fbbf24'>Sources:</b> Top 5 URLs
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📖 How It Works")
    steps_info = [
        ("📐", "PLAN", "LLM generates 5 diverse search queries"),
        ("🔍", "SEARCH", "Tavily fetches relevant web results"),
        ("📄", "EXTRACT", "Jina Reader pulls full page content"),
        ("🧠", "SYNTHESIZE", "LLM finds key facts across sources"),
        ("📋", "REPORT", "Structured markdown report generated"),
    ]
    for icon, name, desc in steps_info:
        st.markdown(f"""
        <div style='margin:0.4rem 0; font-size:0.8rem'>
          <span style='color:#8b5cf6;font-weight:700'>{icon} {name}</span>
          <span style='color:rgba(200,215,240,0.5);margin-left:0.4rem'>{desc}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    if st.session_state.report:
        filename = f"research_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        st.download_button(
            label="⬇️ Download Report (.md)",
            data=st.session_state.report,
            file_name=filename,
            mime="text/markdown",
        )

# ─────────────────────────────────────────────────────────────────────────────
# Main Content
# ─────────────────────────────────────────────────────────────────────────────

# Hero
st.markdown("""
<div class="hero-header">
  <div class="hero-title">🔬 ResearchBot</div>
  <div class="hero-subtitle">Autonomous AI Research Agent · Powered by Groq + Tavily</div>
</div>
""", unsafe_allow_html=True)

# Topic Input
col_input, col_btn = st.columns([5, 1])

with col_input:
    topic = st.text_input(
        "Research Topic",
        placeholder='e.g. "Quantum computing breakthroughs in 2025"',
        label_visibility="collapsed",
    )

with col_btn:
    run_btn = st.button("🚀 Research", disabled=st.session_state.running)

# Example topics
st.markdown("""
<div style='margin:-0.5rem 0 1.5rem; font-size:0.8rem; color:rgba(200,215,240,0.4)'>
  Try: <span style='color:#93c5fd'>Quantum computing 2025</span> · 
  <span style='color:#93c5fd'>AI regulation in Europe</span> · 
  <span style='color:#93c5fd'>Climate change adaptation strategies</span> · 
  <span style='color:#93c5fd'>CRISPR gene editing latest</span>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# Agent Execution
# ─────────────────────────────────────────────────────────────────────────────

STEP_ORDER = ["plan", "search", "extract", "report"]
STEP_LABELS = {
    "plan":   "📐 Plan",
    "search": "🔍 Search",
    "extract":"📄 Extract",
    "report": "📋 Report",
}

def render_step_tracker(current: str):
    badges = []
    reached = False
    for s in STEP_ORDER:
        if s == current:
            reached = True
            cls = "step-active"
        elif not reached:
            cls = "step-done"
        else:
            cls = "step-waiting"
        badges.append(f'<span class="step-badge {cls}">{STEP_LABELS[s]}</span>')
    st.markdown(
        f'<div class="step-container">{"".join(badges)}</div>',
        unsafe_allow_html=True,
    )

if run_btn and topic.strip():
    if not groq_key or not tavily_key:
        st.error("⚠️ Please enter your Groq and Tavily API keys in the sidebar.")
    else:
        # Reset state
        st.session_state.report = None
        st.session_state.queries = []
        st.session_state.sources = []
        st.session_state.logs = []
        st.session_state.running = True
        st.session_state.step = "plan"

        agent = ResearchAgent(groq_key, tavily_key)

        start_time = time.time()

        # Live progress containers
        st.markdown("### 🔄 Agent Running...")
        progress_bar = st.progress(0)
        step_placeholder = st.empty()
        status_placeholder = st.empty()
        queries_placeholder = st.empty()
        sources_placeholder = st.empty()

        def on_progress(step, data):
            step_idx = STEP_ORDER.index(step) if step in STEP_ORDER else 0
            progress = int((step_idx + 1) / len(STEP_ORDER) * 100)
            progress_bar.progress(progress)

            with step_placeholder.container():
                render_step_tracker(step)

            if step == "plan":
                st.session_state.queries = data
                pills = "".join(
                    f'<span class="query-pill">🔎 {q}</span>'
                    for q in data
                )
                queries_placeholder.markdown(
                    f"**Generated Queries:**<br>{pills}",
                    unsafe_allow_html=True,
                )

            elif step == "extract":
                src = data.get("source")
                if src:
                    st.session_state.sources.append(src)
                    cards = "".join(
                        f"""<div class='source-card'>
                              <div class='source-domain'>🌐 {s.domain}</div>
                              <div class='source-title'>{s.title[:80]}</div>
                            </div>"""
                        for s in st.session_state.sources
                    )
                    sources_placeholder.markdown(
                        f"**Extracted Sources ({len(st.session_state.sources)}):** {cards}",
                        unsafe_allow_html=True,
                    )

        try:
            research_state = agent.research(topic.strip(), on_progress=on_progress)
            elapsed = time.time() - start_time

            st.session_state.report = research_state.report
            st.session_state.state = research_state
            st.session_state.elapsed = elapsed
            st.session_state.running = False

            progress_bar.progress(100)
            step_placeholder.empty()
            status_placeholder.success(
                f"✅ Research complete in {elapsed:.1f}s  ·  "
                f"{len(research_state.sources)} sources  ·  "
                f"{len(research_state.queries)} queries"
            )

        except Exception as e:
            st.session_state.running = False
            st.error(f"❌ Agent error: {str(e)}")
            import traceback
            with st.expander("Stack Trace"):
                st.code(traceback.format_exc())

# ─────────────────────────────────────────────────────────────────────────────
# Report Display
# ─────────────────────────────────────────────────────────────────────────────

if st.session_state.report:
    st.markdown("---")

    # Stats row
    state = st.session_state.state
    c1, c2, c3, c4 = st.columns(4)
    stats = [
        (c1, len(state.queries),  "Queries Run"),
        (c2, len(state.sources),  "Sources Read"),
        (c3, len(state.report.split()), "Report Words"),
        (c4, f"{st.session_state.elapsed:.1f}s", "Time Taken"),
    ]
    for col, val, label in stats:
        with col:
            st.markdown(f"""
            <div class='stat-box'>
              <div class='stat-number'>{val}</div>
              <div class='stat-label'>{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # Two-column layout: Report + Sources
    col_report, col_meta = st.columns([3, 1])

    with col_report:
        st.markdown("### 📋 Research Report")
        st.markdown(
            f'<div class="report-container">{st.session_state.report}</div>',
            unsafe_allow_html=True,
        )

    with col_meta:
        st.markdown("### 📚 Sources Used")
        for i, src in enumerate(state.sources, 1):
            with st.expander(f"{i}. {src.title[:45]}..."):
                st.markdown(f"**Domain:** `{src.domain}`")
                st.markdown(f"**URL:** {src.url}")
                st.markdown(f"**Snippet:** {src.snippet[:200]}...")

        st.markdown("---")
        st.markdown("### 🔎 Queries Used")
        for i, q in enumerate(state.queries, 1):
            st.markdown(f"`{i}.` {q}")

        st.markdown("---")
        st.markdown("### ⬇️ Export")
        filename = f"research_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        st.download_button(
            label="Download as Markdown",
            data=st.session_state.report,
            file_name=filename,
            mime="text/markdown",
        )

    # Raw logs
    with st.expander("🖥️ Agent Execution Log"):
        log_text = "\n".join(state.logs)
        st.code(log_text, language=None)

elif not st.session_state.running:
    # Empty state
    st.markdown("""
    <div style='text-align:center; padding:4rem 2rem; color:rgba(200,215,240,0.3)'>
      <div style='font-size:4rem; margin-bottom:1rem'>🔬</div>
      <div style='font-size:1.2rem; font-weight:500'>Enter a topic above to begin</div>
      <div style='font-size:0.9rem; margin-top:0.5rem'>
        The agent will plan, search, extract, synthesize, and report — all automatically.
      </div>
    </div>
    """, unsafe_allow_html=True)
