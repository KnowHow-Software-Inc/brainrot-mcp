from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any


class ContextCreate(BaseModel):
    key: str
    content: str
    summary: Optional[str] = None
    context_metadata: Optional[Dict[str, Any]] = None
    tags: List[str] = []


class Context(BaseModel):
    id: int
    key: str
    content: str
    summary: Optional[str] = None
    context_metadata: Optional[Dict[str, Any]] = None
    tags: List[str] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True