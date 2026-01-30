from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    from acv_cli.config import get_config
    from acv_cli.db import Database
    config = get_config()
    app.state.db = Database(config.data_paths["db_path"])
    yield
    # Shutdown

app = FastAPI(
    title="Self-AI-Knowledge API",
    description="Multi-model AI knowledge base API",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
from .routers import sessions, knowledge, skills, search

app.include_router(sessions.router, prefix="/api/sessions")
app.include_router(knowledge.router, prefix="/api/knowledge")
app.include_router(skills.router, prefix="/api/skills")
app.include_router(search.router, prefix="/api/search")

@app.get("/")
async def root():
    return {"message": "Self-AI-Knowledge API", "version": "0.1.0"}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/stats")
async def stats():
    return app.state.db.get_stats()
