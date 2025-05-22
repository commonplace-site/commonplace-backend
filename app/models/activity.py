import uuid
from sqlalchemy import Column, String, DateTime, JSON, ForeignKey, Text, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import BASE
from uuid import uuid4
import enum
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from uuid import UUID
from sqlalchemy.dialects.postgresql import UUID

class ActivityType(str, enum.Enum):
    LOGIN = "login"
    LOGOUT = "logout"
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    SEARCH = "search"
    UPLOAD = "upload"
    DOWNLOAD = "download"
    SHARE = "share"
    COMMENT = "comment"
    RATE = "rate"
    SYSTEM = "system"
    ERROR = "error"

class ActivityCategory(str, enum.Enum):
    AUTHENTICATION = "authentication"
    MEMORY = "memory"
    FILE = "file"
    USER = "user"
    SYSTEM = "system"
    AUDIT = "audit"

class Activity(BASE):
    __tablename__ = "activities"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    business_id = Column(String(36), ForeignKey("businesses.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(100), nullable=False)  # placeholder for ActivityType
    category = Column(String(100), nullable=False)  # placeholder for ActivityCategory
    action = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    activities_metadata = Column(JSON, default=dict)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="activities")
    business = relationship("Business", back_populates="activities")


class ActivitySchema(BaseModel):
    id: uuid.UUID
    business_id: str
    user_id: str
    type: ActivityType
    category: ActivityCategory
    action: str
    description: Optional[str] = None
    metadata: dict = Field(default_factory=dict)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True 