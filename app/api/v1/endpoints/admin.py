from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy.orm import Session
from app.core.utils import role_required, get_current_user, verify_token
from app.db.dependencies import get_db
from app.models.audio_file import AudioFile
from app.models.users import User, UserProfile, Role
from app.models.learning_module import LearningModule
from app.models.lesson import Lesson
from app.schemas.files import FileOut
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.schemas.learning import ModuleCreate, ModuleUpdate, LessonCreate, LessonUpdate # type: ignore
from uuid import UUID
from app.services.redis_service import redis_service
from datetime import datetime, timedelta
import logging

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)

logger = logging.getLogger(__name__)

# User Management
@router.get("/users", response_model=List[UserResponse])
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    role: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(role_required("Admin"))
):
    """Get all users with optional role filter"""
    query = db.query(User)
    if role:
        query = query.join(Role).filter(Role.name == role)
    return query.offset(skip).limit(limit).all()

@router.post("/users", response_model=UserResponse)
async def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(role_required("Admin"))
):
    """Create a new user"""
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(role_required("Admin"))
):
    """Update user details"""
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    for key, value in user_update.dict(exclude_unset=True).items():
        setattr(db_user, key, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(role_required("Admin"))
):
    """Delete a user"""
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(db_user)
    db.commit()
    return {"message": "User deleted successfully"}

# Content Management
@router.get("/private-audios", response_model=List[FileOut])
async def get_private_audios(
    db: Session = Depends(get_db),
    current_user: dict = Depends(role_required("Admin"))
):
    """Get all private audio files"""
    return db.query(AudioFile).filter(AudioFile.audio_type == "private").all()

@router.post("/modules", response_model=ModuleCreate)
async def create_module(
    module: ModuleCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(role_required("Admin"))
):
    """Create a new learning module"""
    db_module = LearningModule(**module.dict())
    db.add(db_module)
    db.commit()
    db.refresh(db_module)
    return db_module

@router.put("/modules/{module_id}", response_model=ModuleUpdate)
async def update_module(
    module_id: UUID,
    module_update: ModuleUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(role_required("Admin"))
):
    """Update a learning module"""
    db_module = db.query(LearningModule).filter(LearningModule.id == module_id).first()
    if not db_module:
        raise HTTPException(status_code=404, detail="Module not found")
    
    for key, value in module_update.dict(exclude_unset=True).items():
        setattr(db_module, key, value)
    
    db.commit()
    db.refresh(db_module)
    return db_module

@router.post("/lessons", response_model=LessonCreate)
async def create_lesson(
    lesson: LessonCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(role_required("Admin"))
):
    """Create a new lesson"""
    db_lesson = Lesson(**lesson.dict())
    db.add(db_lesson)
    db.commit()
    db.refresh(db_lesson)
    return db_lesson

@router.put("/lessons/{lesson_id}", response_model=LessonUpdate)
async def update_lesson(
    lesson_id: UUID,
    lesson_update: LessonUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(role_required("Admin"))
):
    """Update a lesson"""
    db_lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not db_lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    for key, value in lesson_update.dict(exclude_unset=True).items():
        setattr(db_lesson, key, value)
    
    db.commit()
    db.refresh(db_lesson)
    return db_lesson

# Analytics and Reports
@router.get("/analytics/users")
async def get_user_analytics(
    db: Session = Depends(get_db),
    current_user: dict = Depends(role_required("Admin"))
):
    """Get user analytics"""
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    teachers = db.query(User).join(Role).filter(Role.name == "Teacher").count()
    students = db.query(User).join(Role).filter(Role.name == "Student").count()
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "teachers": teachers,
        "students": students
    }

@router.get("/analytics/content")
async def get_content_analytics(
    db: Session = Depends(get_db),
    current_user: dict = Depends(role_required("Admin"))
):
    """Get content analytics"""
    total_modules = db.query(LearningModule).count()
    total_lessons = db.query(Lesson).count()
    total_audio_files = db.query(AudioFile).count()
    
    return {
        "total_modules": total_modules,
        "total_lessons": total_lessons,
        "total_audio_files": total_audio_files
    }

