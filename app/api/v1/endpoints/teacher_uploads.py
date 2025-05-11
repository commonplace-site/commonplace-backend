from uuid import UUID
from typing import List, Optional
from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException
from sqlalchemy.orm import Session
from app.core.utils import role_required, get_current_user
from app.db.dependencies import get_db
from app.models.audio_file import AudioFile
from app.models.learning_module import LearningModule
from app.models.lesson import Lesson
from app.models.users import User, UserProfile
from app.schemas.files import FileOut
from app.schemas.learning import ModuleCreate, ModuleUpdate, LessonCreate, LessonUpdate
from app.services.s3 import upload_to_s3

router = APIRouter(
    prefix="/teacher",
    tags=["Teacher"]
)

# Audio Management
@router.post("/upload-private")
async def upload_private_audio(
    user_id: UUID = Form(...),
    topic: str = Form(...),
    question_type: str = Form(...),
    language_level: str = Form(...),
    rubric_score: Optional[float] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(role_required("Teacher"))
):
    """Upload a private audio file for a student"""
    file_url = upload_to_s3(file, "PrivateUploads")

    new_audio = AudioFile(
        user_id=user_id,
        audio_type="private",
        file_url=file_url,
        topic=topic,
        question_type=question_type,
        language_level=language_level,
        rubric_score=rubric_score,
    )
    db.add(new_audio)
    db.commit()
    return {"message": "Private audio uploaded successfully"}

@router.get("/private-audios", response_model=List[FileOut])
async def get_private_audios(
    student_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(role_required("Teacher"))
):
    """Get private audio files for students"""
    query = db.query(AudioFile).filter(AudioFile.audio_type == "private")
    if student_id:
        query = query.filter(AudioFile.user_id == student_id)
    return query.all()

# Student Management
@router.get("/students", response_model=List[UserProfile])
async def get_students(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(role_required("Teacher"))
):
    """Get list of students"""
    return db.query(UserProfile).join(User).filter(User.role == "Student").offset(skip).limit(limit).all()

@router.get("/students/{student_id}", response_model=UserProfile)
async def get_student(
    student_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(role_required("Teacher"))
):
    """Get student details"""
    student = db.query(UserProfile).filter(UserProfile.user_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

# Content Management
@router.post("/modules", response_model=ModuleCreate)
async def create_module(
    module: ModuleCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(role_required("Teacher"))
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
    current_user: dict = Depends(role_required("Teacher"))
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
    current_user: dict = Depends(role_required("Teacher"))
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
    current_user: dict = Depends(role_required("Teacher"))
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

# Progress Tracking
@router.get("/student-progress/{student_id}")
async def get_student_progress(
    student_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(role_required("Teacher"))
):
    """Get student's learning progress"""
    student = db.query(UserProfile).filter(UserProfile.user_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Get completed lessons
    completed_lessons = db.query(Lesson).filter(
        Lesson.id.in_(student.completed_lessons)
    ).all()
    
    # Get audio submissions
    audio_submissions = db.query(AudioFile).filter(
        AudioFile.user_id == student_id
    ).all()
    
    return {
        "student": student,
        "completed_lessons": len(completed_lessons),
        "total_lessons": db.query(Lesson).count(),
        "audio_submissions": len(audio_submissions),
        "average_score": sum(a.rubric_score or 0 for a in audio_submissions) / len(audio_submissions) if audio_submissions else 0
    }
