from datetime import datetime
from sqlalchemy import JSON, TIMESTAMP, BigInteger, Boolean, Column, ForeignKey, Integer,String, Text
from app.db.database import BASE
from sqlalchemy.orm import relationship



class RolePlaySession(BASE):
    __tablename__='roleplay_sessions'

    id=Column(BigInteger,primary_key=True)
    user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    user = relationship("User", back_populates="roleplay_sessions")
    scenario=Column(String(255)) 
    avatar_used=Column(String(100))
    recording_url =Column(Text)
    feedback=Column(Text)
    created_at = Column(TIMESTAMP(timezone=True),default=datetime.utcnow)
