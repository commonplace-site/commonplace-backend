from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy import JSON, TIMESTAMP, BigInteger, Boolean, Column, Date, ForeignKey, Integer,String, Text
from app.db.database import BASE
from sqlalchemy.orm import relationship


class LicenseKey(BASE):
    __tablename__ = "licenseKey"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    user = relationship("User", back_populates="license_keys")
    business_name = Column(String)
    established_date = Column(Date)
    renewal_due_date = Column(Date)
    created_at=Column(TIMESTAMP(timezone=True),default=datetime.utcnow)
    updated_at=Column(TIMESTAMP(timezone=True),default=datetime.utcnow)
    