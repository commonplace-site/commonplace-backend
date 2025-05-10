from datetime import datetime
from sqlalchemy import JSON, TIMESTAMP, BigInteger, Boolean, Column, ForeignKey, Integer, String, Text
from app.db.database import BASE
from sqlalchemy.orm import relationship
class Role(BASE):
    __tablename__ = 'roles'
    
    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    users = relationship("User", back_populates="role")
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

