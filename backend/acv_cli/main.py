#!/usr/bin/env python3
"""Self-AI-Knowledge CLI - Multi-model AI knowledge base and skill hub."""

import typer
from typing import Optional
from pathlib import Path
import json
import logging

from .config import get_config
from .subprocess_wrap import SubprocessWrapper
from .sessions import SessionManager
from .knowledge import KnowledgeManager
from .skills import SkillManager
from .db import Database

app = typer.Typer(
    name="acv",
    help="Self-AI-Knowledge: Multi-model AI knowledge base and skill hub",
    add_completion=False,
)

# Initialize managers
config = get_config()
db = Database(config.data_paths["db_path"])
session_mgr = SessionManager()
knowledge_mgr = KnowledgeManager()
skill_mgr = SkillManager()

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.logging.get("log_level", "INFO")),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def _on_message(msg: dict) -> None:
    """Callback for subprocess messages."""
    if msg["type"] == "message":
        # Messages are already printed by subprocess_wrap
        pass
    elif msg["type"] == "session_end":
        # Save session
        session_data = msg["data"]
        path = session_mgr.save_session(session_data)
        # Index in database
        db.add_session(session_data)
        typer.echo(f"\n✅ Session saved: {path}")


@app.command()
def init():
    """Initialize the knowledge base."""
    typer.echo("Initializing Self-AI-Knowledge...")

    # Create directories
    for path_key in ["sessions_dir", "knowledge_dir", "skills_dir"]:
        path = Path(config.data_paths[path_key])
        path.mkdir(parents=True, exist_ok=True)
        typer.echo(f"  📁 {path}")

    # Initialize database
    db_path = Path(config.data_paths["db_path"])
    db_path.parent.mkdir(parents=True, exist_ok=True)
    db = Database(config.data_paths["db_path"])
    typer.echo(f"  🗄️  Database: {db_path}")

    typer.echo("\n✅ Initialization complete!")
    typer.echo("Edit config.toml to customize settings.")


@app.command()
def run(
    agent: str = typer.Argument(..., help="Agent to run (claude, gemini, codex)"),
    project: Optional[str] = typer.Option(None, "-p", "--project", help="Project name"),
    profile: Optional[str] = typer.Option(None, "--profile", help="Agent profile"),
    tag: list[str] = typer.Option([], "-t", "--tag", help="Tags for the session"),
):
    """Run an agent CLI with recording."""
    command = config.get_agent_command(agent, profile)
    
    typer.echo(f"🚀 Starting {agent} session...")
    typer.echo(f"   Command: {command}")
    typer.echo("   (Press Ctrl+C to stop recording)")
    typer.echo("")

    wrapper = SubprocessWrapper(_on_message)
    
    try:
        session_data = wrapper.run(
            command=command,
            agent=agent,
            project=project,
            tags=tag,
        )
    except KeyboardInterrupt:
        typer.echo("\n⚠️  Session interrupted")


@app.command()
def sessions(
    limit: int = typer.Option(20, "-l", "--limit"),
    model: Optional[str] = typer.Option(None, "-m", "--model", help="Filter by model"),
):
    """List recent sessions."""
    typer.echo(f"📜 Recent sessions (limit: {limit})")
    typer.echo("-" * 60)

    sessions = session_mgr.list_sessions(limit=limit, model_source=model)
    for s in sessions:
        date = s["created_at"][:16].replace("T", " ")
        tags = f" [{', '.join(s['tags'])}]" if s['tags'] else ""
        typer.e(f"{date} | {s['model_source']:8} | {s['session_id']}")
        if s.get("project"):
            typer.e(f" (@{s['project']})")
        typer.e(f"{tags}\n")


@app.command()
def session(
    session_id: str = typer.Argument(..., help="Session ID"),
):
    """Show session details."""
    session_data = session_mgr.load_session(session_id)
    if not session_data:
        typer.echo(f"❌ Session not found: {session_id}")
        raise typer.Exit(1)

    typer.echo(f"Session: {session_id}")
    typer.echo(f"Model: {session_data['model_source']}")
    typer.echo(f"Date: {session_data['created_at']}")
    if session_data.get("project"):
        typer.echo(f"Project: {session_data['project']}")
    typer.echo(f"Messages: {len(session_data.get('messages', []))}")
    
    # Show summary if available
    summaries = session_data.get("summaries", {})
    if summaries.get("short"):
        typer.echo("\n📝 Summary:")
        typer.echo(summaries["short"])


@app.command()
def summarize(
    session_id: str = typer.Argument(..., help="Session ID"),
    skill: Optional[str] = typer.Option(None, "-s", "--skill", help="Skill to use"),
):
    """Summarize a session and extract knowledge candidates."""
    session_data = session_mgr.load_session(session_id)
    if not session_data:
        typer.echo(f"❌ Session not found: {session_id}")
        raise typer.Exit(1)

    typer.echo(f"📊 Summarizing session: {session_id}")
    
    # This would call a skill or LLM to summarize
    # For now, just show the structure
    typer.echo("   (Summarization skill not yet implemented)")
    
    # Save updated session
    session_mgr.save_session(session_data)
    db.add_session(session_data)


