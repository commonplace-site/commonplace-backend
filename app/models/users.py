from datetime import datetime
from typing import Optional
import uuid
from uuid import UUID as UUIDType
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import JSON, TIMESTAMP, BigInteger, Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from app.db.database import BASE
from app.models.activity import Activity
from app.models.ticket_models import Ticket
from sqlalchemy.orm import relationship
from pydantic import BaseModel
import sqlalchemy as sa


class User(BASE):
    __tablename__ = 'users'

    # id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=sa.text('uuid_generate_v4()'))
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()'))

    first_Name = Column(String(256), nullable=False)
    last_Name = Column(String(256), nullable=True)
    email = Column(String(150), unique=True, nullable=False)
    password = Column(String(256), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    vocabulary_logs = relationship("VocabularyLog", back_populates="user")
    grammar_logs = relationship("GrammarLog", back_populates="user")
    pronunciation_logs = relationship("PronunciationLog", back_populates="user")
    comprehension_logs = relationship("ComprehensionLog", back_populates="user")
    roleplay_sessions = relationship("RolePlaySession", back_populates="user")
    audio_files = relationship("AudioFile", back_populates="user")
    feedback_logs = relationship("FeedbackLog", back_populates="user")
    activities = relationship("Activity", back_populates="user")
    tickets = relationship("Ticket", back_populates="user", foreign_keys="Ticket.user_id")
    created_tickets = relationship("Ticket", back_populates="creator", foreign_keys="Ticket.created_by")
    assigned_tickets = relationship("Ticket", back_populates="assignee", foreign_keys="Ticket.assigned_to")
    ticket_comments = relationship("TicketComment", back_populates="user")
    ticket_history = relationship("TicketHistory", back_populates="user")
    developer_logs = relationship("DeveloperLog", back_populates="user")
    room127_logs = relationship("Room127Log", back_populates="user")
    module_states = relationship("ModuleState", back_populates="user")
    chatbot_memories = relationship("ChatbotMemory", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user")
    conversation_contexts = relationship("ConversationContext", back_populates="user", cascade="all, delete-orphan")
    codex_logs = relationship("CodexLog", back_populates="user", cascade="all, delete-orphan")
    user_roles = relationship("UserRole", back_populates="user")
    files = relationship("File", back_populates="user")
    license_keys = relationship("LicenseKey", back_populates="user")
    businesses = relationship("Business", back_populates="owner")



class UserConsent(BASE):
    __tablename__ = "user_consent"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=sa.text('uuid_generate_v4()'))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    consent_given = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class UserSchema(BaseModel):
    """User schema."""
    id: UUIDType
    email: str
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserProfileSchema(BaseModel):
    """User profile schema."""
    user_id: UUIDType
    business_id: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
