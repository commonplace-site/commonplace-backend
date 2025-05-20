from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.ticket_models import Ticket, TicketComment, TicketHistory, TicketStatus
from app.schemas.ticket import TicketCreate, TicketUpdate, TicketCommentCreate, TicketCommentUpdate, TicketFilter
from app.core.security import get_current_user
from app.core.rbac import check_permission
from app.services.email import EmailService
from app.models.users import User
from uuid import uuid4, UUID
from fastapi import HTTPException, status

class TicketService:
    def __init__(self, db: Session):
        self.db = db
        self.email_service = EmailService()

    def create_ticket(self, ticket_data: Dict) -> Ticket:
        """Create a new ticket"""
        ticket = Ticket(
            title=ticket_data["title"],
            description=ticket_data["description"],
            priority=ticket_data["priority"],
            type=ticket_data["type"],
            assignee_id=ticket_data["assignee_id"],
            labels=ticket_data.get("labels", []),
            metadata=ticket_data.get("metadata", {}),
            status="open",
            created_at=datetime.utcnow()
        )
        
        self.db.add(ticket)
        self.db.commit()
        self.db.refresh(ticket)
        return ticket

    def get_ticket(self, ticket_id: UUID) -> Optional[Ticket]:
        """Get ticket by ID"""
        return self.db.query(Ticket).filter(Ticket.id == ticket_id).first()

    def update_ticket(self, ticket_id: UUID, ticket_data: TicketUpdate) -> Optional[Ticket]:
        """Update ticket information"""
        ticket = self.get_ticket(ticket_id)
        if not ticket:
            return None

        for key, value in ticket_data.dict(exclude_unset=True).items():
            setattr(ticket, key, value)

        ticket.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(ticket)
        return ticket

    def delete_ticket(self, ticket_id: UUID) -> bool:
        """Delete a ticket"""
        ticket = self.get_ticket(ticket_id)
        if not ticket:
            return False

        self.db.delete(ticket)
        self.db.commit()
        return True

    def get_user_tickets(self, user_id: UUID, status: Optional[str] = None) -> List[Ticket]:
        """Get all tickets assigned to a user"""
        query = self.db.query(Ticket).filter(Ticket.assignee_id == user_id)
        if status:
            query = query.filter(Ticket.status == status)
        return query.all()

    def get_tickets_by_type(self, ticket_type: str) -> List[Ticket]:
        """Get all tickets of a specific type"""
        return self.db.query(Ticket).filter(Ticket.type == ticket_type).all()

    def get_tickets_by_priority(self, priority: str) -> List[Ticket]:
        """Get all tickets of a specific priority"""
        return self.db.query(Ticket).filter(Ticket.priority == priority).all()

    def assign_ticket(self, ticket_id: UUID, assignee_id: UUID) -> Optional[Ticket]:
        """Assign a ticket to a user"""
        ticket = self.get_ticket(ticket_id)
        if not ticket:
            return None

        ticket.assignee_id = assignee_id
        ticket.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(ticket)
        return ticket

    def update_ticket_status(self, ticket_id: UUID, status: str) -> Optional[Ticket]:
        """Update ticket status"""
        valid_statuses = ["open", "in_progress", "review", "completed", "closed"]
        if status not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            )

        ticket = self.get_ticket(ticket_id)
        if not ticket:
            return None

        ticket.status = status
        ticket.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(ticket)
        return ticket

    def add_ticket_comment(self, ticket_id: UUID, comment: str, user_id: UUID) -> Optional[Ticket]:
        """Add a comment to a ticket"""
        ticket = self.get_ticket(ticket_id)
        if not ticket:
            return None

        if "comments" not in ticket.metadata:
            ticket.metadata["comments"] = []

        ticket.metadata["comments"].append({
            "user_id": str(user_id),
            "comment": comment,
            "timestamp": datetime.utcnow().isoformat()
        })

        ticket.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(ticket)
        return ticket

    def get_tickets_by_labels(self, labels: List[str]) -> List[Ticket]:
        """Get tickets with specific labels"""
        return self.db.query(Ticket).filter(
            Ticket.labels.overlap(labels)
        ).all()

    def get_tickets_by_metadata(self, metadata_key: str, metadata_value: str) -> List[Ticket]:
        """Get tickets with specific metadata"""
        return self.db.query(Ticket).filter(
            Ticket.metadata[metadata_key].astext == metadata_value
        ).all()

    async def _send_assignment_notification(self, ticket: Ticket, assigned_by_id: str) -> None:
        """Send email notification for ticket assignment"""
        assigned_to_user = self.db.query(User).filter(User.id == ticket.assignee_id).first()
        assigned_by_user = self.db.query(User).filter(User.id == assigned_by_id).first()
        
        if assigned_to_user and assigned_to_user.email:
            await self.email_service.send_ticket_assignment_email(
                email_to=assigned_to_user.email,
                ticket_title=ticket.title,
                ticket_description=ticket.description,
                ticket_id=ticket.id,
                assigned_by=assigned_by_user.name if assigned_by_user else "System"
            )

    async def _send_update_notification(self, ticket: Ticket, updated_by_id: str, changes: Dict[str, Any]) -> None:
        """Send email notification for ticket updates"""
        assigned_to_user = self.db.query(User).filter(User.id == ticket.assignee_id).first()
        updated_by_user = self.db.query(User).filter(User.id == updated_by_id).first()
        
        if assigned_to_user and assigned_to_user.email:
            await self.email_service.send_ticket_update_email(
                email_to=assigned_to_user.email,
                ticket_title=ticket.title,
                ticket_id=ticket.id,
                updated_by=updated_by_user.name if updated_by_user else "System",
                changes=changes
            )

    def delete_ticket(self, ticket_id: str, user_id: str) -> bool:
        """Delete a ticket"""
        ticket = self.get_ticket(ticket_id)
        if not ticket:
            return False

        self._create_history(ticket_id, user_id, "delete", {
            "title": ticket.title,
            "status": ticket.status
        })
        
        self.db.delete(ticket)
        self.db.commit()
        return True

    def list_tickets(self, filters: TicketFilter) -> List[Ticket]:
        """List tickets with filters"""
        query = self.db.query(Ticket)

        if filters.status:
            query = query.filter(Ticket.status == filters.status)
        if filters.priority:
            query = query.filter(Ticket.priority == filters.priority)
        if filters.type:
            query = query.filter(Ticket.type == filters.type)
        if filters.assigned_to:
            query = query.filter(Ticket.assignee_id == filters.assigned_to)
        if filters.created_by:
            query = query.filter(Ticket.created_by == filters.created_by)
        if filters.tags:
            query = query.filter(Ticket.labels.overlap(filters.tags))
        if filters.created_after:
            query = query.filter(Ticket.created_at >= filters.created_after)
        if filters.created_before:
            query = query.filter(Ticket.created_at <= filters.created_before)
        if filters.due_before:
            query = query.filter(Ticket.due_date <= filters.due_before)

        return query.order_by(Ticket.created_at.desc()).all()

    def add_comment(self, ticket_id: str, comment_data: TicketCommentCreate, user_id: str) -> Optional[TicketComment]:
        """Add a comment to a ticket"""
        ticket = self.get_ticket(ticket_id)
        if not ticket:
            return None

        comment = TicketComment(
            id=str(uuid4()),
            ticket_id=ticket_id,
            user_id=user_id,
            content=comment_data.content,
            metadata=comment_data.metadata
        )

        self.db.add(comment)
        self._create_history(ticket_id, user_id, "comment", {
            "comment_id": comment.id,
            "content": comment.content
        })
        self.db.commit()
        self.db.refresh(comment)
        return comment

    def update_comment(self, comment_id: str, comment_data: TicketCommentUpdate, user_id: str) -> Optional[TicketComment]:
        """Update a comment"""
        comment = self.db.query(TicketComment).filter(TicketComment.id == comment_id).first()
        if not comment or comment.user_id != user_id:
            return None

        changes = {}
        for field, value in comment_data.dict(exclude_unset=True).items():
            if hasattr(comment, field) and getattr(comment, field) != value:
                changes[field] = {
                    "old": getattr(comment, field),
                    "new": value
                }
                setattr(comment, field, value)

        if changes:
            self._create_history(comment.ticket_id, user_id, "update_comment", changes)
            comment.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(comment)

        return comment

    def delete_comment(self, comment_id: str, user_id: str) -> bool:
        """Delete a comment"""
        comment = self.db.query(TicketComment).filter(TicketComment.id == comment_id).first()
        if not comment or comment.user_id != user_id:
            return False

        self._create_history(comment.ticket_id, user_id, "delete_comment", {
            "comment_id": comment.id,
            "content": comment.content
        })

        self.db.delete(comment)
        self.db.commit()
        return True

    def _create_history(self, ticket_id: str, user_id: str, action: str, changes: Dict[str, Any]) -> None:
        """Create a history entry for a ticket action"""
        history = TicketHistory(
            id=str(uuid4()),
            ticket_id=ticket_id,
            user_id=user_id,
            action=action,
            changes=changes,
            metadata={}
        )
        self.db.add(history)

    async def _send_comment_notification(self, ticket: Ticket, comment: TicketComment, comment_by_id: str) -> None:
        """Send email notification for new comments"""
        assigned_to_user = self.db.query(User).filter(User.id == ticket.assignee_id).first()
        comment_by_user = self.db.query(User).filter(User.id == comment_by_id).first()
        
        if assigned_to_user and assigned_to_user.email:
            await self.email_service.send_ticket_comment_email(
                email_to=assigned_to_user.email,
                ticket_title=ticket.title,
                ticket_id=ticket.id,
                comment_by=comment_by_user.name if comment_by_user else "System",
                comment_content=comment.content
            ) 