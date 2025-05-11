from datetime import datetime
from sqlalchemy import JSON, TIMESTAMP, BigInteger, Boolean, Column, ForeignKey, Integer,String, Text
from app.db.database import BASE
from sqlalchemy.orm import relationship



class LearningModule(BASE):
    __tablename__ = 'learning_modules'

    id= Column(BigInteger,primary_key=True)
    name=Column(String(100),nullable=False)
    status=Column(String(50),default='pending')
    active_user=Column(Integer,default=0)
    last_updated_at =Column(TIMESTAMP(timezone=True))
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
