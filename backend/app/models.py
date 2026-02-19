from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(String, nullable=True)  # para futura multi-tenant

    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)

    source_document = Column(String, nullable=True)  # nombre del PDF usado

    processing_time_ms = Column(Integer, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
