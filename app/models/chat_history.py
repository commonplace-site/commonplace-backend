from sqlalchemy import Column, String, DateTime, JSON, Integer, ForeignKey, Text
from sqlalchemy.sql import func
from app.db.database import BASE
from uuid import uuid4

class ChatHistory(BASE):
    __tablename__ = "chat_history"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String(36), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    context = Column(String(50), nullable=False)  # speak, write, explain, etc.
    model_source = Column(String(50), nullable=False)
    messages = Column(JSON, nullable=False)  # List of message objects
    metadata = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_archived = Column(Integer, default=0)  # 0 = active, 1 = archived
    last_message_at = Column(DateTime(timezone=True), server_default=func.now()) 