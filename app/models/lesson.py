from datetime import datetime
from sqlalchemy import JSON, TIMESTAMP, BigInteger, Boolean, Column, ForeignKey, Integer,String, Text
from app.db.database import BASE
from sqlalchemy.orm import relationship


class Lesson(BASE):
    __tablename__ = 'lessons'

    id=Column(BigInteger,primary_key=True)
    title=Column(String(255),nullable=False)
    description=Column(Text)
    content_url=Column(Text)
    created_at=Column(TIMESTAMP(timezone=True),default=datetime.utcnow)
    updated_at=Column(TIMESTAMP(timezone=True),default=datetime.utcnow)