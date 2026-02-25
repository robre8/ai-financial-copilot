from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.orm import declarative_base
from pgvector.sqlalchemy import Vector
from datetime import datetime

Base = declarative_base()


class Document(Base):
    """
    Persistent vector store for document embeddings.
    Uses pgvector for similarity search.
    """
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)  # The actual text chunk
    embedding = Column(Vector(384), nullable=False)  # 384-dim for all-MiniLM-L6-v2
    metadata = Column(JSON, nullable=True)  # Source file, page number, etc.
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<Document(id={self.id}, content_preview='{self.content[:50]}...')>"


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(String, nullable=True)  # para futura multi-tenant

    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)

    source_document = Column(String, nullable=True)  # nombre del PDF usado

    processing_time_ms = Column(Integer, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
