from fastapi import APIRouter, HTTPException
from typing import Any

router = APIRouter()

@router.get("")
async def list_knowledge(
    category: str | None = None,
    limit: int = 50,
):
    """List knowledge items."""
    from acv_cli.knowledge import KnowledgeManager
    from acv_cli.models import Category
    
    mgr = KnowledgeManager()
    cat = None
    if category:
        try:
            cat = Category(category)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid category: {category}")
    
    return mgr.list_knowledge_items(category=cat, limit=limit)

@router.get("/{item_id}")
async def get_knowledge(item_id: str):
    """Get knowledge item details."""
    from acv_cli.knowledge import KnowledgeManager
    
    mgr = KnowledgeManager()
    item, path = mgr.load_knowledge_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Knowledge item not found")
    
    return {
        "item": item.model_dump(),
        "path": path,
    }

@router.post("")
async def create_knowledge(
    title: str,
    content: str,
    category: str,
    source_sessions: list[str],
    model_sources: list[str],
    tags: list[str] | None = None,
    confidence: str = "medium",
    generated_by_skill: str | None = None,
):
    """Create a new knowledge item."""
    from acv_cli.knowledge import KnowledgeManager
    from acv_cli.models import Category, Confidence
    
    mgr = KnowledgeManager()
    
    try:
        cat = Category(category)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid category: {category}")
    
    try:
        conf = Confidence(confidence)
    except ValueError:
        conf = Confidence.MEDIUM
    
    item, path = mgr.create_knowledge_item(
        title=title,
        content=content,
        category=cat,
        source_sessions=source_sessions,
        model_sources=model_sources,
        tags=tags,
        confidence=conf,
        generated_by_skill=generated_by_skill,
    )
    
    # Update database index
    from acv_cli.config import get_config
    from acv_cli.db import Database
    config = get_config()
    db = Database(config.data_paths["db_path"])
    db.add_knowledge_item(item, path)
    
    return {"item": item.model_dump(), "path": path}
