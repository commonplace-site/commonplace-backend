from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, File, Form, UploadFile
from requests import Session

from app.core.utils import role_required
from app.db.dependencies import get_db
from app.models.LanguageTest import LanguageTestAudio
from app.models.audio_file import AudioFile
from app.schemas.files import FileOut
from app.services.s3 import upload_to_s3

router = APIRouter(tags=["Learning Test"])

# @router.post("/language-test/upload")
# def upload_test_audio_to_s3(
#     section: str = Form(...),
#     user_id: UUID = Form(...),
#     topic: str = Form(...),
#     question_type: str = Form(...),
#     language_level: str = Form(...),
#     rubric_score: float = Form(None),
#     file: UploadFile = File(...),
#     db: Session = Depends(get_db),
# ):
#     file_url = upload_to_s3(file, f"LanguageTest/{section}")

#     entry = LanguageTestAudio(
#         section=section,
#         user_id=user_id,
#         topic=topic,
#         question_type=question_type,
#         language_level=language_level,
#         rubric_score=rubric_score,
#         file_path=file_url,
#     )
#     db.add(entry)
#     db.commit()
#     return entry


@router.post("/language-test/upload")
def upload_test_audio(
    section: str = Form(...),
    user_id: UUID = Form(...),
    topic: str = Form(...),
    question_type: str = Form(...),
    language_level: str = Form(...),
    rubric_score: float = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):

    file_url = upload_to_s3(file, f"LanguageTest/{section}")
    entry = LanguageTestAudio(
        section=section, user_id=user_id, topic=topic, question_type=question_type,
        language_level=language_level, rubric_score=rubric_score, file_path=file_url
    )
    db.add(entry)
    db.commit()
    return entry



@router.get("/filter", response_model=List[FileOut])
def admin_filter_audio(
    audio_type: Optional[str] = None,
    language_level: Optional[str] = None,
    min_score: Optional[float] = None,
    db: Session = Depends(get_db),
    admin_user: dict = Depends(role_required("Admin"))
):
    query = db.query(AudioFile)
    if audio_type:
        query = query.filter(AudioFile.audio_type == audio_type)
    if language_level:
        query = query.filter(AudioFile.language_level == language_level)
    if min_score is not None:
        query = query.filter(AudioFile.rubric_score >= min_score)
    return query.all()
