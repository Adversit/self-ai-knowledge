import json
from pathlib import Path
from typing import Any, Optional
from datetime import datetime

from .config import get_config
from .models import Skill

class SkillManager:
    def __init__(self):
        self.config = get_config()
        self.skills_dir = Path(self.config.data_paths["skills_dir"])
        self.skills_dir.mkdir(parents=True, exist_ok=True)

    def list_skills(self) -> list[dict]:
        """List all skills in the skills directory."""
        skills = []
        if not self.skills_dir.exists():
            return []

        for skill_dir in self.skills_dir.iterdir():
            if not skill_dir.is_dir():
                continue
            skill = self.load_skill(skill_dir.name)
            if skill:
                skills.append({
                    "skill_id": skill.skill_id,
                    "name": skill.name,
                    "description": skill.description,
                    "command": skill.command,
                    "created_at": skill.created_at.isoformat(),
                })
        return skills

    def load_skill(self, skill_id: str) -> Skill | None:
        """Load a skill by ID."""
        skill_dir = self.skills_dir / skill_id
        skill_md = skill_dir / "SKILL.md"

        if not skill_md.exists():
            return None

        with open(skill_md, encoding="utf-8") as f:
            content = f.read()

        # Parse frontmatter
        if content.startswith("---"):
            parts = content.split("---\n")
            if len(parts) >= 3:
                frontmatter = parts[1]
                body = parts[2]
            else:
                frontmatter = ""
                body = content
        else:
            frontmatter = ""
            body = content

        # Simple frontmatter parsing
        data = {"skill_id": skill_id}
        for line in frontmatter.split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                data[key] = value

        # Parse description from body
        description = body.strip()
        if description.startswith("# "):
            description = description[2:].strip().split("\n")[0]

        return Skill(
            skill_id=data.get("skill_id", skill_id),
            name=data.get("name", skill_id),
            description=description,
            command=data.get("command"),
            parameters=json.loads(data.get("parameters", "{}")),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
        )

    def get_skill_command(self, skill_id: str) -> Optional[str]:
        """Get the command to execute for a skill."""
        skill = self.load_skill(skill_id)
        return skill.command if skill else None

    def validate_skill(self, skill_id: str) -> dict:
        """Validate a skill structure."""
        skill_dir = self.skills_dir / skill_id
        result = {
            "skill_id": skill_id,
            "valid": True,
            "errors": [],
            "warnings": [],
            "files": [],
        }

        if not skill_dir.exists():
            result["valid"] = False
            result["errors"].append("Skill directory does not exist")
            return result

        # Check required files
        for filename in ["SKILL.md"]:
            filepath = skill_dir / filename
            result["files"].append(filename)
            if not filepath.exists():
                result["valid"] = False
                result["errors"].append(f"Missing required file: {filename}")

        # Check optional files
        for filename in ["scripts/summarize_session.py"]:
            filepath = skill_dir / filename
            result["files"].append(filename)
            if not filepath.exists():
                result["warnings"].append(f"Optional file missing: {filename}")

        return result

    def create_skill_template(
        self,
        skill_id: str,
        name: str,
        description: str,
        command: Optional[str] = None,
    ) -> Path:
        """Create a new skill from template."""
        skill_dir = self.skills_dir / skill_id
        skill_dir.mkdir(parents=True, exist_ok=True)

        skill_md_content = f'''---
skill_id: "{skill_id}"
name: "{name}"
command: "{command or ""}"
parameters: {{}}
created_at: "{datetime.now().isoformat()}"
---

# {name}

{description}

## Usage

Describe how to use this skill.

## Parameters

- `param1`: Description of parameter 1
- `param2`: Description of parameter 2

## Examples

```bash
# Example usage
```
'''

        skill_md = skill_dir / "SKILL.md"
        with open(skill_md, "w", encoding="utf-8") as f:
            f.write(skill_md_content)

        return skill_dir

    def run_skill(
        self,
        skill_id: str,
        session_data: dict,
        **kwargs,
    ) -> dict:
        """Run a skill on session data."""
        skill = self.load_skill(skill_id)
        if not skill:
            return {"error": f"Skill not found: {skill_id}"}

        # Skill execution logic would go here
        # This is a placeholder - actual implementation depends on skill type

        return {
            "skill_id": skill_id,
            "session_id": session_data.get("session_id"),
            "result": "Skill execution placeholder",
        }
