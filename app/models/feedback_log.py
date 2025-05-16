from datetime import datetime
from sqlalchemy import JSON, TIMESTAMP, UUID, BigInteger, Boolean, Column, ForeignKey, Integer,String, Text
from app.db.database import BASE
from sqlalchemy.orm import relationship
import uuid
import sqlalchemy as sa



class FeedbackLog(BASE):
    __tablename__ = 'feedback_logs'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=sa.text('gen_random_uuid()'))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    user = relationship("User", back_populates="feedback_logs")
    source = Column(String(50))
    feedback_text = Column(Text)
    related_module = Column(String(100))
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
