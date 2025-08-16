import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from dotenv import load_dotenv

from database import DatabaseManager, ContextDB
from models import Context, ContextCreate

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    DatabaseManager.create_tables()
    print("Database initialized")
    yield


app = FastAPI(title="Brainrot API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Brainrot API is running", "version": "1.0.0"}


@app.post("/api/contexts", response_model=Context)
async def push_context(
    context: ContextCreate,
    db: Session = Depends(DatabaseManager.get_db)
):
    """Push (store) a new context or update existing one"""
    # Check if context with this key already exists
    existing = db.query(ContextDB).filter(ContextDB.key == context.key).first()
    
    if existing:
        # Update existing context
        existing.content = context.content
        existing.summary = context.summary
        existing.context_metadata = context.context_metadata
        existing.tags = context.tags
        existing.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing)
        return existing
    else:
        # Create new context
        db_context = ContextDB(
            key=context.key,
            content=context.content,
            summary=context.summary,
            context_metadata=context.context_metadata,
            tags=context.tags
        )
        db.add(db_context)
        db.commit()
        db.refresh(db_context)
        return db_context


@app.get("/api/contexts/{key}", response_model=Context)
async def pop_context(
    key: str,
    db: Session = Depends(DatabaseManager.get_db)
):
    """Pop (retrieve) a context by key"""
    context = db.query(ContextDB).filter(ContextDB.key == key).first()
    if not context:
        raise HTTPException(status_code=404, detail=f"Context with key '{key}' not found")
    return context


@app.get("/api/contexts", response_model=List[Context])
async def list_contexts(
    tag: Optional[str] = None,
    db: Session = Depends(DatabaseManager.get_db)
):
    """List all contexts, optionally filtered by tag"""
    query = db.query(ContextDB)
    
    if tag:
        # Filter by tag (since tags is JSON, we need to check if tag is in the array)
        contexts = []
        all_contexts = query.all()
        for ctx in all_contexts:
            if tag in (ctx.tags or []):
                contexts.append(ctx)
        return contexts
    
    return query.all()


@app.delete("/api/contexts/{key}")
async def delete_context(
    key: str,
    db: Session = Depends(DatabaseManager.get_db)
):
    """Delete a context by key"""
    context = db.query(ContextDB).filter(ContextDB.key == key).first()
    if not context:
        raise HTTPException(status_code=404, detail=f"Context with key '{key}' not found")
    
    db.delete(context)
    db.commit()
    return {"message": f"Context '{key}' deleted successfully"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run("server:app", host=host, port=port, reload=True)