from uuid import UUID
from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session
from app.core.utils import role_required
from app.db.dependencies import get_db
from app.models.audio_file import AudioFile
from app.services.s3 import upload_to_s3

router = APIRouter(tags=["Teach Uploads"])

@router.post("/teacher/upload-private")
def upload_private_audio(
    user_id: UUID = Form(...),
    topic: str = Form(...),
    question_type: str = Form(...),
    language_level: str = Form(...),
    rubric_score: float = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin_user: dict = Depends(role_required("Teacher")) 
):
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
    return {"message": "Private audio uploaded"}
