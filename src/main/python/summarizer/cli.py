"""Command-line interface for the summarizer tool."""

import argparse
import datetime as dt
from pathlib import Path
from typing import Optional, Sequence

from .file_ops import find_notes, trim_notes
from .llm_clients import make_client
from .prompts import build_prompt
from .feedback import interactive_refinement_loop


def parse_date_or_range(spec: str) -> tuple[dt.date, dt.date]:
    """Accept 'YYYY-MM-DD' or 'YYYY-MM-DD:YYYY-MM-DD'."""
    if ":" in spec:
        a, b = spec.split(":", 1)
        start = dt.date.fromisoformat(a)
        end = dt.date.fromisoformat(b)
    else:
        start = end = dt.date.fromisoformat(spec)
    if end < start:
        raise SystemExit("End date precedes start date.")
    return start, end


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description=("Summarize JSON transcripts into a task-grouped Markdown "
                     "report with optional interactive refinement")
    )
    parser.add_argument(
        "date_or_range",
        help="Date (YYYY-MM-DD) or range (YYYY-MM-DD:YYYY-MM-DD)",
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path.cwd(),
        help="Directory containing JSON transcript files",
    )
    parser.add_argument(
        "--provider",
        default="openai",
        help="LLM provider: openai | gemini",
    )
    parser.add_argument(
        "--model",
        default="gpt-4o-mini",
        help="Model name for the chosen provider",
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help="Optional API key (otherwise read from env var)",
    )
    parser.add_argument(
        "--context-days",
        type=int,
        default=14,
        help="Days of prior context to include (default: 14)",
    )
    parser.add_argument(
        "--max-chars",
        type=int,
        default=120_000,
        help="Soft limit on prompt size; older CONTEXT notes are dropped first",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Enable interactive feedback mode for summary refinement",
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=5,
        help="Maximum number of refinement iterations (default: 5)",
    )

    args = parser.parse_args(argv)

    start, end = parse_date_or_range(args.date_or_range)
    notes = find_notes(
        args.input_dir, start, end, context_days=args.context_days
    )

    if not notes:
        print("No transcripts found in the specified window.")
        return 1

    # Fit notes to a simple char budget to avoid over-long prompts.
    notes = trim_notes(notes, args.max_chars)

    prompt = build_prompt(
        notes, start=start, end=end, context_days=args.context_days
    )

    client = make_client(args.provider, args.model, args.api_key)
    initial_summary = client.complete(prompt)

    # Use interactive refinement if requested
    if args.interactive:
        print("Initial summary generated. Starting interactive refinement...")
        summary_md = interactive_refinement_loop(
            initial_summary, client, max_iterations=args.max_iterations
        )
    else:
        summary_md = initial_summary
        print(summary_md)

    # Offer to save
    try:
        choice = input(
            "\nSave this summary to a Markdown file? [y/N]: "
        ).strip().lower()
    except EOFError:
        choice = "n"
    if choice == "y":
        out_dir = Path("summaries")
        out_dir.mkdir(parents=True, exist_ok=True)
        suffix = (
            start.isoformat()
            if start == end
            else f"{start.isoformat()}_to_{end.isoformat()}"
        )
        out_path = out_dir / f"summary_{suffix}.md"
        out_path.write_text(summary_md, encoding="utf-8")
        print(f"Saved: {out_path.resolve()}")

    return 0
