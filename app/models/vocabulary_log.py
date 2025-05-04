from datetime import datetime
from sqlalchemy import JSON, TIMESTAMP, UUID, BigInteger, Boolean, Column, ForeignKey, Integer,String, Text
from app.db.database import BASE
from sqlalchemy.orm import relationship

class VocabularyLog(BASE):
    __tablename__ = 'vocabulary_logs'

    id = Column(BigInteger, primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    user = relationship("User", back_populates="vocabulary_logs")
    word = Column(String(100), nullable=False)
    meaning = Column(String(255))
    source = Column(String(100))
    added_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)