from datetime import datetime
from sqlalchemy import JSON, TIMESTAMP, BigInteger, Boolean, Column, ForeignKey, Integer,String, Text
from app.db.database import BASE
from sqlalchemy.orm import relationship


class ComprehensionLog(BASE):
    __tablename__ = 'comprehension_logs'
    id=Column(BigInteger,primary_key=True)
    user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    user = relationship("User", back_populates="comprehension_logs")
    material=Column(Text)
    comprehension_score=Column(Integer)
    created_at=Column(TIMESTAMP(timezone=True),default=datetime.utcnow)