from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.utils import role_required, get_current_user
from app.db.dependencies import get_db
from app.models.audio_file import AudioFile
from app.models.users import User, UserProfile, Role
from app.models.learning_module import LearningModule
from app.models.lesson import Lesson
from app.schemas.files import FileOut
from app.schemas.users import UserCreate, UserUpdate, UserResponse
from app.schemas.learning import ModuleCreate, ModuleUpdate, LessonCreate, LessonUpdate
from uuid import UUID

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)

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
