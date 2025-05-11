import os
import shutil
import uuid
from typing import Optional, List
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Query
from app.core.utils import get_current_user, stt_transcribe
from app.db.database import SessionLocal
from app.models.users import User
from sqlalchemy.orm import Session
from pydantic import BaseModel
import speech_recognition as sr
from pydub import AudioSegment
import tempfile

# Constants
TEMP_AUDIO_DIR = "temp_audio"
SUPPORTED_FORMATS = [".wav", ".mp3", ".ogg", ".flac", ".m4a"]
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

# Create temp directory if it doesn't exist
os.makedirs(TEMP_AUDIO_DIR, exist_ok=True)

class TranscriptionOptions(BaseModel):
    language: Optional[str] = "en-US"
    punctuate: bool = True
    speaker_diarization: bool = False
    word_timestamps: bool = False
    profanity_filter: bool = True

class TranscriptionResponse(BaseModel):
    transcript: str
    language: str
    confidence: float
    duration: float
    word_timestamps: Optional[List[dict]] = None
    speakers: Optional[List[dict]] = None

router = APIRouter(
    # prefix="/auth",
    tags=["stt"]
)

def convert_to_wav(input_path: str) -> str:
    """Convert audio file to WAV format"""
    audio = AudioSegment.from_file(input_path)
    wav_path = f"{TEMP_AUDIO_DIR}/{uuid.uuid4()}.wav"
    audio.export(wav_path, format="wav")
    return wav_path

@router.post("/stt/", response_model=TranscriptionResponse)
async def speech_to_text(
    file: UploadFile = File(...),
    options: TranscriptionOptions = None,
    current_user: User = Depends(get_current_user)
):
    """
    Convert speech to text with advanced options
    """
    if not options:
        options = TranscriptionOptions()

    # Validate file size
    file_size = 0
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File size exceeds maximum limit of 50MB")

    # Validate file format
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in SUPPORTED_FORMATS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format. Supported formats: {', '.join(SUPPORTED_FORMATS)}"
        )

    # Save uploaded file
    temp_file_path = f"{TEMP_AUDIO_DIR}/{uuid.uuid4()}{file_ext}"
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # Convert to WAV if needed
        if file_ext != ".wav":
            wav_path = convert_to_wav(temp_file_path)
            os.remove(temp_file_path)
            temp_file_path = wav_path

        # Perform transcription
        transcript_result = await stt_transcribe(
            temp_file_path,
            language=options.language,
            punctuate=options.punctuate,
            speaker_diarization=options.speaker_diarization,
            word_timestamps=options.word_timestamps,
            profanity_filter=options.profanity_filter
        )

        return TranscriptionResponse(
            transcript=transcript_result["text"],
            language=transcript_result["language"],
            confidence=transcript_result["confidence"],
            duration=transcript_result["duration"],
            word_timestamps=transcript_result.get("word_timestamps"),
            speakers=transcript_result.get("speakers")
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Cleanup
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

@router.post("/stt/batch/")
async def batch_speech_to_text(
    files: List[UploadFile] = File(...),
    options: TranscriptionOptions = None,
    current_user: User = Depends(get_current_user)
):
    """
    Process multiple audio files for transcription
    """
    results = []
    for file in files:
        result = await speech_to_text(file, options, current_user)
        results.append({
            "filename": file.filename,
            "transcription": result
        })
    return {"results": results}

@router.get("/stt/supported-languages/")
async def get_supported_languages():
    """
    Get list of supported languages for transcription
    """
    recognizer = sr.Recognizer()
    return {
        "languages": [
            {"code": "en-US", "name": "English (US)"},
            {"code": "en-GB", "name": "English (UK)"},
            {"code": "es-ES", "name": "Spanish"},
            {"code": "fr-FR", "name": "French"},
            {"code": "de-DE", "name": "German"},
            {"code": "it-IT", "name": "Italian"},
            {"code": "pt-BR", "name": "Portuguese (Brazil)"},
            {"code": "ru-RU", "name": "Russian"},
            {"code": "ja-JP", "name": "Japanese"},
            {"code": "ko-KR", "name": "Korean"},
            {"code": "zh-CN", "name": "Chinese (Simplified)"},
        ]
    }

# @app.post("/save_audio/")
# def save_audio(audio_path: str = Form(...), db: Session = Depends(SessionLocal), current_user: User = Depends(get_current_user)):
#     new_session = SessionModel(user_id=current_user.id)
#     db.add(new_session)
#     db.commit()
#     db.refresh(new_session)

#     audio = AudioFile(session_id=new_session.id, filename=audio_path)
#     db.add(audio)
#     db.commit()
#     return {"msg": "Audio saved successfully"}
 