"""Prompt construction for LLM summarization."""

import datetime as dt
from typing import Sequence

from .models import Note


SUMMARY_TEMPLATE = """
You are summarizing transcripts for a knowledge worker.

Summarize the TARGET WINDOW first, but use CONTEXT notes to stitch multi-day efforts.

STRICTLY FOLLOW THIS MARKDOWN FORMAT (no preamble, no extra headings):
--------------------------------
{title_line}
<Short 2-3 sentence summary of the major items>

### Tasks Completed
- <Short 1-2 sentences describing task 1> (<note ID[s]>)
- <Short 1-2 sentences describing task 2> (<note ID[s]>)
- ...

### Remaining Action Items
- <Short 1-2 sentences describing action item 1> (<note ID[s]>)
- <Short 1-2 sentences describing action item 2> (<note ID[s]>)
- ...

--------------------------------
Rules:
- You should try to capture all tasks discussed in the notes, but don't
  overinflate the summary with too many tiny tasks.
- Group by TASK, not by date. If the same task appears across multiple days,
  output ONE bullet and optionally indicate the days in parentheses.
- You shouldcapture the main points of the tasks, but don't be overly simple
  to the point of being useless.
- Consider a task *completed* if ANY note indicates completion (e.g.,
  "finished", "completed", "finished", "done", "shipped", "fixed", "updated",
  etc.).  Otherwise keep as an action item.
- Keep bullets concise (<= 50 words when possible for simple items) and
  informative.  Include the most relevant note IDs for each bullet.
- Use the exact note IDs shown below (filenames). Do not fabricate IDs.
- Only include items that appear in the notes.

TARGET WINDOW: {target_start} to {target_end} (inclusive)
CONTEXT WINDOW: {context_start} to {target_end} (inclusive)

NOTES (each starts with an ID line):
{notes_block}
""".strip()


def build_notes_block(notes: Sequence[Note]) -> str:
    """Render notes as compact blocks the LLM can cite back by filename."""
    lines: list[str] = []
    for n in notes:
        flag = "[IN-RANGE]" if n.in_range else "[CONTEXT]"
        lines.append(f"\n# ID: {n.id}  {flag}  {n.when.isoformat(sep=' ')}\n{n.text}\n")
    return "\n".join(lines)


def build_prompt(notes: Sequence[Note], start: dt.date, end: dt.date, context_days: int) -> str:
    """Build the complete prompt for LLM summarization."""
    title_line = (
        f"## Daily Summary {start.isoformat()}"
        if start == end
        else f"## Multi-Day Summary {start.isoformat()} → {end.isoformat()}"
    )
    context_start = start - dt.timedelta(days=context_days)
    return SUMMARY_TEMPLATE.format(
        title_line=title_line,
        target_start=start.isoformat(),
        target_end=end.isoformat(),
        context_start=context_start.isoformat(),
        notes_block=build_notes_block(notes),
    )
