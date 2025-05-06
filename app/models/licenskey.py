from datetime import datetime
from uuid import UUID
from sqlalchemy import JSON, TIMESTAMP, BigInteger, Boolean, Column, Date, ForeignKey, Integer,String, Text
from app.db.database import BASE
from sqlalchemy.orm import relationship


class License(BASE):
    __tablename__ = "licenses"
    id = Column(Integer, primary_key=True, index=True)
    business_name = Column(String)
    established_date = Column(Date)
    renewal_due_date = Column(Date)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    user = relationship("User", back_populates="licenses")
    created_at=Column(TIMESTAMP(timezone=True),default=datetime.utcnow)
    updated_at=Column(TIMESTAMP(timezone=True),default=datetime.utcnow)
    