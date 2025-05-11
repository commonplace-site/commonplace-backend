from sqlalchemy import Column, String, DateTime, JSON, Integer, ForeignKey, Text, Boolean, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import BASE
from uuid import uuid4
import enum

class TicketStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    RESOLVED = "resolved"
    CLOSED = "closed"

class TicketPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class TicketType(str, enum.Enum):
    BUG = "bug"
    FEATURE = "feature"
    ENHANCEMENT = "enhancement"
    DOCUMENTATION = "documentation"
    SUPPORT = "support"

class Ticket(BASE):
    __tablename__ = "tickets"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(Enum(TicketStatus), nullable=False, default=TicketStatus.OPEN)
    priority = Column(Enum(TicketPriority), nullable=False, default=TicketPriority.MEDIUM)
    type = Column(Enum(TicketType), nullable=False)
    
    # Foreign keys
    created_by = Column(String(36), ForeignKey("user_profiles.user_id"), nullable=False)
    assigned_to = Column(String(36), ForeignKey("user_profiles.user_id"), nullable=True)
    
    # Additional fields
    tags = Column(JSON, default=list)
    meta_data = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    due_date = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    creator = relationship("UserProfile", foreign_keys=[created_by], backref="created_tickets")
    assignee = relationship("UserProfile", foreign_keys=[assigned_to], backref="assigned_tickets")
    comments = relationship("TicketComment", back_populates="ticket", cascade="all, delete-orphan")
    history = relationship("TicketHistory", back_populates="ticket", cascade="all, delete-orphan")

class TicketComment(BASE):
    __tablename__ = "ticket_comments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    ticket_id = Column(String(36), ForeignKey("tickets.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("user_profiles.user_id"), nullable=False)
    content = Column(Text, nullable=False)
    meta_data = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    ticket = relationship("Ticket", back_populates="comments")
    user = relationship("UserProfile", backref="ticket_comments")

class TicketHistory(BASE):
    __tablename__ = "ticket_history"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    ticket_id = Column(String(36), ForeignKey("tickets.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("user_profiles.user_id"), nullable=False)
    action = Column(String(50), nullable=False)  # e.g., "status_change", "assignment", "comment"
    changes = Column(JSON, nullable=False)  # Store the changes made
    meta_data = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    ticket = relationship("Ticket", back_populates="history")
    user = relationship("UserProfile", backref="ticket_history") 