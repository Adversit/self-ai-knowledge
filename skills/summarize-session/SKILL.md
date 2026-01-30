skill_id: "summarize-session"
name: "Summarize Session"
command: "python scripts/summarize_session.py"
parameters: {}
created_at: "2026-01-30T00:00:00+00:00"
---

# Summarize Session

Extract summaries, action items, and knowledge candidates from AI conversation sessions.

## Description

This skill analyzes a recorded session and generates:
- A short summary (1-2 sentences)
- A detailed summary with key points
- Action items identified
- Knowledge candidates for promotion to the knowledge base

## Usage

```bash
acv summarize --session <session_id> --skill summarize-session
```

## Parameters

- `session_id`: The session to summarize
- `format`: Output format (short, detailed, json)
- `extract_candidates`: Whether to extract knowledge candidates (true/false)

## Examples

```bash
# Summarize and extract knowledge
acv summarize --session 2026-01-30T12-30-01-claude --skill summarize-session

# Short summary only
acv summarize --session 2026-01-30T12-30-01-claude --format short
```

## Notes

This skill works with sessions recorded by `acv run` command.
