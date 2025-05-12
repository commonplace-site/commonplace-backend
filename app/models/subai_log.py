from sqlalchemy import Column, String, DateTime, JSON, Integer, ForeignKey
from sqlalchemy.sql import func
from app.db.database import BASE
from uuid import uuid4

class SubAILog(BASE):
    __tablename__ = "subai_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String(36), nullable=False, index=True)
    prompt = Column(String, nullable=False)
    model = Column(String(50), nullable=False)
    response = Column(JSON, nullable=False)
    metadata = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now()) 