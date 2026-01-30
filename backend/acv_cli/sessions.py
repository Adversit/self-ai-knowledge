import json
from datetime import datetime
from pathlib import Path
from typing import Any

from .config import get_config

class SessionManager:
    def __init__(self):
        self.config = get_config()
        self.sessions_dir = Path(self.config.data_paths["sessions_dir"])
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

    def save_session(self, session_data: dict) -> str:
        """Save session to JSON and generate markdown transcript."""
        session_id = session_data["session_id"]
        date_str = session_id[:10]  # YYYY-MM-DD
        month_dir = self.sessions_dir / date_str
        month_dir.mkdir(parents=True, exist_ok=True)

        # Save JSON
        json_path = month_dir / f"{session_id}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)

        # Generate markdown transcript
        md_path = month_dir / f"{session_id}.md"
        self._generate_markdown(session_data, md_path)

        return str(json_path)

    def load_session(self, session_id: str) -> dict | None:
        """Load session by ID."""
        date_str = session_id[:10]
        month_dir = self.sessions_dir / date_str
        json_path = month_dir / f"{session_id}.json"

        if json_path.exists():
            with open(json_path, encoding="utf-8") as f:
                return json.load(f)
        return None

    def list_sessions(self, limit: int = 50, model_source: str | None = None) -> list[dict]:
        """List recent sessions."""
        sessions = []
        sessions_dir = Path(self.config.data_paths["sessions_dir"])

        if not sessions_dir.exists():
            return []

        for month_dir in sorted(sessions_dir.iterdir(), reverse=True):
            if not month_dir.is_dir():
                continue
            for json_file in sorted(month_dir.glob("*.json"), reverse=True):
                with open(json_file, encoding="utf-8") as f:
                    data = json.load(f)
                    if model_source and data.get("model_source") != model_source:
                        continue
                    sessions.append({
                        "session_id": data["session_id"],
                        "created_at": data["created_at"],
                        "model_source": data["model_source"],
                        "project": data.get("project"),
                        "tags": data.get("tags", []),
                    })
                    if len(sessions) >= limit:
                        return sessions

        return sessions[:limit]

    def _generate_markdown(self, session_data: dict, md_path: Path) -> None:
        """Generate readable markdown transcript."""
        session_id = session_data["session_id"]
        model = session_data.get("model_source", "unknown")
        project = session_data.get("project")
        tags = session_data.get("tags", [])

        lines = [
            f"# Session: {session_id}",
            "",
            f"**Model:** {model}",
            f"**Date:** {session_data['created_at']}",
        ]

        if project:
            lines.append(f"**Project:** {project}")
        if tags:
            lines.append(f"**Tags:** {', '.join(tags)}")

        lines.extend([
            "",
            "---",
            "",
            "## Conversation",
            "",
        ])

        for msg in session_data.get("messages", []):
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            timestamp = msg.get("timestamp", "")

            if role == "system":
                continue

            role_icon = {
                "user": "👤",
                "assistant": "🤖",
                "system": "⚙️",
            }.get(role, "•")

            lines.append(f"### {role_icon} {role.upper()}")
            lines.append(f"_{timestamp}_")
            lines.append("")
            lines.append(content)
            lines.append("")

        md_content = "\n".join(lines)
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(md_content)