@app.command()
def promote(
    session_id: str = typer.Argument(..., help="Session ID"),
    candidate_index: int = typer.Option(0, "-i", "--index", help="Candidate index"),
    category: str = typer.Option(..., "-c", "--category", help="Category (tech_notes, thinking, etc.)"),
):
    """Promote a knowledge candidate to a knowledge item."""
    session_data = session_mgr.load_session(session_id)
    if not session_data:
        typer.echo(f"❌ Session not found: {session_id}")
        raise typer.Exit(1)

    from .models import Category

    try:
        category_enum = Category(category)
    except ValueError:
        typer.echo(f"❌ Invalid category: {category}")
        typer.echo(f"   Valid: {', '.join(c.value for c in Category)}")
        raise typer.Exit(1)

    typer.echo(f"🚀 Promoting candidate {candidate_index} to {category.value}")
    
    # This would extract from session_data["summaries"]["knowledge_candidates"]
    typer.echo("   (Promotion logic not yet implemented)")


@app.command()
def knowledge(
    category: Optional[str] = typer.Option(None, "-c", "--category", help="Filter by category"),
    limit: int = typer.Option(20, "-l", "--limit"),
):
    """List knowledge items."""
    from .models import Category as KCategory

    cat = None
    if category:
        try:
            cat = KCategory(category)
        except ValueError:
            typer.echo(f"❌ Invalid category: {category}")
            raise typer.Exit(1)

    typer.echo(f"📚 Knowledge items (limit: {limit})")
    typer.echo("-" * 60)

    items = knowledge_mgr.list_knowledge_items(category=cat, limit=limit)
    for item in items:
        date = item["date"][:10]
        tags = f" [{', '.join(item['tags'])}]" if item['tags'] else ""
        typer.echo(f"{date} | {item['category']:15} | {item['title'][:40]}{tags}\n")


@app.command()
def search(
    query: str = typer.Argument(..., help="Search query"),
    limit: int = typer.Option(20, "-l", "--limit"),
    category: Optional[str] = typer.Option(None, "-c", "--category", help="Filter by category"),
):
    """Search knowledge base."""
    from .models import Category

    cat = None
    if category:
        try:
            cat = Category(category)
        except ValueError:
            typer.echo(f"❌ Invalid category: {category}")
            raise typer.Exit(1)

    typer.echo(f"🔍 Searching: {query}")
    typer.echo("-" * 60)

    results = db.search(query, limit=limit, category=cat)
    for r in results:
        date = r["date"][:10]
        tags = json.loads(r["tags"] or "[]")
        tag_str = f" [{', '.join(tags)}]" if tags else ""
        typer.echo(f"{date} | {r['category']:15} | {r['title']}{tag_str}\n")


@app.command()
def skills(
    validate: bool = typer.Option(False, "-v", "--validate", help="Validate skills"),
):
    """List or validate skills."""
    skills_list = skill_mgr.list_skills()
    typer.echo(f"🛠️  Skills ({len(skills_list)})")
    typer.echo("-" * 60)

    for s in skills_list:
        cmd = f" ({s['command']})" if s.get("command") else ""
        typer.echo(f"  • {s['skill_id']}: {s['name']}{cmd}")
        typer.echo(f"    {s['description'][:60]}...")
        
        if validate:
            result = skill_mgr.validate_skill(s['skill_id'])
            if not result['valid']:
                typer.echo(f"    ❌ Invalid: {result['errors']}")
            else:
                typer.echo(f"    ✅ Valid")


@app.command()
def web():
    """Start the web interface."""
    typer.echo("🌐 Starting web interface...")
    typer.echo(f"   http://{config.web.get('host', '127.0.0.1')}:{config.web.get('port', 8787)}")
    
    # Import and run FastAPI
    import uvicorn
    from acv_api.app import app as api_app
    
    uvicorn.run(
        api_app,
        host=config.web.get("host", "127.0.0.1"),
        port=config.web.get("port", 8787),
        reload=config.web.get("reload", True),
    )


@app.command()
def stats():
    """Show statistics."""
    stats_data = db.get_stats()
    typer.echo("📊 Statistics")
    typer.echo("-" * 40)
    typer.echo(f"Sessions: {stats_data['sessions']}")
    typer.echo(f"Knowledge items: {stats_data['knowledge_items']}")
    typer.echo("\nBy category:")
    for cat, count in stats_data.get("by_category", {}).items():
        typer.echo(f"  • {cat}: {count}")


def main():
    app()


if __name__ == "__main__":
    main()
