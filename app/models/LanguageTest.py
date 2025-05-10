
from datetime import datetime
from uuid import UUID
from sqlalchemy import  TIMESTAMP, Column, Float,  Integer,String
from app.db.database import BASE
from sqlalchemy.orm import relationship

class LanguageTestAudio(BASE):
    __tablename__ = "language_test_audio"
    id = Column(Integer, primary_key=True)
    section = Column(String)
    user_id = Column(UUID)
    topic = Column(String)
    question_type = Column(String)
    language_level = Column(String)
    rubric_score = Column(Float, nullable=True)
    file_path = Column(String)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
