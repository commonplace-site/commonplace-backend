from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from app.db.database import get_db
from app.services.room127 import Room127Service
from app.schemas.mcp import MCPContext, MCPEntry

router = APIRouter(prefix="/mcp", tags=["mcp"])

@router.get("/room127", response_model=MCPContext)
async def get_room127_mcp(
    tag: Optional[str] = Query(None, description="Filter by tag"),
    from_date: Optional[datetime] = Query(None, description="Filter from date"),
    db: Session = Depends(get_db)
):
    """
    Get Room 127 entries in MCP format
    """
    service = Room127Service(db)
    entries = service.get_entries(tag=tag, from_date=from_date)
    
    # Convert entries to MCP format
    mcp_entries = []
    for entry in entries:
        meta_data = entry.meta_data or {}
        mcp_entries.append(
            MCPEntry(
                entry=entry.content,
                submitted_by=meta_data.get("submitted_by", "system"),
                date=entry.created_at,
                tags=meta_data.get("tags", [])
            )
        )
    
    # Create summary
    summary = f"Found {len(mcp_entries)} entries"
    if tag:
        summary += f" with tag '{tag}'"
    
    return MCPContext(
        title=f"Room 127 Entries",
        source="Commonplace API v1",
        generated_at=datetime.utcnow(),
        content=mcp_entries,
        summary=summary
    ) 