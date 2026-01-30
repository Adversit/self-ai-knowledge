import json
import re
from datetime import datetime
from pathlib import Path
from typing import Optional
import uuid

from .config import get_config
from .models import KnowledgeItem, Category, Confidence

class KnowledgeManager:
    def __init__(self):
        self.config = get_config()
        self.knowledge_dir = Path(self.config.data_paths["knowledge_dir"])
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """Create all category directories."""
        for category in Category:
            dir_path = self.knowledge_dir / category.value
            dir_path.mkdir(parents=True, exist_ok=True)

    def get_category_path(self, category: Category) -> Path:
        return self.knowledge_dir / category.value

    def create_knowledge_item(
        self,
        title: str,
        content: str,
        category: Category,
        source_sessions: list[str],
        model_sources: list[str],
        tags: list[str] | None = None,
        confidence: Confidence = Confidence.MEDIUM,
        generated_by_skill: str | None = None,
    ) -> tuple[KnowledgeItem, str]:
        """Create a new knowledge item and save to disk."""
        date = datetime.now()
        item_id = f"{category.value}-{date.strftime('%Y-%m-%d')}-{uuid.uuid4().hex[:8]}"
        
        item = KnowledgeItem(
            id=item_id,
            title=title,
            date=date,
            category=category,
            tags=tags or [],
            source_sessions=source_sessions,
            model_sources=model_sources,
            confidence=confidence,
            generated_by_skill=generated_by_skill,
            summary=self._extract_summary(content),
        )

        # Save to markdown file
        category_path = self.get_category_path(category)
        year_dir = category_path / date.strftime("%Y")
        year_dir.mkdir(parents=True, exist_ok=True)

        md_path = year_dir / f"{item_id}.md"
        self._save_markdown(item, content, md_path)

        return item, str(md_path)

    def _extract_summary(self, content: str, max_length: int = 200) -> str:
        """Extract a brief summary from content."""
        # Remove markdown formatting
        text = re.sub(r'[#*`\[\]]', '', content)
        text = text.strip()
        if len(text) <= max_length:
            return text
        return text[:max_length].rstrip() + "..."

    def _save_markdown(self, item: KnowledgeItem, content: str, path: Path) -> None:
        """Save knowledge item with YAML frontmatter."""
        frontmatter = [
            "---",
            f'id: "{item.id}"',
            f'title: "{item.title}"',
            f'date: "{item.date.isoformat()}"',
            f'source_sessions: {json.dumps(item.source_sessions)}',
            f'model_sources: {json.dumps(item.model_sources)}',
            f'tags: {json.dumps(item.tags)}',
            f'category: "{item.category.value}"',
            f'confidence: "{item.confidence.value}"',
        ]
        if item.generated_by_skill:
            frontmatter.append(f'generated_by_skill: "{item.generated_by_skill}"')
        frontmatter.append("---")

        full_content = "\n".join(frontmatter) + "\n\n" + content
        with open(path, "w", encoding="utf-8") as f:
            f.write(full_content)

    def load_knowledge_item(self, item_id: str) -> tuple[KnowledgeItem | None, str | None]:
        """Load knowledge item by ID."""
        for category in Category:
            category_path = self.get_category_path(category)
            for year_dir in category_path.iterdir():
                if not year_dir.is_dir():
                    continue
                md_path = year_dir / f"{item_id}.md"
                if md_path.exists():
                    return self._parse_markdown(md_path), str(md_path)
        return None, None

    def _parse_markdown(self, path: Path) -> KnowledgeItem | None:
        """Parse markdown file with frontmatter."""
        with open(path, encoding="utf-8") as f:
            content = f.read()

        # Split frontmatter and content
        parts = content.split("---\n")
        if len(parts) < 3:
            return None

        frontmatter = parts[1].strip()
        body = "---\n".join(parts[2:]).strip()

        # Parse YAML frontmatter
        data = {}
        for line in frontmatter.split("\n"):
            line = line.strip()
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            
            if value.startswith("[") and value.endswith("]"):
                value = json.loads(value.replace("'", '"'))
            data[key] = value

        return KnowledgeItem(
            id=data.get("id", path.stem),
            title=data.get("title", path.stem),
            date=datetime.fromisoformat(data.get("date", path.stat().st_mtime)),
            category=Category(data.get("category", "tech_notes")),
            tags=data.get("tags", []),
            source_sessions=data.get("source_sessions", []),
            model_sources=data.get("model_sources", []),
            confidence=Confidence(data.get("confidence", "medium")),
            generated_by_skill=data.get("generated_by_skill"),
            summary=data.get("summary"),
        )

    def list_knowledge_items(
        self,
        category: Category | None = None,
        limit: int = 50,
    ) -> list[dict]:
        """List knowledge items."""
        items = []
        search_dir = self.knowledge_dir
        if category:
            search_dir = search_dir / category.value

        if not search_dir.exists():
            return []

        for year_dir in sorted(search_dir.iterdir(), reverse=True):
            if not year_dir.is_dir():
                continue
            for md_file in sorted(year_dir.glob("*.md"), reverse=True):
                item = self._parse_markdown(md_file)
                if item:
                    items.append({
                        "id": item.id,
                        "title": item.title,
                        "date": item.date.isoformat(),
                        "category": item.category.value,
                        "tags": item.tags,
                        "summary": item.summary,
                        "confidence": item.confidence.value,
                    })
                if len(items) >= limit:
                    return items

        return items[:limit]
