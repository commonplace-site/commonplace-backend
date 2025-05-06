from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, File, Form, Depends, Response, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session
import yaml
from app.core.storage import save_audio_file
from app.core.utils import role_required
from app.db.dependencies import get_db
from app.models.audio_file import AudioFile
from app.schemas.files import FileOut
from app.schemas.licens import LicenseCreate
from app.services.s3 import upload_to_s3
from app.services.whisper_parse import parse_audio_with_whisper


router = APIRouter(tags=['Audio files'])

# @router.post("/audio/upload")
# def upload_audio_file(
#     user_id: UUID = Form(...),
#     audio_type: str = Form(...),
#     topic: str = Form(...),
#     question_type: str = Form(...),
#     language_level: str = Form(...),
#     rubric_score: float = Form(None),
#     file: UploadFile = File(...),
#     db: Session = Depends(get_db),
# ):
#     path = save_audio_file(file, audio_type)

#     new_audio = AudioFile(
#         user_id=user_id,
#         audio_type=audio_type,
#         file_url=path,
#         topic=topic,
#         question_type=question_type,
#         language_level=language_level,
#         rubric_score=rubric_score,
#         # transcription_text=transcription
#     )

#     db.add(new_audio)
#     db.commit()
#     db.refresh(new_audio)

#     return new_audio

from fastapi import APIRouter, UploadFile, File, Form, Depends
from sqlalchemy.orm import Session
from uuid import UUID

router = APIRouter()

@router.post("/audio/upload")
def upload_audio_file(
    user_id: UUID = Form(...),
    audio_type: str = Form(...),
    topic: str = Form(...),
    question_type: str = Form(...),
    language_level: str = Form(...),
    rubric_score: float = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    # Upload to S3 instead of saving locally
    file_url =  upload_to_s3(file, audio_type)

    new_audio = AudioFile(
        user_id=user_id,
        audio_type=audio_type,
        file_url=file_url,  # S3 URL
        topic=topic,
        question_type=question_type,
        language_level=language_level,
        rubric_score=rubric_score,
        # transcription_text=transcription
    )

    db.add(new_audio)
    db.commit()
    db.refresh(new_audio)

    return new_audio

@router.get("/user/{user_id}",response_model=list[FileOut]) 
def get_user_audio_files(user_id:UUID,db:Session=Depends(get_db)):
    return db.query(AudioFile).filter(AudioFile.user_id==user_id).all()


@router.get("/reference",response_model=list[FileOut])
def get_reference_audios(db:Session=Depends(get_db)):
    return db.query(AudioFile).filter(AudioFile.audio_type=="reference").all()

@router.get("/download/{audio_id}")
def download_audio(audio_id:int,db:Session=Depends(get_db)):
    audio=db.query(AudioFile).filter(AudioFile.id==audio_id).first()
    if not audio:
        return {"error":"Audio file not found"}
    return FileResponse(audio.file_url,   filename=audio.file_url.split("/")[-1])


@router.get("/filter", response_model=List[FileOut])
def admin_filter_audio(
    audio_type: Optional[str] = None, 
    language_level: Optional[str] = None,
    min_score: Optional[float] = None,
    db: Session = Depends(get_db),
    admin_user: dict = Depends(role_required("Admin")),
):
    query = db.query(AudioFile)

    if audio_type:
        query = query.filter(AudioFile.audio_type == audio_type)
    if language_level:
        query = query.filter(AudioFile.language_level == language_level)
    if min_score is not None:
        query = query.filter(AudioFile.rubric_score >= min_score)

    return query.all()




@router.get("/audio/{audio_id}/metadata")
def get_audio_metadata(
    audio_id: int,
    format: Optional[str] = "json",  # default is json
    db: Session = Depends(get_db)
):
    audio = db.query(AudioFile).filter(AudioFile.id == audio_id).first()
    if not audio:
        return JSONResponse(content={"error": "Audio not found"}, status_code=404)

    metadata = {
        "filename": audio.file_url.split("/")[-1],
        "speaker": str(audio.user_id),
        "topic": audio.topic,
        "date": str(audio.created_at),
        "language_level": audio.language_level,
        "tags": [audio.question_type],
        "rubric_score": audio.rubric_score,
    }

    # Return YAML only if explicitly requested
    if format == "yaml":
        return Response(content=yaml.dump(metadata), media_type="text/yaml")

    # Otherwise return JSON
    return JSONResponse(content=metadata)



@router.post("/audio/parse-p3")
def parse_audio_and_tag(file: UploadFile = File(...)):
    # S3 bucket name where the audio file will be uploaded
    bucket_name = "your-s3-bucket-name"

    # Parse audio and get transcript, tags, and S3 file URL
    transcript, tags, file_url = parse_audio_with_whisper(file, bucket_name)

    # Return the result
    return {
        "transcript": transcript,
        "tags": tags,
        "file_url": file_url  # Returning the S3 URL for the uploaded audio
    }
