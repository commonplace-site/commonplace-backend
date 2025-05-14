import os
import uuid
from typing import Optional, List
from fastapi import APIRouter, Depends, Form, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field

from app.core.utils import get_current_user
from app.models.users import User
from app.services.tts import tts_generate, VOICES, VOICE_INFO, AUDIO_FORMATS

router = APIRouter(
    # prefix="/user",
    tags=["Text-to-Speech"]
)

# Constants
TEMP_AUDIO_DIR = "temp_audio"
os.makedirs(TEMP_AUDIO_DIR, exist_ok=True)

# In-memory cache for generated audio files
session_cache = {}

# Pydantic models for request/response
class TTSRequest(BaseModel):
    text: str = Field(..., description="Text to convert to speech")
    voice_name: Optional[str] = Field(None, description="Voice to use")
    audio_format: Optional[str] = Field("mp3", description="Output audio format (mp3, wav, ogg)")
    speaking_rate: Optional[float] = Field(1.0, description="Speaking rate (0.5 to 2.0)")
    pitch: Optional[float] = Field(0.0, description="Voice pitch adjustment (-10 to 10)")
    use_ssml: Optional[bool] = Field(False, description="Whether to use SSML for advanced formatting")

class TTSResponse(BaseModel):
    audio_file: str = Field(..., description="Path to the generated audio file")
    voice_name: str = Field(..., description="Voice used for synthesis")
    audio_format: str = Field(..., description="Format of the generated audio")
    duration: Optional[float] = Field(None, description="Duration of the audio in seconds")

@router.post("/tts", response_model=TTSResponse)
async def text_to_speech(
    request: TTSRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Convert text to speech using Azure Text-to-Speech service
    
    Args:
        request: TTS request parameters
        current_user: The authenticated user
    
    Returns:
        TTSResponse: Contains information about the generated audio
    """
    try:
        # Validate audio format
        if request.audio_format not in AUDIO_FORMATS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported audio format. Supported formats: {', '.join(AUDIO_FORMATS.keys())}"
            )
        
        # Validate speaking rate
        if not 0.5 <= request.speaking_rate <= 2.0:
            raise HTTPException(
                status_code=400,
                detail="Speaking rate must be between 0.5 and 2.0"
            )
        
        # Validate pitch
        if not -10 <= request.pitch <= 10:
            raise HTTPException(
                status_code=400,
                detail="Pitch must be between -10 and 10"
            )
        
        # Check cache first
        cache_key = f"tts-{request.text}-{request.voice_name}-{request.audio_format}-{request.speaking_rate}-{request.pitch}"
        if cache_key in session_cache:
            return TTSResponse(
                audio_file=session_cache[cache_key],
                voice_name=request.voice_name or "zh-CN-XiaoxiaoNeural",
                audio_format=request.audio_format
            )
        
        # Generate speech
        audio_data = await tts_generate(
            text=request.text,
            voice_name=request.voice_name,
            audio_format=request.audio_format,
            speaking_rate=request.speaking_rate,
            pitch=request.pitch,
            use_ssml=request.use_ssml
        )
        
        # Save to temporary file
        temp_audio_path = f"{TEMP_AUDIO_DIR}/{uuid.uuid4()}.{request.audio_format}"
        with open(temp_audio_path, "wb") as f:
            f.write(audio_data)
        
        # Cache the result
        session_cache[cache_key] = temp_audio_path
        
        return TTSResponse(
            audio_file=temp_audio_path,
            voice_name=request.voice_name or "zh-CN-XiaoxiaoNeural",
            audio_format=request.audio_format
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tts/voices")
async def get_available_voices(
    language: Optional[str] = Query(None, description="Filter voices by language code (e.g., zh-CN, en-US)")
):
    """
    Get list of available voices for text-to-speech
    
    Args:
        language: Optional language code to filter voices
    
    Returns:
        dict: Available voices grouped by language
    """
    if language:
        if language not in VOICE_INFO:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported language. Supported languages: {', '.join(VOICE_INFO.keys())}"
            )
        return {"voices": {language: VOICE_INFO[language]}}
    return {"voices": VOICE_INFO}

@router.get("/tts/formats")
async def get_supported_formats():
    """
    Get list of supported audio formats
    """
    return {"formats": list(AUDIO_FORMATS.keys())}

@router.get("/tts/audio/{file_id}")
async def get_audio_file(
    file_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get generated audio file
    
    Args:
        file_id: ID of the audio file
        current_user: The authenticated user
    
    Returns:
        FileResponse: The audio file
    """
    file_path = f"{TEMP_AUDIO_DIR}/{file_id}"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    return FileResponse(
        file_path,
        media_type=f"audio/{os.path.splitext(file_path)[1][1:]}"
    )

@router.delete("/tts/cache")
async def clear_cache(
    current_user: User = Depends(get_current_user)
):
    """
    Clear the TTS cache
    
    Args:
        current_user: The authenticated user
    
    Returns:
        dict: Success message
    """
    global session_cache
    session_cache = {}
    return {"message": "Cache cleared successfully"}

# @router.post("/avatar/")
# async def avatar_generate(text: str = Form(...), current_user: User = Depends(get_current_user)):
#     video_url = await generate_avatar_speech(text)
#     return {"video_url": video_url}
