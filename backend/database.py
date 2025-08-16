import os
import sqlite3
import sqlite_vec
import json
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, JSON, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sentence_transformers import SentenceTransformer
from datetime import datetime
from typing import Generator, List, Optional, Tuple
from dotenv import load_dotenv
import numpy as np

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/brainrot.db")

os.makedirs("data", exist_ok=True)

# Initialize sqlite-vec extension
def enable_sqlite_vec(dbapi_connection, connection_record):
    dbapi_connection.enable_load_extension(True)
    sqlite_vec.load(dbapi_connection)
    dbapi_connection.enable_load_extension(False)

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

# Enable sqlite-vec for all connections
event.listen(engine, "connect", enable_sqlite_vec)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Initialize embedding model
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

Base = declarative_base()


class ContextDB(Base):
    __tablename__ = "contexts"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True, nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    context_metadata = Column(JSON, nullable=True)
    tags = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def generate_embedding(self) -> np.ndarray:
        """Generate embedding for the content"""
        text_to_embed = f"{self.content} {self.summary or ''}"
        return embedding_model.encode(text_to_embed)


class DatabaseManager:
    @staticmethod
    def create_tables():
        Base.metadata.create_all(bind=engine)
        # Create vector table for embeddings using raw connection
        raw_conn = engine.raw_connection()
        try:
            cursor = raw_conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS context_vectors (
                    id INTEGER PRIMARY KEY,
                    context_id INTEGER NOT NULL,
                    embedding BLOB NOT NULL,
                    FOREIGN KEY (context_id) REFERENCES contexts (id) ON DELETE CASCADE
                )
            """)
            # Create vector index for similarity search
            cursor.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS vec_contexts USING vec0(
                    id INTEGER PRIMARY KEY,
                    embedding FLOAT[384]
                )
            """)
            raw_conn.commit()
        finally:
            raw_conn.close()

    @staticmethod
    def get_db() -> Generator[Session, None, None]:
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    @staticmethod
    def store_embedding(context_id: int, embedding: np.ndarray):
        """Store embedding vector for a context"""
        raw_conn = engine.raw_connection()
        try:
            cursor = raw_conn.cursor()
            # Store in both tables for redundancy and different use cases
            cursor.execute(
                "INSERT OR REPLACE INTO context_vectors (context_id, embedding) VALUES (?, ?)",
                (context_id, embedding.tobytes())
            )
            # Store in vector search table
            embedding_list = embedding.tolist()
            cursor.execute(
                "INSERT OR REPLACE INTO vec_contexts (id, embedding) VALUES (?, ?)",
                (context_id, json.dumps(embedding_list))
            )
            raw_conn.commit()
        finally:
            raw_conn.close()
    
    @staticmethod
    def similarity_search(query_text: str, limit: int = 10, threshold: float = 0.5) -> List[Tuple[int, float]]:
        """Search for similar contexts using vector similarity"""
        query_embedding = embedding_model.encode(query_text)
        
        raw_conn = engine.raw_connection()
        try:
            cursor = raw_conn.cursor()
            # Use sqlite-vec for similarity search
            query_list = query_embedding.tolist()
            cursor.execute("""
                SELECT id, distance
                FROM vec_contexts
                WHERE embedding MATCH ?
                ORDER BY distance
                LIMIT ?
            """, (json.dumps(query_list), limit))
            
            results = cursor.fetchall()
            # sqlite-vec returns distance, convert to similarity score (lower distance = higher similarity)
            # For cosine distance, similarity = 1 - distance, but we need to handle the threshold properly
            return [(row[0], max(0.0, 2.0 - row[1])) for row in results if (2.0 - row[1]) >= threshold]
        finally:
            raw_conn.close()
    
    @staticmethod
    def get_embedding(context_id: int) -> Optional[np.ndarray]:
        """Retrieve stored embedding for a context"""
        raw_conn = engine.raw_connection()
        try:
            cursor = raw_conn.cursor()
            cursor.execute(
                "SELECT embedding FROM context_vectors WHERE context_id = ?",
                (context_id,)
            )
            result = cursor.fetchone()
            
            if result:
                return np.frombuffer(result[0], dtype=np.float32)
            return None
        finally:
            raw_conn.close()