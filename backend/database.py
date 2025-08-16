import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from typing import Generator
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/brainrot.db")

os.makedirs("data", exist_ok=True)

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class HelpRequestDB(Base):
    __tablename__ = "help_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    context = Column(Text, nullable=False)
    priority = Column(String, default="medium")
    tags = Column(JSON, default=list)
    status = Column(String, default="open")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ResponseDB(Base):
    __tablename__ = "responses"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, index=True, nullable=False)
    responder_id = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    helpful = Column(Boolean, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class DatabaseManager:
    @staticmethod
    def create_tables():
        Base.metadata.create_all(bind=engine)

    @staticmethod
    def get_db() -> Generator[Session, None, None]:
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    @staticmethod
    def seed_demo_data(db: Session):
        demo_requests = [
            HelpRequestDB(
                user_id="alice",
                title="React Hook Help Needed",
                description="Getting infinite re-renders with useEffect",
                context="Working on a dashboard component that fetches user data",
                priority="high",
                tags=["react", "hooks", "debugging"],
                status="open"
            ),
            HelpRequestDB(
                user_id="bob",
                title="SQL Query Optimization",
                description="Query taking 30+ seconds on large dataset",
                context="E-commerce platform with 1M+ products",
                priority="medium",
                tags=["sql", "performance", "database"],
                status="open"
            )
        ]
        
        for req in demo_requests:
            existing = db.query(HelpRequestDB).filter_by(title=req.title).first()
            if not existing:
                db.add(req)
        
        db.commit()