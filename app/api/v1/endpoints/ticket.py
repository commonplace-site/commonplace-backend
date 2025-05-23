from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.rbac import check_permission
from app.core.utils import get_current_user
from app.db.dependencies import get_db
from app.services.ticket import TicketService
from app.schemas.ticket import (
    TicketCreate, TicketUpdate, TicketResponse,
    TicketCommentCreate, TicketCommentUpdate, TicketCommentResponse,
    TicketHistoryResponse, TicketFilter
)

router = APIRouter()

@router.post("", response_model=TicketResponse)
async def create_ticket(
    ticket_data: TicketCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new ticket"""
    check_permission(current_user, "ticket:create")
    ticket_service = TicketService(db)
    ticket = await ticket_service.create_ticket(ticket_data, current_user["id"])
    return ticket

@router.get("/{ticket_id}", response_model=TicketResponse)
async def get_ticket(
    ticket_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get a ticket by ID"""
    check_permission(current_user, "ticket:read")
    ticket_service = TicketService(db)
    ticket = ticket_service.get_ticket(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket

@router.put("/{ticket_id}", response_model=TicketResponse)
async def update_ticket(
    ticket_id: str,
    ticket_data: TicketUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update a ticket"""
    check_permission(current_user, "ticket:update")
    ticket_service = TicketService(db)
    ticket = await ticket_service.update_ticket(ticket_id, ticket_data, current_user["id"])
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket

@router.delete("/{ticket_id}")
async def delete_ticket(
    ticket_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete a ticket"""
    check_permission(current_user, "ticket:delete")
    ticket_service = TicketService(db)
    if not ticket_service.delete_ticket(ticket_id, current_user["id"]):
        raise HTTPException(status_code=404, detail="Ticket not found")
    return {"message": "Ticket deleted successfully"}

@router.get("", response_model=List[TicketResponse])
async def list_tickets(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    type: Optional[str] = None,
    assigned_to: Optional[str] = None,
    created_by: Optional[str] = None,
    tags: Optional[List[str]] = Query(None),
    created_after: Optional[str] = None,
    created_before: Optional[str] = None,
    due_before: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List tickets with filters"""
    check_permission(current_user, "ticket:read")
    filters = TicketFilter(
        status=status,
        priority=priority,
        type=type,
        assigned_to=assigned_to,
        created_by=created_by,
        tags=tags,
        created_after=created_after,
        created_before=created_before,
        due_before=due_before
    )
    ticket_service = TicketService(db)
    return ticket_service.list_tickets(filters)

@router.post("/{ticket_id}/comments", response_model=TicketCommentResponse)
async def add_comment(
    ticket_id: str,
    comment_data: TicketCommentCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Add a comment to a ticket"""
    check_permission(current_user, "ticket:comment")
    ticket_service = TicketService(db)
    comment = await ticket_service.add_comment(ticket_id, comment_data, current_user["id"])
    if not comment:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return comment

@router.put("/comments/{comment_id}", response_model=TicketCommentResponse)
async def update_comment(
    comment_id: str,
    comment_data: TicketCommentUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update a comment"""
    check_permission(current_user, "ticket:comment")
    ticket_service = TicketService(db)
    comment = ticket_service.update_comment(comment_id, comment_data, current_user["id"])
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment

@router.delete("/comments/{comment_id}")
async def delete_comment(
    comment_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete a comment"""
    check_permission(current_user, "ticket:comment")
    ticket_service = TicketService(db)
    if not ticket_service.delete_comment(comment_id, current_user["id"]):
        raise HTTPException(status_code=404, detail="Comment not found")
    return {"message": "Comment deleted successfully"}

@router.get("/{ticket_id}/history", response_model=List[TicketHistoryResponse])
async def get_ticket_history(
    ticket_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get ticket history"""
    check_permission(current_user, "ticket:read")
    ticket_service = TicketService(db)
    ticket = ticket_service.get_ticket(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket.history 