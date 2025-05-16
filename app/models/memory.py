import uuid
from sqlalchemy import Column, Float, String, DateTime, JSON, Integer, ForeignKey, Text, Boolean, Enum, ARRAY
from sqlalchemy.sql import func, expression
from sqlalchemy.orm import relationship, remote
from sqlalchemy.dialects.postgresql import UUID
from app.db.database import BASE
from uuid import uuid4
import enum
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from uuid import UUID as UUIDType
import sqlalchemy as sa

class MemoryType(str, enum.Enum):
    USER_PROFILE = "UserProfile"
    CODEX = "Codex"
    ROOM127 = "Room127"
    SUSPENSE = "Suspense"
    FILE = "File"
    AUDIT_LOG = "AuditLog"
    DEVELOPER_LOG = "DeveloperLog"
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    DOCUMENT = "document"

class Room127Log(BASE):
    __tablename__ = 'room_127_logs'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    context = Column(String(50), nullable=False)
    feedback = Column(JSON, nullable=True)
    meta_data = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="room127_logs")
    # We don't add a relationship to UserProfile here since there's no direct foreign key

class ModuleState(BASE):
    __tablename__ = 'module_states'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    module_id = Column(String(36), nullable=False)
    state = Column(JSON, nullable=False)
    meta_data = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="module_states")
    # We don't add a relationship to UserProfile here since there's no direct foreign key

class CodexLog(BASE):
    __tablename__ = 'codex_logs'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    context = Column(String(50), nullable=False)
    analysis = Column(JSON, nullable=True)
    meta_data = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="codex_logs")
    # We don't add a relationship to UserProfile here since there's no direct foreign key

class DeveloperLog(BASE):
    __tablename__ = 'developer_logs'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    context = Column(String(50), nullable=False)
    log_level = Column(String(20), nullable=False)  # e.g., INFO, WARNING, ERROR
    meta_data = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="developer_logs")
    # We don't add a relationship to UserProfile here since there's no direct foreign key

class AuditLog(BASE):
    __tablename__ = 'audit_logs'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    action = Column(String(100), nullable=False)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="audit_logs")
    # We don't add a relationship to UserProfile here since there's no direct foreign key

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    TEACHER = "teacher"
    STUDENT = "student"
    DEVELOPER = "developer"
    MODERATOR = "moderator"

# Temporarily commented out Memory model and its relationships

class Memory(BASE):
    __tablename__ = "memories"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    business_id = Column(String(36), ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    type = Column(Enum(MemoryType), nullable=False)
    tags = Column(ARRAY(String), default=list)
    content = Column(Text, nullable=False)
    embedding = Column(ARRAY(Float), nullable=True)
    date = Column(DateTime(timezone=True), default=datetime.utcnow)
    memory_metadata = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="memories")
    business = relationship("Business", back_populates="memories")
    user_profile = relationship(
        "UserProfile", 
        primaryjoin="and_(Memory.user_id == foreign(UserProfile.user_id), "
                   "Memory.business_id == foreign(UserProfile.business_id))",
        back_populates="memories",
        viewonly=True
    )


class Business(BASE):
    __tablename__ = "businesses"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    settings = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    # Temporarily commented out Memory relationship
    # memories = relationship("Memory", back_populates="business")
    # users = relationship("UserProfile", back_populates="business")
    activities = relationship("Activity", back_populates="business")

# Temporarily commented out UserProfile model and its relationships

class UserProfile(BASE):
    __tablename__ = "user_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    business_id = Column(String(36), ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.STUDENT)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    preferences = Column(JSON, default=dict)
    meta_data = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    last_active = Column(DateTime(timezone=True), default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Relationships
    user = relationship("User", back_populates="profile", uselist=False)
    business = relationship("Business", back_populates="users")
    memories = relationship(
        "Memory", 
        primaryjoin="and_(UserProfile.user_id == foreign(Memory.user_id), "
                    "UserProfile.business_id == foreign(Memory.business_id))",
        back_populates="user_profile",
        viewonly=True
    )
    room127_logs = relationship(
        "Room127Log", 
        primaryjoin="UserProfile.user_id == Room127Log.user_id",
        viewonly=True
    )
    module_states = relationship(
        "ModuleState", 
        primaryjoin="UserProfile.user_id == ModuleState.user_id",
        viewonly=True
    )
    codex_logs = relationship(
        "CodexLog", 
        primaryjoin="UserProfile.user_id == CodexLog.user_id",
        viewonly=True
    )
    developer_logs = relationship(
        "DeveloperLog", 
        primaryjoin="UserProfile.user_id == DeveloperLog.user_id",
        viewonly=True
    )
    audit_logs = relationship(
        "AuditLog", 
        primaryjoin="UserProfile.user_id == AuditLog.user_id",
        viewonly=True
    )


class MemorySchema(BaseModel):
    id: UUIDType = Field(default_factory=uuid4)
    business_id: str
    user_id: str
    type: MemoryType
    tags: List[str]
    content: str
    embedding: Optional[List[float]] = None
    date: datetime
    metadata: dict = Field(default_factory=dict)

    class Config:
        from_attributes = True

# This duplicate enum seems unnecessary - consider removing
class MemoryType(enum.Enum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"