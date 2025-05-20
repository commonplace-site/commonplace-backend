from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Table
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import BASE
from uuid import uuid4
from sqlalchemy.dialects.postgresql import UUID

# Association table for business users
business_users = Table(
    'business_users',
    BASE.metadata,
    Column('business_id', UUID(as_uuid=True), ForeignKey('businesses.id', ondelete='CASCADE')),
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE')),
    Column('role', String(50), nullable=False),  # e.g., "business_admin", "business_teacher", "business_student"
    Column('is_active', Boolean, default=True),
    Column('created_at', DateTime(timezone=True), server_default=func.now()),
    Column('updated_at', DateTime(timezone=True), onupdate=func.now())
)

class Business(BASE):
    __tablename__ = "businesses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(100), nullable=False)
    license_key = Column(String(100), unique=True, nullable=False)
    established_date = Column(DateTime(timezone=True), nullable=False)
    renewal_due_date = Column(DateTime(timezone=True), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
    modules = relationship("Module", back_populates="business")
    owner = relationship("User", back_populates="businesses")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    users = relationship("User", secondary=business_users, back_populates="businesses")
    modules = relationship("LearningModule", back_populates="business")
    lessons = relationship("Lesson", back_populates="business") 