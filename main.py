"""
main.py — CLI entry point for ResearchBot.
Usage: python main.py "Your research topic here"
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from agent import ResearchAgent


def save_report(report: str, topic: str) -> Path:
    """Save the report as a markdown file in a reports/ folder."""
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)

    safe_name = "".join(c if c.isalnum() or c in " -_" else "_" for c in topic)
    safe_name = safe_name[:50].strip().replace(" ", "_")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = reports_dir / f"{timestamp}_{safe_name}.md"

    filename.write_text(report, encoding="utf-8")
    return filename


def main():
    parser = argparse.ArgumentParser(
        description="ResearchBot — AI-powered web research agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py "Quantum computing breakthroughs 2025"
  python main.py "AI regulation in Europe" --save
  python main.py "Climate change adaptation" --no-save
        """
    )
    parser.add_argument("topic", help="The research topic to investigate")
    parser.add_argument("--save", action="store_true", default=True,
                        help="Save report to file (default: True)")
    parser.add_argument("--no-save", action="store_true", default=False,
                        help="Don't save report to file")
    args = parser.parse_args()

    groq_key = os.getenv("GROQ_API_KEY")
    tavily_key = os.getenv("TAVILY_API_KEY")

    if not groq_key:
        print("❌ ERROR: GROQ_API_KEY not found in .env or environment")
        sys.exit(1)
    if not tavily_key:
        print("❌ ERROR: TAVILY_API_KEY not found in .env or environment")
        sys.exit(1)

    agent = ResearchAgent(groq_key, tavily_key)

    try:
        state = agent.research(args.topic)

        print("\n" + "="*60)
        print(state.report)
        print("="*60)

        should_save = args.save and not args.no_save
        if should_save:
            path = save_report(state.report, args.topic)
            print(f"\n💾 Report saved to: {path}")

    except KeyboardInterrupt:
        print("\n\n⚠️ Research interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error during research: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
