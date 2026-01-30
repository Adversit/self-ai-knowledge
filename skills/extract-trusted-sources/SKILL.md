skill_id: "extract-trusted-sources"
name: "Extract Trusted Sources"
command: ""
parameters: {}
created_at: "2026-01-30T00:00:00+00:00"
---

# Extract Trusted Sources

Identify and extract trusted information sources from AI conversations.

## Description

This skill scans conversation sessions and extracts:
- URLs and links mentioned
- Documentation references
- Official sources and authoritative content
- Code examples with attribution

## Usage

```bash
acv summarize --session <session_id> --skill extract-trusted-sources
```

## What It Looks For

- HTTP/HTTPS URLs
- GitHub repository references
- Documentation site mentions
- Official API documentation
- Academic papers and citations

## Output Format

Each source is extracted as a `trusted_sources` knowledge item with:
- Full URL/path
- Context from the conversation
- Confidence score based on verification status
