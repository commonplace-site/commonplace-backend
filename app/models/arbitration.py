from sqlalchemy import Column, String, DateTime, JSON, Integer, ForeignKey
from sqlalchemy.sql import func
from app.db.database import BASE
from uuid import uuid4

class Arbitration(BASE):
    __tablename__ = "arbitration"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    request_id = Column(String(36), unique=True, index=True)
    content = Column(String, nullable=False)
    context = Column(String, nullable=False)
    model_source = Column(String, nullable=False)
    status = Column(String, nullable=False)
    priority = Column(Integer, default=1)
    review_notes = Column(String)
    arbitration_metadata = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    reviewed_by = Column(String)
    reviewed_at = Column(DateTime(timezone=True)) 