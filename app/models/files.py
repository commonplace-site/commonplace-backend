from sqlalchemy import TIMESTAMP, Column, ForeignKey, String, DateTime, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.database import BASE
import uuid
from datetime import datetime
import sqlalchemy as sa

class File(BASE):
    __tablename__ = "files"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()'), index=True)
    filename = Column(String, nullable=False)
    s3_url = Column(String, nullable=False)
    uploaded_by = Column(String, nullable=False)
    folder = Column(String, nullable=False)
    filetype = Column(String, nullable=False)
    uploaded_at = Column(DateTime, server_default=func.now())
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))  
    user = relationship("User", back_populates="files")
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

