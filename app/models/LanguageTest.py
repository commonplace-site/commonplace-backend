from datetime import datetime
from sqlalchemy import TIMESTAMP, Column, Float, Integer, String, text, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.db.database import BASE
from sqlalchemy.orm import relationship

class LanguageTest(BASE):
    __tablename__ = "language_test_audio"
    
    id = Column(Integer, primary_key=True)
    section = Column(String)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    topic = Column(String)
    question_type = Column(String)
    language_level = Column(String)
    rubric_score = Column(Float, nullable=True)
    file_path = Column(String)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
