from uuid import UUID
from typing import List, Optional
from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException
from sqlalchemy.orm import Session
from app.core.utils import role_required, get_current_user
from app.db.dependencies import get_db
from app.models.users import User, UserConsent
from app.models.learning_module import LearningModule
from app.models.lesson import Lesson
from app.models.audio_file import AudioFile
from app.schemas.learning import ModuleResponse, LessonResponse # type: ignore
from app.schemas.files import FileOut
from app.services.s3 import upload_to_s3

router = APIRouter(
    prefix="/student",
    tags=["Student"]
)

# Profile Management
@router.post("/consent")
async def student_consent(
    user_id: UUID = Form(...),
    consent: bool = Form(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(role_required("Student"))
):
    """Update student consent"""
    existing = db.query(UserConsent).filter(UserConsent.user_id == user_id).first()
    if existing:
        existing.consent_given = consent
    else:
        db.add(UserConsent(user_id=user_id, consent_given=consent))
    db.commit()
    return {"message": f"Consent updated to {consent}"}

# @router.get("/profile", response_model=UserProfile)
# async def get_profile(
#     db: Session = Depends(get_db),
#     current_user: dict = Depends(role_required("Student"))
# ):
#     """Get student profile"""
#     profile = db.query(UserProfile).filter(UserProfile.user_id == current_user["id"]).first()
#     if not profile:
#         raise HTTPException(status_code=404, detail="Profile not found")
#     return profile

# @router.put("/profile")
# async def update_profile(
#     profile_update: dict,
#     db: Session = Depends(get_db),
#     current_user: dict = Depends(role_required("Student"))
# ):
#     """Update student profile"""
#     profile = db.query(UserProfile).filter(UserProfile.user_id == current_user["id"]).first()
#     if not profile:
#         raise HTTPException(status_code=404, detail="Profile not found")
    
#     for key, value in profile_update.items():
#         setattr(profile, key, value)
    
#     db.commit()
#     db.refresh(profile)
#     return {"message": "Profile updated successfully"}

# Learning Content
@router.get("/modules", response_model=List[ModuleResponse])
async def get_modules(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(role_required("Student"))
):
    """Get available learning modules"""
    return db.query(LearningModule).offset(skip).limit(limit).all()

@router.get("/modules/{module_id}", response_model=ModuleResponse)
async def get_module(
    module_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(role_required("Student"))
):
    """Get specific learning module"""
    module = db.query(LearningModule).filter(LearningModule.id == module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    return module

@router.get("/lessons", response_model=List[LessonResponse])
async def get_lessons(
    module_id: Optional[UUID] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(role_required("Student"))
):
    """Get available lessons"""
    query = db.query(Lesson)
    if module_id:
        query = query.filter(Lesson.module_id == module_id)
    return query.offset(skip).limit(limit).all()

@router.get("/lessons/{lesson_id}", response_model=LessonResponse)
async def get_lesson(
    lesson_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(role_required("Student"))
):
    """Get specific lesson"""
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return lesson

# Audio Submissions
@router.post("/submit-audio")
async def submit_audio(
    lesson_id: UUID = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(role_required("Student"))
):
    """Submit audio for a lesson"""
    # Upload to S3
    file_url = upload_to_s3(file, "StudentSubmissions")
    
    # Create audio record
    new_audio = AudioFile(
        user_id=current_user["id"],
        lesson_id=lesson_id,
        audio_type="submission",
        file_url=file_url
    )
    db.add(new_audio)
    db.commit()
    
    return {"message": "Audio submitted successfully"}

@router.get("/my-submissions", response_model=List[FileOut])
async def get_my_submissions(
    db: Session = Depends(get_db),
    current_user: dict = Depends(role_required("Student"))
):
    """Get student's audio submissions"""
    return db.query(AudioFile).filter(
        AudioFile.user_id == current_user["id"],
        AudioFile.audio_type == "submission"
    ).all()

# Progress Tracking
# @router.get("/my-progress")
# async def get_my_progress(
#     db: Session = Depends(get_db),
#     current_user: dict = Depends(role_required("Student"))
# ):
#     """Get student's learning progress"""
#     profile = db.query(UserProfile).filter(UserProfile.user_id == current_user["id"]).first()
#     if not profile:
#         raise HTTPException(status_code=404, detail="Profile not found")
    
#     # Get completed lessons
#     completed_lessons = db.query(Lesson).filter(
#         Lesson.id.in_(profile.completed_lessons)
#     ).all()
    
#     # Get audio submissions
#     audio_submissions = db.query(AudioFile).filter(
#         AudioFile.user_id == current_user["id"]
#     ).all()
    
#     return {
#         "completed_lessons": len(completed_lessons),
#         "total_lessons": db.query(Lesson).count(),
#         "audio_submissions": len(audio_submissions),
#         "average_score": sum(a.rubric_score or 0 for a in audio_submissions) / len(audio_submissions) if audio_submissions else 0
#     }
