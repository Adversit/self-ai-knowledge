from pydantic import BaseModel, Field
from typing import List, Literal, Optional
from datetime import datetime
from enum import Enum

# Enums
class Role(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class Category(str, Enum):
    TRUSTED_SOURCES = "trusted_sources"
    THINKING = "thinking"
    TECH_NOTES = "tech_notes"
    SKILLS_DERIVED = "skills_derived"

class Confidence(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

# Models
class Message(BaseModel):
    role: Role
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)

class KnowledgeCandidate(BaseModel):
    type: Category
    title: str
    content: str
    tags: List[str] = []
    confidence: Confidence = Confidence.MEDIUM

class SessionSummaries(BaseModel):
    short: Optional[str] = None
    detailed: Optional[str] = None
    action_items: List[str] = []
    knowledge_candidates: List[KnowledgeCandidate] = []

class Session(BaseModel):
    session_id: str
    created_at: datetime = Field(default_factory=datetime.now)
    model_source: str  # "claude", "gemini", "codex"
    model_variant: Optional[str] = None  # "claude-code", "gemini-1.5-pro"
    entry_point: Literal["cli", "import"] = "cli"
    project: Optional[str] = None
    tags: List[str] = []
    messages: List[Message] = []
    summaries: SessionSummaries = Field(default_factory=SessionSummaries)

class KnowledgeItem(BaseModel):
    id: str
    title: str
    date: datetime = Field(default_factory=datetime.now)
    category: Category
    tags: List[str] = []
    source_sessions: List[str] = []
    model_sources: List[str] = []
    confidence: Confidence = Confidence.MEDIUM
    generated_by_skill: Optional[str] = None
    summary: Optional[str] = None

class Skill(BaseModel):
    skill_id: str
    name: str
    description: str
    command: Optional[str] = None
    parameters: dict = {}
    created_at: datetime = Field(default_factory=datetime.now)
