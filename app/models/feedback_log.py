from datetime import datetime
from sqlalchemy import JSON, TIMESTAMP, UUID, BigInteger, Boolean, Column, ForeignKey, Integer,String, Text
from app.db.database import BASE
from sqlalchemy.orm import relationship



class FeedbackLog(BASE):
    __tablename__ = 'feedback_logs'

    id=Column(BigInteger,primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    user = relationship("User", back_populates="feedback_logs")
    source = Column(String(50))
    feedback_text=Column(Text)
    related_module=Column(String(100))
    created_at=Column(TIMESTAMP(timezone=True),default=datetime.utcnow)