@router.get("/admin/logs/codex")
async def get_codex_logs(
    start_date: str = None,
    end_date: str = None,
    limit: int = 100,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """Get Codex logs with optional date filtering"""
    verify_token(authorization)
    
    try:
        # Get logs from Redis
        logs = await redis_service.get_list("codex_logs", start=-limit, end=-1)
        
        # Filter by date if provided
        if start_date or end_date:
            filtered_logs = []
            for log in logs:
                log_date = datetime.fromisoformat(log["timestamp"])
                if start_date and log_date < datetime.fromisoformat(start_date):
                    continue
                if end_date and log_date > datetime.fromisoformat(end_date):
                    continue
                filtered_logs.append(log)
            logs = filtered_logs
            
        return {
            "logs": logs,
            "total": len(logs),
            "start_date": start_date,
            "end_date": end_date
        }
    except Exception as e:
        logger.error(f"Failed to get Codex logs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get Codex logs: {str(e)}")

@router.get("/admin/logs/audit")
async def get_audit_logs(
    action: str = None,
    user_id: str = None,
    start_date: str = None,
    end_date: str = None,
    limit: int = 100,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """Get audit logs with optional filtering"""
    verify_token(authorization)
    
    try:
        # Get logs from Redis
        logs = await redis_service.get_audit_logs(limit=limit)
        
        # Apply filters
        filtered_logs = []
        for log in logs:
            if action and log["action"] != action:
                continue
            if user_id and log["user_id"] != user_id:
                continue
            if start_date and datetime.fromisoformat(log["timestamp"]) < datetime.fromisoformat(start_date):
                continue
            if end_date and datetime.fromisoformat(log["timestamp"]) > datetime.fromisoformat(end_date):
                continue
            filtered_logs.append(log)
            
        return {
            "logs": filtered_logs,
            "total": len(filtered_logs),
            "filters": {
                "action": action,
                "user_id": user_id,
                "start_date": start_date,
                "end_date": end_date
            }
        }
    except Exception as e:
        logger.error(f"Failed to get audit logs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get audit logs: {str(e)}")

@router.get("/admin/logs/contradictions")
async def get_contradiction_logs(
    status: str = None,
    start_date: str = None,
    end_date: str = None,
    limit: int = 100,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """Get contradiction resolution logs"""
    verify_token(authorization)
    
    try:
        # Get logs from Redis
        logs = await redis_service.get_list("contradiction_logs", start=-limit, end=-1)
        
        # Apply filters
        filtered_logs = []
        for log in logs:
            if status and log["status"] != status:
                continue
            if start_date and datetime.fromisoformat(log["timestamp"]) < datetime.fromisoformat(start_date):
                continue
            if end_date and datetime.fromisoformat(log["timestamp"]) > datetime.fromisoformat(end_date):
                continue
            filtered_logs.append(log)
            
        return {
            "logs": filtered_logs,
            "total": len(filtered_logs),
            "filters": {
                "status": status,
                "start_date": start_date,
                "end_date": end_date
            }
        }
    except Exception as e:
        logger.error(f"Failed to get contradiction logs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get contradiction logs: {str(e)}")

@router.get("/admin/dashboard/stats")
async def get_dashboard_stats(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """Get dashboard statistics"""
    verify_token(authorization)
    
    try:
        # Get stats from Redis
        stats = await redis_service.get("dashboard_stats")
        if not stats:
            # Initialize stats if not exists
            stats = {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "average_response_time": 0,
                "active_users": 0,
                "total_contradictions": 0,
                "resolved_contradictions": 0,
                "pending_contradictions": 0,
                "last_updated": datetime.utcnow().isoformat()
            }
            await redis_service.set("dashboard_stats", stats)
            
        return stats
    except Exception as e:
        logger.error(f"Failed to get dashboard stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard stats: {str(e)}")
