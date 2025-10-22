# Summarizer

A tool for turning daily voice transcripts into task-grouped markdown summaries.

### Why this exists:

- **Task-Grouped**: Groups notes by task rather than by date. If you work on something across multiple days, it's a single bullet.
- **Context-Aware**: Includes prior days' context to stitch multi-day efforts together.
- **Interactive Refinement**: Optional feedback loop to refine summaries with more/less detail, corrections, or different focus.
- **LLM-Powered**: Supports OpenAI and Gemini models for summarization.

## Installation

Install with `uv` (recommended):

```shell
cd summarizer
uv sync
```

Or with pip:

```shell
pip install -e .
```

## Usage

Summarize transcripts for a single date:

```shell
summarizer 2025-09-10 --input-dir ~/path/to/transcripts
```

Or a date range:

```shell
summarizer 2025-09-08:2025-09-10 --input-dir ~/path/to/transcripts
```

With interactive refinement:

```shell
summarizer 2025-09-10 --input-dir ~/path/to/transcripts --interactive
```

The tool expects JSON files with a `text` field containing transcripts. It'll parse filenames to extract dates.

### Options

- `--provider` - LLM provider: `openai` or `gemini` (default: `openai`)
- `--model` - Model name (default: `gpt-4o-mini`)
- `--api-key` - API key (otherwise reads from env: `OPENAI_API_KEY` or `GEMINI_API_KEY`)
- `--context-days` - Days of prior context to include (default: 14)
- `--max-chars` - Soft limit on prompt size (default: 120000)
- `--interactive` - Enable interactive refinement mode
- `--max-iterations` - Max refinement iterations (default: 5)

## WhisperMac Sync Setup

If you use [MacWhisper](https://goodsnooze.gumroad.com/l/macwhisper) for voice transcription, the included sync tool automatically copies new recordings to a watched directory for processing.

### Setup

Run the setup script:

```shell
cd whispermac_sync
uv run setup.py
```

The script will:
1. Prompt for source directory (defaults to MacWhisper's GlobalRecordings folder)
2. Prompt for destination directory (defaults to `global_recordings_sync_watched/` in this repo)
3. Generate the LaunchAgent plist file
4. Optionally create symlinks to `~/bin/` and `~/Library/LaunchAgents/`
5. Optionally load the LaunchAgent to start monitoring

### How it works

The LaunchAgent watches the source directory and triggers `whispermac_sync.sh` when new files appear. The script:
- Finds the newest file modified in the last minute
- Waits for the file size to stabilize (file is done writing)
- Syncs it to the destination using `rsync --ignore-existing`

Logs are written to `~/Library/Logs/whispermacsync.out.log`.

### Managing the sync

Reload the agent (after changing config):
```shell
launchctl unload ~/Library/LaunchAgents/com.user.whispermacsync.plist
launchctl load ~/Library/LaunchAgents/com.user.whispermacsync.plist
```

Stop the agent:
```shell
launchctl unload ~/Library/LaunchAgents/com.user.whispermacsync.plist
```

### Output Format

Summaries are task-grouped markdown with:
- A short 2-3 sentence overview
- **Tasks Completed** - Things you finished
- **Remaining Action Items** - Things still in progress

Example:

```markdown
## Multi-Day Summary 2025-09-08 → 2025-09-10
Worked on model training pipeline improvements and data quality issues. 
Completed the feature extraction refactor. Still working on experiment 
framework updates and documentation.

### Tasks Completed
- Refactored feature extraction pipeline for better performance (09-08, 09-09)
- Fixed data validation bug in preprocessing step (09-10)

### Remaining Action Items
- Update experiment tracking framework (09-08, 09-09)
- Complete technical documentation for new pipeline (09-09, 09-10)
```
