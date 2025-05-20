from typing import Dict, Any, Optional
from datetime import datetime
from uuid import UUID
from sqlalchemy import Column, String, DateTime, JSON, Text, Enum as SQLEnum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import BASE
from pydantic import BaseModel
import enum
from uuid import uuid4

class ChatbotMemoryType(str, enum.Enum):
    USER_MESSAGE = "user_message"
    ASSISTANT_MESSAGE = "assistant_message"
    SYSTEM_MESSAGE = "system_message"
    CONTEXT = "context"

class ChatbotMemory(BASE):
    __tablename__ = "chatbot_memories"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    business_id = Column(String(36), nullable=False)
    conversation_id = Column(String(36), nullable=False)
    type = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    memory_metadata = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="chatbot_memories")

class ChatbotMemorySchema(BaseModel):
    business_id: str
    user_id: UUID
    conversation_id: str
    type: ChatbotMemoryType
    content: str
    embedding: Optional[list] = None
    memory_metadata: Dict[str, Any] = {}

    class Config:
        orm_mode = True

class ConversationContext(BASE):
    __tablename__ = "conversation_contexts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    business_id = Column(String(36), nullable=False)
    context = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="conversation_contexts")

class ConversationContextSchema(BaseModel):
    conversation_id: str
    user_id: UUID
    business_id: str
    context: Dict[str, Any] = {}

    class Config:
        orm_mode = True 