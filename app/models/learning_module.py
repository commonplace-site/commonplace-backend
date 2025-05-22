from datetime import datetime
from sqlalchemy import JSON, TIMESTAMP, BigInteger, Boolean, Column, ForeignKey, Integer, String, Text
from app.db.database import BASE
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

class LearningModule(BASE):
    __tablename__ = 'learning_modules'

    id = Column(BigInteger, primary_key=True)
    name = Column(String(100), nullable=False)
    status = Column(String(50), default='pending')
    active_user = Column(Integer, default=0)
    business_id = Column(UUID(as_uuid=True), ForeignKey('businesses.id', ondelete='CASCADE'), nullable=False)
    last_updated_at = Column(TIMESTAMP(timezone=True))
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    business = relationship("Business", back_populates="learning_modules")
    lessons = relationship("Lesson", back_populates="module", cascade="all, delete-orphan")
