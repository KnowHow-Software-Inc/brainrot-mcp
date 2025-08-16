import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from dotenv import load_dotenv

from database import DatabaseManager, HelpRequestDB, ResponseDB
from models import HelpRequest, HelpRequestCreate, Response, ResponseCreate

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    DatabaseManager.create_tables()
    db = next(DatabaseManager.get_db())
    DatabaseManager.seed_demo_data(db)
    print("Database initialized with demo data")
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


@app.post("/api/requests", response_model=HelpRequest)
async def create_help_request(
    request: HelpRequestCreate,
    db: Session = Depends(DatabaseManager.get_db)
):
    db_request = HelpRequestDB(
        user_id=request.user_id,
        title=request.title,
        description=request.description,
        context=request.context,
        priority=request.priority,
        tags=request.tags,
        status="open"
    )
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    return db_request


@app.get("/api/requests", response_model=List[HelpRequest])
async def get_all_requests(
    status: str = None,
    user_id: str = None,
    db: Session = Depends(DatabaseManager.get_db)
):
    query = db.query(HelpRequestDB)
    
    if status:
        query = query.filter(HelpRequestDB.status == status)
    if user_id:
        query = query.filter(HelpRequestDB.user_id == user_id)
    
    return query.all()


@app.get("/api/requests/{request_id}", response_model=HelpRequest)
async def get_request(
    request_id: int,
    db: Session = Depends(DatabaseManager.get_db)
):
    request = db.query(HelpRequestDB).filter(HelpRequestDB.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    return request


@app.post("/api/responses", response_model=Response)
async def create_response(
    response: ResponseCreate,
    db: Session = Depends(DatabaseManager.get_db)
):
    request = db.query(HelpRequestDB).filter(HelpRequestDB.id == response.request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    db_response = ResponseDB(
        request_id=response.request_id,
        responder_id=response.responder_id,
        content=response.content
    )
    db.add(db_response)
    
    request.status = "answered"
    
    db.commit()
    db.refresh(db_response)
    return db_response


@app.get("/api/responses/{request_id}", response_model=List[Response])
async def get_responses(
    request_id: int,
    db: Session = Depends(DatabaseManager.get_db)
):
    responses = db.query(ResponseDB).filter(ResponseDB.request_id == request_id).all()
    return responses


@app.put("/api/responses/{response_id}/helpful")
async def mark_response_helpful(
    response_id: int,
    helpful: bool,
    db: Session = Depends(DatabaseManager.get_db)
):
    response = db.query(ResponseDB).filter(ResponseDB.id == response_id).first()
    if not response:
        raise HTTPException(status_code=404, detail="Response not found")
    
    response.helpful = helpful
    db.commit()
    return {"message": "Response marked", "helpful": helpful}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run("server:app", host=host, port=port, reload=True)