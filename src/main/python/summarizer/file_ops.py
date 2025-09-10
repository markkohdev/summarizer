"""File operations and parsing for transcript files."""

import datetime as dt
import json
import re
import sys
from pathlib import Path
from typing import List, Optional, Tuple

from .models import Note


FILENAME_TS = re.compile(r"\((\d{4}-\d{2}-\d{2}) (\d{2})\.(\d{2})\.(\d{2})\)")


def parse_filename_dt(filename: str) -> Optional[dt.datetime]:
    """Extract a naive datetime from filenames like 'Global (YYYY-MM-DD HH.MM.SS).json'."""
    m = FILENAME_TS.search(filename)
    if not m:
        return None
    ymd, hh, mm, ss = m.group(1), m.group(2), m.group(3), m.group(4)
    return dt.datetime.strptime(
        f"{ymd} {hh}:{mm}:{ss}", "%Y-%m-%d %H:%M:%S"
    )


def load_note(path: Path) -> Optional[Tuple[str, str]]:
    """Return (id, text) by concatenating all 'text' fields found in the JSON list.

    The JSON format is expected to be a list[ { 'text': ... }, ... ]. Unknown
    items are ignored.
    """
    try:
        blobs = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:  # pragma: no cover - IO path
        print(
            f"Warning: failed to read {path.name}: {e}",
            file=sys.stderr
        )
        return None
    texts: List[str] = []
    if isinstance(blobs, list):
        for obj in blobs:
            if isinstance(obj, dict) and isinstance(obj.get("text"), str):
                texts.append(obj["text"].strip())
    content = "\n\n".join(t for t in texts if t)
    return (path.name, content) if content else None


def find_notes(
    input_dir: Path,
    start: dt.date,
    end: dt.date,
    context_days: int = 14,
) -> List[Note]:
    """Scan input_dir for JSON transcripts within [start - context_days, end]."""
    context_start = start - dt.timedelta(days=context_days)
    notes: List[Note] = []

    for path in sorted(input_dir.glob("*.json")):
        when = parse_filename_dt(path.name)
        if not when:
            continue
        d = when.date()
        if not (context_start <= d <= end):
            continue
        loaded = load_note(path)
        if not loaded:
            continue
        nid, text = loaded
        notes.append(
            Note(id=nid, when=when, text=text, in_range=(start <= d <= end))
        )

    return notes


def trim_notes(notes: List[Note], max_chars: int) -> List[Note]:
    """Fit notes to a simple char budget to avoid over-long prompts.
    
    Prefer keeping IN-RANGE notes; drop oldest CONTEXT notes first.
    """
    if sum(len(n.text) for n in notes) <= max_chars:
        return notes
    in_range = [n for n in notes if n.in_range]
    context = [n for n in notes if not n.in_range]
    context.sort(key=lambda n: n.when)  # oldest first
    while context and (
        sum(len(n.text) for n in in_range + context) > max_chars
    ):
        context.pop(0)  # drop oldest context
    return in_range + context
