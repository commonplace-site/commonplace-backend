from datetime import datetime
from sqlalchemy import JSON, TIMESTAMP, UUID, BigInteger, Boolean, Column, Float, ForeignKey, Integer,String, Text
from app.db.database import BASE
from sqlalchemy.orm import relationship



class AudioFile(BASE):

    __tablename__ = 'audio_files'
    id=Column(BigInteger,primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    user = relationship("User", back_populates="audio_files")
    audio_type=Column(String(50))
    file_url=Column(Text,nullable=False)
    transcription_text=Column(Text)
    topic=Column(String(100))
    question_type=Column(String(50))
    language_level =Column(String(100))
    rubric_score=Column(Float ,nullable=True)
    created_at= Column(TIMESTAMP(timezone=True),default=datetime.utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)




