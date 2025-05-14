from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID

from app.core.rbac import require_permission
from app.db.dependencies import get_db
from app.models.memory import Room127Log
from app.schemas.memory import Room127LogCreate, Room127LogResponse
from app.schemas.mcp import MCPContext, MCPEntry
from app.services.room127 import Room127Service
from app.core.utils import SourceRegistry

router = APIRouter(prefix="/room127", tags=["room127"])

@router.get("/", response_model=MCPContext)
async def get_room127_entries(
    tag: Optional[str] = Query(None, description="Filter by tag"),
    from_date: Optional[datetime] = Query(None, description="Filter from date"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission("room127", "read"))
):
    """
    Get Room 127 entries with optional filtering
    """
    service = Room127Service(db)
    entries = service.get_entries(tag=tag, from_date=from_date)
    return service.to_mcp_format(entries)

@router.post("/logs", response_model=Room127LogResponse)
async def create_room127_log(
    log: Room127LogCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission("room127", "create"))
):
    """
    Create a new Room 127 log entry
    """
    # Track the submission in the source registry
    SourceRegistry.track_submission(
        current_user.get("id"),
        "room127_entry",
        {
            "tag": log.context,
            "user_id": str(log.user_id),
            "timestamp": datetime.utcnow().isoformat()
        }
    )
    
    db_log = Room127Log(**log.dict())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

@router.get("/logs/{user_id}", response_model=List[Room127LogResponse])
async def get_user_room127_logs(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission("room127", "read"))
):
    """
    Get all Room 127 logs for a specific user
    """
    logs = db.query(Room127Log).filter(Room127Log.user_id == str(user_id)).all()
    return logs

@router.get("/mcp", response_model=MCPContext)
async def get_room127_mcp(
    tag: Optional[str] = Query(None, description="Filter by tag"),
    from_date: Optional[datetime] = Query(None, description="Filter from date"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission("room127", "read"))
):
    """
    Get Room 127 entries in MCP format (proxy endpoint)
    """
    service = Room127Service(db)
    entries = service.get_entries(tag=tag, from_date=from_date)
    return service.to_mcp_format(entries) 