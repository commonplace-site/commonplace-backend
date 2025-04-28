from datetime import datetime
from sqlalchemy import JSON, TIMESTAMP, BigInteger, Boolean, Column, ForeignKey, Integer,String, Text
from app.db.database import BASE
from sqlalchemy.orm import relationship



class PronunciationLog(BASE):
    __tablename__ ='pronunciation_logs'
    id=Column(BigInteger,primary_key=True)
    user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    original_text=Column(Text)
    audio_file_url=Column(Text)
    ai_feedback=Column(Text)
    created_at=Column(TIMESTAMP(timezone=True),default=datetime.utcnow)