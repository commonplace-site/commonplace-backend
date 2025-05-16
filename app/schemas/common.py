from typing import Any, Optional, Dict, List
from pydantic import BaseModel, Field

class ResponseSchema(BaseModel):
    """Standard response schema for all API endpoints"""
    success: bool = Field(..., description="Whether the request was successful")
    data: Optional[Any] = Field(None, description="Response data")
    error: Optional[str] = Field(None, description="Error message if any")
    meta: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {"message": "Operation successful"},
                "error": None,
                "meta": {"timestamp": "2024-03-19T10:00:00Z"}
            }
        } 