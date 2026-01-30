from fastapi import APIRouter, HTTPException
from typing import Any

router = APIRouter()

@router.get("")
async def list_sessions(limit: int = 50, model: str | None = None):
    """List recent sessions."""
    from acv_cli.sessions import SessionManager
    mgr = SessionManager()
    return mgr.list_sessions(limit=limit, model_source=model)

@router.get("/{session_id}")
async def get_session(session_id: str):
    """Get session details."""
    from acv_cli.sessions import SessionManager
    mgr = SessionManager()
    session = mgr.load_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@router.post("/{session_id}/summarize")
async def summarize_session(session_id: str):
    """Summarize a session."""
    from acv_cli.sessions import SessionManager
    from acv_cli.db import Database
    from acv_cli.config import get_config
    
    config = get_config()
    mgr = SessionManager()
    db = Database(config.data_paths["db_path"])
    
    session = mgr.load_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # TODO: Implement actual summarization with LLM/skill
    return {"message": "Summarization not yet implemented", "session_id": session_id}
