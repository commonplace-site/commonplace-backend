from datetime import datetime
from sqlalchemy import JSON, TIMESTAMP, BigInteger, Boolean, Column, ForeignKey, Integer,String, Text
from app.db.database import BASE
from sqlalchemy.orm import relationship



class Integration(BASE):
    __tablename__ = 'integrations'

    id=Column(BigInteger, primary_key=True)
    name= Column(String(100), nullable=False)
    type = Column(String(50))
    status=Column(Boolean,default=True)
    usage_count= Column(BigInteger, default=0)
    usage_limit = Column(BigInteger)
    base_url=Column(Text)
    api_key=Column(Text)
    config=Column(JSON)    
    last_check_at=Column(TIMESTAMP(timezone=True))
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
