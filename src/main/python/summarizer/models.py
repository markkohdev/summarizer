"""Data models for the summarizer tool."""

import dataclasses
import datetime as dt


@dataclasses.dataclass(frozen=True)
class Note:
    """A single transcript note extracted from a JSON file."""
    id: str                 # filename (used as the reference ID)
    when: dt.datetime       # parsed from the filename (local naive datetime)
    text: str               # concatenated text from the JSON payload
    in_range: bool          # True if inside the requested target window
