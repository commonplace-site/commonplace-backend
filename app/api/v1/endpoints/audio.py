from typing import List, Optional, Any, Dict
from uuid import UUID
from fastapi import APIRouter, File, Form, Depends, Response, UploadFile, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session
import yaml
from app import models
from app.core.storage import save_audio_file
from app.core.utils import role_required, get_current_user, speech_to_text, text_to_speech
from app.db.dependencies import get_db
from app.models import memory
from app.models.audio_file import AudioFile
from app.schemas.files import FileOut
from app.schemas.licens import LicenseCreate
from app.services.s3 import upload_to_s3
# from app.services.whisper_parse import parse_audio_with_whisper
import tempfile
import os
from datetime import datetime
from sentence_transformers import SentenceTransformer


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



# @router.post("/audio/parse-p3")
# def parse_audio_and_tag(file: UploadFile = File(...)):
#     # S3 bucket name where the audio file will be uploaded
#     bucket_name = "your-s3-bucket-name"

#     # Parse audio and get transcript, tags, and S3 file URL
#     transcript, tags, file_url = parse_audio_with_whisper(file, bucket_name)

#     # Return the result
#     return {
#         "transcript": transcript,
#         "tags": tags,
#         "file_url": file_url  # Returning the S3 URL for the uploaded audio
#     }

@router.post("/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
    language: str = "zh-CN",
    db: Session = Depends(get_db),
    current_user: dict = Depends(role_required("Student"))
):
    """Transcribe audio file to text"""
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_file.flush()
        
        try:
            # Transcribe audio
            text = speech_to_text(temp_file.name, language)
            
            # Upload original audio to S3
            file_url = upload_to_s3(file, "AudioSubmissions")
            
            # Save to database
            audio_file = AudioFile(
                user_id=current_user["id"],
                file_url=file_url,
                audio_type="submission"
            )
            db.add(audio_file)
            db.commit()
            
            return {
                "text": text,
                "file_url": file_url
            }
        finally:
            os.unlink(temp_file.name)

@router.post("/synthesize")
async def synthesize_speech(
    text: str,
    language: str = "zh-CN",
    current_user: dict = Depends(role_required("Student"))
):
    """Convert text to speech"""
    try:
        audio_data = await text_to_speech(text, language)
        return {
            "audio_data": audio_data,
            "format": "mp3"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def store_memory(self, memory_id: str, memory_type: ChatbotMemoryType, content: str):
    embedding = await self.vector_store.generate_embedding(memory.content)
    await self.vector_store.store_memory(
        memory_id=memory_id,
        memory_type=memory.type,
        content=memory.content,
        embedding=embedding,
        metadata={
            "user_id": str(current_user.id),
            "business_id": memory.business_id,
            "conversation_id": memory.conversation_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

async def search_similar_memories(
    self,
    query: str,
    memory_type: Optional[ChatbotMemoryType] = None,
    filter_conditions: Optional[Dict[str, Any]] = None,
    limit: int = 5
) -> List[Dict[str, Any]]:
    results = self.client.search(
        collection_name=collection_name,
        query_vector=query_embedding,
        query_filter=search_filter,
        limit=limit,
        score_threshold=0.7  # Only return results with similarity score > 0.7
    )

async def get_conversation_context(
    self,
    conversation_id: str,
    memory_type: Optional[ChatbotMemoryType] = None,
    limit: int = 10
) -> List[Dict[str, Any]]:

async def get_user_history(
    self,
    user_id: str,
    business_id: str,
    memory_type: Optional[ChatbotMemoryType] = None,
    limit: int = 10
) -> List[Dict[str, Any]]:

self.embedding_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

async def search_user_history(self, user_id: str, business_id: str, ...):
    filter_conditions = {
        "user_id": user_id,
        "business_id": business_id
    }

def _init_collections(self):
    for memory_type in ChatbotMemoryType:
        collection_name = f"chatbot_{memory_type.value}"

async def delete_memory(self, memory_id: str, memory_type: ChatbotMemoryType):
    self.client.delete(
        collection_name=collection_name,
        points_selector=models.PointIdsList(points=[memory_id]),
        wait=True
    )
