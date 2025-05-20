from datetime import datetime
from sqlalchemy import JSON, TIMESTAMP, BigInteger, Boolean, Column, ForeignKey, Integer, String, Text
from app.db.database import BASE
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID


class Lesson(BASE):
    __tablename__ = 'lessons'

    id = Column(BigInteger, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    content_url = Column(Text)
    module_id = Column(BigInteger, ForeignKey('learning_modules.id', ondelete='CASCADE'), nullable=False)
    business_id = Column(UUID(as_uuid=True), ForeignKey('businesses.id', ondelete='CASCADE'), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    module = relationship("LearningModule", back_populates="lessons")
    business = relationship("Business", back_populates="lessons")