#!/usr/bin/env python3
"""
Summarize Session Skill

Extract summaries, action items, and knowledge candidates from AI conversation sessions.
"""

import json
import sys
from pathlib import Path
from datetime import datetime


def summarize_session(session_data: dict) -> dict:
    """Summarize a session and extract knowledge candidates."""
    
    messages = session_data.get("messages", [])
    content_parts = []
    
    for msg in messages:
        if msg.get("role") in ["user", "assistant"]:
            content_parts.append(f"[{msg['role']}]: {msg['content']}")
    
    full_content = "\n\n".join(content_parts)
    
    # Simple extraction - in production, this would call an LLM
    short_summary = _extract_short_summary(full_content)
    detailed_summary = _extract_detailed_summary(full_content)
    action_items = _extract_action_items(full_content)
    knowledge_candidates = _extract_knowledge_candidates(full_content, session_data)
    
    return {
        "short": short_summary,
        "detailed": detailed_summary,
        "action_items": action_items,
        "knowledge_candidates": knowledge_candidates,
    }


def _extract_short_summary(content: str) -> str:
    """Extract a short summary from content."""
    # Simple heuristic - first significant paragraph
    paragraphs = [p.strip() for p in content.split("\n\n") if len(p.strip()) > 50]
    if paragraphs:
        summary = paragraphs[0][:200]
        if len(paragraphs[0]) > 200:
            summary += "..."
        return summary
    return "Session content extracted."


def _extract_detailed_summary(content: str) -> str:
    """Extract a detailed summary."""
    # Return first 3 paragraphs
    paragraphs = [p.strip() for p in content.split("\n\n") if len(p.strip()) > 50]
    return "\n\n".join(paragraphs[:3])


def _extract_action_items(content: str) -> list[str]:
    """Extract action items from content."""
    # Look for common patterns
    items = []
    lines = content.split("\n")
    for line in lines:
        line = line.strip()
        if any(keyword in line.lower() for keyword in ["todo", "action", "next step", "task"]):
            # Clean up the line
            cleaned = line.split("]", 1)[-1].strip().lstrip("-*").strip()
            if cleaned and len(cleaned) > 5:
                items.append(cleaned)
    return items[:10]


def _extract_knowledge_candidates(content: str, session_data: dict) -> list[dict]:
    """Extract potential knowledge items."""
    candidates = []
    
    # Simple heuristics for different categories
    tech_keywords = ["api", "code", "function", "error", "bug", "fix", "implement"]
    thinking_keywords = ["think", "consider", "idea", "approach", "design", "architecture"]
    source_keywords = ["source", "documentation", "reference", "link", "article"]
    
    paragraphs = [p.strip() for p in content.split("\n\n") if len(p.strip()) > 100]
    
    for i, para in enumerate(paragraphs[:5]):
        para_lower = para.lower()
        
        if any(kw in para_lower for kw in tech_keywords):
            candidates.append({
                "type": "tech_notes",
                "title": para[:60] + "...",
                "content": para,
                "tags": ["extracted"],
                "confidence": "medium",
            })
        elif any(kw in para_lower for kw in thinking_keywords):
            candidates.append({
                "type": "thinking",
                "title": para[:60] + "...",
                "content": para,
                "tags": ["extracted"],
                "confidence": "medium",
            })
        elif any(kw in para_lower for kw in source_keywords):
            candidates.append({
                "type": "trusted_sources",
                "title": para[:60] + "...",
                "content": para,
                "tags": ["extracted"],
                "confidence": "medium",
            })
    
    return candidates


def main():
    if len(sys.argv) < 2:
        print("Usage: summarize_session.py <session_json_path>")
        sys.exit(1)
    
    session_path = Path(sys.argv[1])
    if not session_path.exists():
        print(f"Error: Session file not found: {session_path}")
        sys.exit(1)
    
    with open(session_path, encoding="utf-8") as f:
        session_data = json.load(f)
    
    result = summarize_session(session_data)
    
    # Output as JSON for machine reading
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
