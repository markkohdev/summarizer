"""Summarizer package for processing transcript notes into task-grouped reports.

This package provides functionality to:
- Parse JSON transcript files with timestamped filenames
- Summarize notes using various LLM providers (OpenAI, Gemini)
- Generate task-grouped Markdown reports
- Support both single-day and multi-day summaries

Usage examples:
  # single day (defaults to local timezone of the machine)
  summarizer 2025-09-05 --input-dir ./notes --provider openai \
    --model gpt-4o-mini

  # date range (inclusive)
  summarizer 2025-09-05:2025-09-09 --input-dir ./notes --provider gemini \
    --model gemini-1.5-pro

  # interactive mode for refinement
  summarizer 2025-09-05 --interactive --max-iterations 3

Provider/API keys:
  - OpenAI (ChatGPT): set environment variable OPENAI_API_KEY (or pass \
    --api-key)
    pip install openai
  - Google Gemini: set environment variable GOOGLE_API_KEY (or pass --api-key)
    pip install google-generativeai

Notes directory:
  - The script scans for files whose names contain an ISO date of the form
    "(YYYY-MM-DD HH.MM.SS)" (e.g., Global (2025-09-05 13.42.00).json).
  - Each JSON file is expected to be a list of objects with a 'text' field.

Prompting behavior:
  - For a SINGLE date, the report title is "## Daily Summary YYYY-MM-DD".
  - For a DATE RANGE, the title is "## Multi-Day Summary YYYY-MM-DD → YYYY-MM-DD".
  - The model is explicitly instructed to:
      * Group by TASK rather than date.
      * Mark a task as completed if ANY note indicates completion.
      * Append note ID(s) (the filenames) in parentheses for each bullet.
      * Put unresolved items in "Remaining Action Items".
      * Keep the top blurb short (2–3 sentences).

Implementation notes:
  - The LLM client is provider-pluggable; extend LLMClient if you use another
    vendor.
  - Context window: by default, the model sees all notes within the selected
    dates PLUS up to N days of prior context (default 14) to help stitch
    multi-day tasks.
"""

__version__ = "0.1.0"

from .cli import main
from .feedback import interactive_refinement_loop, get_user_feedback, refine_summary

__all__ = ["main", "interactive_refinement_loop", "get_user_feedback", "refine_summary"]
