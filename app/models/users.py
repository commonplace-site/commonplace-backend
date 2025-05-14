from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import JSON, TIMESTAMP, UUID, BigInteger, Boolean, Column, ForeignKey, Integer,String, Text
from app.db.database import BASE
from sqlalchemy.orm import relationship



class User(BASE):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    first_Name=Column(String(256), nullable=False)
    last_Name=Column(String(256), nullable=True)
    email = Column(String(150), unique=True, nullable=False)
    password = Column(String(256), nullable=False)

    profile = relationship("Profile", back_populates='user', uselist=False)
    vocabulary_logs = relationship("VocabularyLog", back_populates="user")
    grammar_logs = relationship("GrammarLog", back_populates="user")
    pronunciation_logs = relationship("PronunciationLog", back_populates="user")
    comprehension_logs = relationship("ComprehensionLog", back_populates="user")
    roleplay_sessions = relationship("RolePlaySession", back_populates="user")
    audio_files = relationship("AudioFile", back_populates="user")
    feedback_logs = relationship("FeedbackLog", back_populates="user")
    user_roles = relationship("UserRole", back_populates="user")
    files = relationship("File", back_populates="user")
    license_keys = relationship("LicenseKey", back_populates="user")
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class UserConsent(BASE):
    __tablename__ = "user_consent"
    id = Column(Integer, primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    consent_given = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
