from datetime import datetime
from sqlalchemy import JSON, TIMESTAMP, UUID, BigInteger, Boolean, Column, ForeignKey, Integer,String, Text
from app.db.database import BASE
from sqlalchemy.orm import relationship
import uuid
import sqlalchemy as sa


class ComprehensionLog(BASE):
    __tablename__ = 'comprehension_logs'
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()'))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    user = relationship("User", back_populates="comprehension_logs")
    material = Column(Text)
    comprehension_score = Column(Integer)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
