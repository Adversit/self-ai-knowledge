from fastapi import APIRouter

router = APIRouter()

@router.get("")
async def search(
    q: str,
    limit: int = 20,
    category: str | None = None,
):
    """Search knowledge base."""
    from acv_cli.db import Database
    from acv_cli.config import get_config
    from acv_cli.models import Category
    
    config = get_config()
    db = Database(config.data_paths["db_path"])
    
    cat = None
    if category:
        try:
            cat = Category(category)
        except ValueError:
            pass
    
    results = db.search(query=q, limit=limit, category=cat)
    return {"results": results, "count": len(results)}

@router.post("/fts")
async def search_fts(
    q: str,
    limit: int = 20,
):
    """Full-text search."""
    from acv_cli.db import Database
    from acv_cli.config import get_config
    
    config = get_config()
    db = Database(config.data_paths["db_path"])
    
    results = db.search_fts(query=q, limit=limit)
    return {"results": results, "count": len(results)}
