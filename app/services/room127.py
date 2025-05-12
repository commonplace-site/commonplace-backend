from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.memory import Room127Log
from app.schemas.mcp import MCPContext, MCPContextBuilder

class Room127Service:
    def __init__(self, db: Session):
        self.db = db

    def get_entries(
        self,
        tag: Optional[str] = None,
        from_date: Optional[datetime] = None,
        limit: int = 10
    ) -> List[Room127Log]:
        """Get Room 127 entries with filters"""
        query = self.db.query(Room127Log)
        
        if tag:
            query = query.filter(Room127Log.meta_data['tags'].contains([tag]))
        if from_date:
            query = query.filter(Room127Log.created_at >= from_date)
            
        return query.order_by(Room127Log.created_at.desc()).limit(limit).all()

    def to_mcp_format(self, entries: List[Room127Log]) -> MCPContext:
        """Convert Room 127 entries to MCP format"""
        mcp_entries = []
        for entry in entries:
            meta_data = entry.meta_data or {}
            mcp_entries.append({
                "entry": entry.content,
                "submitted_by": meta_data.get("submitted_by", "system"),
                "date": entry.created_at,
                "tags": meta_data.get("tags", [])
            })
            
        return MCPContextBuilder.from_room127({
            "entries": mcp_entries,
            "summary": self._generate_summary(mcp_entries)
        })

    def _generate_summary(self, entries: List[Dict[str, Any]]) -> str:
        """Generate a summary of the entries"""
        if not entries:
            return "No entries found."
            
        user_entries = sum(1 for e in entries if e["submitted_by"] == "user")
        system_entries = len(entries) - user_entries
        
        return (
            f"{len(entries)} entries found. "
            f"{user_entries} user-submitted, {system_entries} system-generated."
        ) 