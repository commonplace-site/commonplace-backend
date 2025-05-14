from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class MCPEntry(BaseModel):
    entry: str
    submitted_by: str
    date: datetime
    tags: List[str]

class MCPContext(BaseModel):
    type: str = "context"
    title: str
    source: str
    generated_at: datetime
    content: List[MCPEntry]
    summary: str

class MCPContextBuilder:
    @staticmethod
    def from_room127(room127_data: Dict[str, Any]) -> MCPContext:
        """Convert Room 127 data to MCP context format"""
        return MCPContext(
            title=f"Recent Room 127 Entries: {room127_data.get('tag', 'All')}",
            source="Commonplace API v1",
            content=[
                MCPEntry(
                    entry=entry["content"],
                    submitted_by=entry["submitted_by"],
                    date=entry["date"],
                    tags=entry["tags"]
                )
                for entry in room127_data.get("entries", [])
            ],
            summary=room127_data.get("summary", ""),
            use="memory_drift_analysis"
        ) 