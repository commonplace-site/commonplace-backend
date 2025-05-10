from datetime import datetime
from sqlalchemy import JSON, TIMESTAMP, UUID, BigInteger, Boolean, Column, ForeignKey, Integer,String, Text
from app.db.database import BASE
from sqlalchemy.orm import relationship



class RolePlaySession(BASE):
    __tablename__='roleplay_sessions'

    id=Column(BigInteger,primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    user = relationship("User", back_populates="roleplay_sessions")
    scenario=Column(String(255)) 
    avatar_used=Column(String(100))
    recording_url =Column(Text)
    feedback=Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

