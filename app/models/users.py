from datetime import datetime
from typing import Optional
import uuid
from uuid import UUID as UUIDType
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import JSON, TIMESTAMP, BigInteger, Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from app.db.database import BASE
from app.models.ticket_models import Ticket
from sqlalchemy.orm import relationship
from pydantic import BaseModel
import sqlalchemy as sa


class User(BASE):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=sa.text('gen_random_uuid()'))
    first_Name = Column(String(256), nullable=False)
    last_Name = Column(String(256), nullable=True)
    email = Column(String(150), unique=True, nullable=False)
    password = Column(String(256), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    # profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    vocabulary_logs = relationship("VocabularyLog", back_populates="user")
    grammar_logs = relationship("GrammarLog", back_populates="user")
    pronunciation_logs = relationship("PronunciationLog", back_populates="user")
    comprehension_logs = relationship("ComprehensionLog", back_populates="user")
    roleplay_sessions = relationship("RolePlaySession", back_populates="user")
    audio_files = relationship("AudioFile", back_populates="user")
    feedback_logs = relationship("FeedbackLog", back_populates="user")
    # memories = relationship("Memory", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user")
    user_roles = relationship("UserRole", back_populates="user")
    files = relationship("File", back_populates="user")
    license_keys = relationship("LicenseKey", back_populates="user")
    
    # Ticket relationships using string references
    tickets = relationship("Ticket", foreign_keys="[Ticket.user_id]", back_populates="user")
    created_tickets = relationship("Ticket", foreign_keys="[Ticket.created_by]", back_populates="creator")
    assigned_tickets = relationship("Ticket", foreign_keys="[Ticket.assigned_to]", back_populates="assignee")
    ticket_comments = relationship("TicketComment", back_populates="user")
    ticket_history = relationship("TicketHistory", back_populates="user")
    
    # Other relationships
    activities = relationship("Activity", back_populates="user")
    chatbot_memories = relationship("ChatbotMemory", back_populates="user")
    conversation_contexts = relationship("ConversationContext", back_populates="user")
    codex_logs = relationship("CodexLog", back_populates="user")
    developer_logs = relationship("DeveloperLog", back_populates="user")
    room127_logs = relationship("Room127Log", back_populates="user")
    module_states = relationship("ModuleState", back_populates="user")


class UserConsent(BASE):
    __tablename__ = "user_consent"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=sa.text('gen_random_uuid()'))
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
