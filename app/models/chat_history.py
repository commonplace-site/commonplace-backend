from datetime import datetime
from sqlalchemy import Column, String, DateTime, JSON, Integer, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from app.db.database import BASE
import uuid

class ChatHistory(BASE):
    __tablename__ = "chat_histories"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    context = Column(String(50), nullable=False)  # speak, write, explain, etc.
    model_source = Column(String(50), nullable=False)
    messages = Column(JSON, nullable=False)  # List of message objects
    chat_metadata = Column(JSON)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    is_archived = Column(Integer, default=0)  # 0 = active, 1 = archived
    last_message_at = Column(DateTime(timezone=True), server_default=func.now())
    message = Column(Text, nullable=False) 