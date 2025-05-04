from datetime import datetime
from sqlalchemy import UUID, Column, BigInteger, ForeignKey, String, Text, TIMESTAMP
from sqlalchemy.orm import relationship
from app.db.database import BASE

class Profile(BASE):
    __tablename__ = 'profiles'

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    name = Column(String(100))
    avatar_url = Column(Text)
    bio = Column(Text)
    native_language = Column(String(50))
    target_language = Column(String(50))
    
    user = relationship("User", back_populates="profile")
    
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
