from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class HelpRequestCreate(BaseModel):
    user_id: str
    title: str
    description: str
    context: str
    priority: str = "medium"
    tags: List[str] = []


class HelpRequest(BaseModel):
    id: int
    user_id: str
    title: str
    description: str
    context: str
    priority: str
    tags: List[str]
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ResponseCreate(BaseModel):
    request_id: int
    responder_id: str
    content: str


class Response(BaseModel):
    id: int
    request_id: int
    responder_id: str
    content: str
    helpful: Optional[bool] = None
    created_at: datetime

    class Config:
        from_attributes = True