import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Any
from contextlib import asynccontextmanager

from .models import KnowledgeItem, Category

class Database:
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Knowledge items table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_items (
                id TEXT PRIMARY KEY,
                path TEXT NOT NULL,
                title TEXT NOT NULL,
                date TEXT NOT NULL,
                category TEXT NOT NULL,
                tags TEXT,
                summary TEXT,
                confidence TEXT,
                generated_by_skill TEXT,
                model_sources TEXT
            )
        """)

        # Sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                model_source TEXT NOT NULL,
                model_variant TEXT,
                project TEXT,
                tags TEXT,
                summaries TEXT
            )
        """)

        # FTS5 full-text search
        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS knowledge_items_fts USING fts5(
                id, title, summary, content,
                content='knowledge_items',
                content_rowid='rowid'
            )
        """)

        conn.commit()
        conn.close()

    def add_knowledge_item(self, item: KnowledgeItem, path: str) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO knowledge_items
            (id, path, title, date, category, tags, summary, confidence, generated_by_skill, model_sources)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            item.id,
            path,
            item.title,
            item.date.isoformat(),
            item.category.value,
            json.dumps(item.tags),
            item.summary,
            item.confidence.value,
            item.generated_by_skill,
            json.dumps(item.model_sources),
        ))

        # Update FTS index
        cursor.execute("""
            INSERT INTO knowledge_items_fts(knowledge_items_fts, id, title, summary)
            VALUES('rebuild', ?, ?, ?)
        """, (item.id, item.title, item.summary or ""))

        conn.commit()
        conn.close()

    def search(self, query: str, limit: int = 20, category: Category | None = None) -> list[dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        sql = """
            SELECT id, path, title, date, category, tags, summary, confidence, generated_by_skill
            FROM knowledge_items
        """
        params = []

        if category:
            sql += " WHERE category = ?"
            params.append(category.value)

        if query:
            if category:
                sql += " AND"
            else:
                sql += " WHERE"
            sql += " title LIKE ? OR summary LIKE ?"
            params.extend([f"%{query}%", f"%{query}%"])

        sql += " ORDER BY date DESC LIMIT ?"
        params.append(limit)

        cursor.execute(sql, params)
        rows = cursor.fetchall()
        conn.close()

        return [dict(zip(
            ["id", "path", "title", "date", "category", "tags", "summary", "confidence", "generated_by_skill"],
            row
        )) for row in rows]

    def search_fts(self, query: str, limit: int = 20) -> list[dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, path, title, summary, category
            FROM knowledge_items_fts
            WHERE knowledge_items_fts MATCH ?
            ORDER BY rank
            LIMIT ?
        """, (query, limit))

        rows = cursor.fetchall()
        conn.close()

        return [dict(zip(["id", "path", "title", "summary", "category"], row)) for row in rows]

    def add_session(self, session_data: dict) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO sessions
            (session_id, created_at, model_source, model_variant, project, tags, summaries)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            session_data["session_id"],
            session_data["created_at"],
            session_data["model_source"],
            session_data.get("model_variant"),
            session_data.get("project"),
            json.dumps(session_data.get("tags", [])),
            json.dumps(session_data.get("summaries", {})),
        ))

        conn.commit()
        conn.close()

    def get_session(self, session_id: str) -> dict | None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            columns = ["session_id", "created_at", "model_source", "model_variant", "project", "tags", "summaries"]
            return dict(zip(columns, row))
        return None

    def list_sessions(self, limit: int = 50, model_source: str | None = None) -> list[dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        sql = "SELECT * FROM sessions"
        params = []
        if model_source:
            sql += " WHERE model_source = ?"
            params.append(model_source)
        sql += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        cursor.execute(sql, params)
        rows = cursor.fetchall()
        conn.close()

        columns = ["session_id", "created_at", "model_source", "model_variant", "project", "tags", "summaries"]
        return [dict(zip(columns, row)) for row in rows]

    def get_stats(self) -> dict:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM knowledge_items")
        knowledge_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM sessions")
        session_count = cursor.fetchone()[0]

        cursor.execute("""
            SELECT category, COUNT(*) FROM knowledge_items GROUP BY category
        """)
        by_category = dict(cursor.fetchall())

        conn.close()

        return {
            "knowledge_items": knowledge_count,
            "sessions": session_count,
            "by_category": by_category,
        }
