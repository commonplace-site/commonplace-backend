from sqlalchemy import Column, String, DateTime, JSON, Integer, ForeignKey, Text, Boolean, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import BASE
from uuid import uuid4
import enum

class ModuleState(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"
    DRAFT = "draft"
    REVIEW = "review"

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    TEACHER = "teacher"
    STUDENT = "student"
    DEVELOPER = "developer"
    MODERATOR = "moderator"

class UserProfile(BASE):
    __tablename__ = "user_profiles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String(36), unique=True, nullable=False, index=True)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.STUDENT)
    preferences = Column(JSON, default=dict)
    learning_stats = Column(JSON, default=dict)
    meta_data = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_active = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)

    # Relationships
    module_states = relationship("ModuleState", back_populates="user")
    codex_logs = relationship("CodexLog", back_populates="user")
    room_logs = relationship("Room127Log", back_populates="user")
    dev_logs = relationship("DeveloperLog", back_populates="user")

class ModuleState(BASE):
    __tablename__ = "module_states"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String(36), ForeignKey("user_profiles.user_id"), nullable=False)
    module_id = Column(String(36), nullable=False)
    state = Column(Enum(ModuleState), nullable=False, default=ModuleState.ACTIVE)
    progress = Column(JSON, default=dict)
    meta_data = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_accessed = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("UserProfile", back_populates="module_states")
    audit_logs = relationship("AuditLog", back_populates="module_state")

class CodexLog(BASE):
    __tablename__ = "codex_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String(36), ForeignKey("user_profiles.user_id"), nullable=False)
    content = Column(Text, nullable=False)
    context = Column(String(50), nullable=False)
    analysis = Column(JSON, default=dict)
    meta_data = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("UserProfile", back_populates="codex_logs")

class Room127Log(BASE):
    __tablename__ = "room_127_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String(36), ForeignKey("user_profiles.user_id"), nullable=False)
    content = Column(Text, nullable=False)
    context = Column(String(50), nullable=False)
    feedback = Column(JSON, default=dict)
    meta_data = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("UserProfile", back_populates="room_logs")

class DeveloperLog(BASE):
    __tablename__ = "developer_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String(36), ForeignKey("user_profiles.user_id"), nullable=False)
    action = Column(String(50), nullable=False)
    details = Column(JSON, default=dict)
    meta_data = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("UserProfile", back_populates="dev_logs")

class AuditLog(BASE):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    module_state_id = Column(String(36), ForeignKey("module_states.id"), nullable=False)
    action = Column(String(50), nullable=False)
    actor_id = Column(String(36), nullable=False)
    changes = Column(JSON, default=dict)
    meta_data = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    module_state = relationship("ModuleState", back_populates="audit_logs") 