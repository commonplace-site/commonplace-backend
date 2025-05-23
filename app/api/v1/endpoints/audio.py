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
from app.models.chatbot import ChatbotMemoryType
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

class ChatbotMemoryManager:
    def __init__(self):
        self.embedding_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        self.client = None  # Initialize your vector store client here
        self._init_collections()  # Initialize collections on startup

    def _init_collections(self):
        """Initialize vector store collections for each memory type"""
        try:
            for memory_type in ChatbotMemoryType:
                collection_name = f"chatbot_{memory_type.value}"
                
                # Check if collection exists
                collections = self.client.get_collections().collections
                collection_names = [collection.name for collection in collections]
                
                if collection_name not in collection_names:
                    # Create collection with appropriate configuration
                    self.client.create_collection(
                        collection_name=collection_name,
                        vectors_config={
                            "size": 384,  # Size for multilingual-MiniLM-L12-v2
                            "distance": "Cosine"
                        }
                    )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to initialize collections: {str(e)}")

    async def delete_memory(
        self,
        memory_id: str,
        memory_type: ChatbotMemoryType
    ):
        """Delete a specific memory from the vector store"""
        collection_name = f"chatbot_{memory_type.value}"
        
        try:
            self.client.delete(
                collection_name=collection_name,
                points_selector=models.PointIdsList(points=[memory_id]),
                wait=True
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to delete memory: {str(e)}")

    async def get_user_history(
        self,
        user_id: str,
        business_id: str,
        memory_type: Optional[ChatbotMemoryType] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Retrieve user's conversation history"""
        filter_conditions = {
            "user_id": user_id,
            "business_id": business_id
        }
        
        # Determine collection name based on memory type
        collection_name = f"chatbot_{memory_type.value}" if memory_type else "chatbot_all"
        
        try:
            # Use scroll operation to get all matching points
            results = self.client.scroll(
                collection_name=collection_name,
                filter=filter_conditions,
                limit=limit,
                with_payload=True,
                with_vectors=False,
                order_by="timestamp"  # Order by timestamp in metadata
            )
            
            # Format and return results
            return [
                {
                    "memory_id": point.id,
                    "content": point.payload.get("content"),
                    "metadata": point.payload.get("metadata", {}),
                    "timestamp": point.payload.get("metadata", {}).get("timestamp"),
                    "memory_type": point.payload.get("metadata", {}).get("memory_type")
                }
                for point in results[0]  # scroll returns (points, next_page_offset)
            ]
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to retrieve user history: {str(e)}"
            )

# Initialize the memory manager as a singleton
memory_manager = ChatbotMemoryManager()

# Example usage in an endpoint
@router.get("/user/{user_id}/history")
async def get_user_history_endpoint(
    user_id: str,
    business_id: str,
    memory_type: Optional[ChatbotMemoryType] = None,
    limit: int = 10,
    current_user: dict = Depends(role_required("Student"))
):
    """Get user's conversation history"""
    return await memory_manager.get_user_history(
        user_id=user_id,
        business_id=business_id,
        memory_type=memory_type,
        limit=limit
    )
