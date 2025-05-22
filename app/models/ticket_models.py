# from datetime import datetime
# from sqlalchemy import Column, String, DateTime, JSON, Text, ForeignKey, Enum as SQLEnum
# from sqlalchemy.dialects.postgresql import UUID
# from sqlalchemy.sql import func
# from sqlalchemy.orm import relationship
# from app.db.database import BASE
# import enum
# import uuid

# class TicketStatus(str, enum.Enum):
#     OPEN = "open"
#     IN_PROGRESS = "in_progress"
#     REVIEW = "review"
#     RESOLVED = "resolved"
#     CLOSED = "closed"

# class TicketPriority(str, enum.Enum):
#     LOW = "low"
#     MEDIUM = "medium"
#     HIGH = "high"
#     URGENT = "urgent"

# class TicketType(str, enum.Enum):
#     BUG = "bug"
#     FEATURE = "feature"
#     ENHANCEMENT = "enhancement"
#     DOCUMENTATION = "documentation"
#     SUPPORT = "support"

# class Ticket(BASE):
#     __tablename__ = "tickets"

#     id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
#     user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
#     title = Column(String(200), nullable=False)
#     description = Column(Text, nullable=False)
#     status = Column(SQLEnum(TicketStatus), nullable=False, default=TicketStatus.OPEN)
#     priority = Column(SQLEnum(TicketPriority), nullable=False, default=TicketPriority.MEDIUM)
#     type = Column(SQLEnum(TicketType), nullable=False)
#     created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
#     assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
#     tags = Column(JSON, default=list)
#     meta_data = Column(JSON, default=dict)
#     created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
#     updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
#     due_date = Column(DateTime(timezone=True), nullable=True)

#     user = relationship("User", foreign_keys=[user_id], back_populates="tickets")
#     creator = relationship("User", foreign_keys=[created_by], back_populates="created_tickets")
#     assignee = relationship("User", foreign_keys=[assigned_to], back_populates="assigned_tickets")
#     comments = relationship("TicketComment", back_populates="ticket", cascade="all, delete-orphan")
#     history = relationship("TicketHistory", back_populates="ticket", cascade="all, delete-orphan")

# # --- TICKET COMMENT ---
# class TicketComment(BASE):
#     __tablename__ = "ticket_comments"

#     id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
#     ticket_id = Column(String(36), ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False)
#     user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
#     content = Column(Text, nullable=False)
#     meta_data = Column(JSON, default=dict)
#     created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
#     updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

#     ticket = relationship("Ticket", back_populates="comments")
#     user = relationship("User", back_populates="ticket_comments")

# class TicketComment(BASE):
#     __tablename__ = "ticket_comments"
#     __table_args__ = {'extend_existing': True}

#     id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
#     ticket_id = Column(String(36), ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False)
#     user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
#     content = Column(Text, nullable=False)
#     meta_data = Column(JSON, default=dict)
#     created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
#     updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

#     # Relationships
#     ticket = relationship("Ticket", back_populates="comments")
#     user = relationship("User", back_populates="ticket_comments")
    

# class TicketHistory(BASE):
#     __tablename__ = "ticket_history"
#     __table_args__ = {'extend_existing': True}

#     id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
#     ticket_id = Column(String(36), ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False)
#     user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
#     action = Column(String(50), nullable=False)
#     changes = Column(JSON, nullable=False)
#     meta_data = Column(JSON, default=dict)
#     created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

#     ticket = relationship("Ticket", back_populates="history")
#     user = relationship("User", back_populates="ticket_history")







from datetime import datetime
from sqlalchemy import Column, String, DateTime, JSON, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import BASE
import enum
import uuid

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

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(SQLEnum(TicketStatus), nullable=False, default=TicketStatus.OPEN)
    priority = Column(SQLEnum(TicketPriority), nullable=False, default=TicketPriority.MEDIUM)
    type = Column(SQLEnum(TicketType), nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    tags = Column(JSON, default=list)
    meta_data = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    due_date = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", foreign_keys=[user_id], back_populates="tickets")
    creator = relationship("User", foreign_keys=[created_by], back_populates="created_tickets")
    assignee = relationship("User", foreign_keys=[assigned_to], back_populates="assigned_tickets")
    comments = relationship("TicketComment", back_populates="ticket", cascade="all, delete-orphan")
    history = relationship("TicketHistory", back_populates="ticket", cascade="all, delete-orphan")

class TicketComment(BASE):
    __tablename__ = "ticket_comments"
    __table_args__ = {'extend_existing': True}

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ticket_id = Column(String(36), ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    meta_data = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    ticket = relationship("Ticket", back_populates="comments")
    user = relationship("User", back_populates="ticket_comments")

class TicketHistory(BASE):
    __tablename__ = "ticket_history"
    __table_args__ = {'extend_existing': True}

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ticket_id = Column(String(36), ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    action = Column(String(50), nullable=False)
    changes = Column(JSON, nullable=False)
    meta_data = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    ticket = relationship("Ticket", back_populates="history")
    user = relationship("User", back_populates="ticket_history")