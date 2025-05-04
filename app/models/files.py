from sqlalchemy import Column, ForeignKey, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.database import BASE
import uuid
from datetime import datetime

class FileMetadata(BASE):
    __tablename__ = "files"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    filename = Column(String, nullable=False)
    s3_url = Column(String, nullable=False)
    uploaded_by = Column(String, nullable=False)
    folder = Column(String, nullable=False)
    filetype = Column(String, nullable=False)
    uploaded_at = Column(DateTime, default=datetime)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))  
    user = relationship("User", back_populates="files")
