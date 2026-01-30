skill_id: "promote-tech-note"
name: "Promote Tech Note"
command: ""
parameters: {}
created_at: "2026-01-30T00:00:00+00:00"
---

# Promote Tech Note

Convert session content into a structured technical note in the knowledge base.

## Description

This skill takes content from a session and formats it as a tech note with:
- Proper frontmatter (id, title, date, tags, etc.)
- Markdown structure with sections
- Source session references
- Confidence and category tags

## Usage

```bash
acv promote --session <session_id> --candidate-index 0 --category tech_notes
```

## Parameters

- `session_id`: Source session ID
- `candidate_index`: Index of knowledge candidate to promote
- `category`: Target category (tech_notes, thinking, trusted_sources, skills_derived)
- `title`: Optional custom title
- `tags`: Optional comma-separated tags

## Examples

```bash
# Promote first candidate as tech note
acv promote --session 2026-01-30T12-30-01-claude --candidate-index 0 --category tech_notes

# With custom title and tags
acv promote --session 2026-01-30T12-30-01-claude --candidate-index 1 \
  --category tech_notes \
  --title "Custom Title" \
  --tags "python,api,best-practices"
```

## Output

Creates a new markdown file in `data/knowledge/<category>/YYYY/`.
