import os
from fastapi import APIRouter, HTTPException, Header, Depends, UploadFile, File, BackgroundTasks
from openai import OpenAI
from dotenv import load_dotenv
import openai
from app.core.utils import verify_token, stt_transcribe
from app.schemas.user import (
    AalamInput, AalamTTSRequest, AalamSTTRequest, AalamResponse,
    TeacherSubmission, ModuleSubmission, ArbitrationRequest, ArbitrationResponse,
    ModelSource, SubmissionStatus, Message, ChatHistoryCreate, ChatHistoryUpdate,
    ChatHistoryResponse, ChatMessageRequest, ChatMessageResponse
)
from app.services.tts import tts_generate, VOICES, VOICE_INFO
from typing import Optional, Dict, Any, List
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from app.db.dependencies import get_db
from app.models.learning_module import LearningModule
from app.models.feedback_log import FeedbackLog
from app.models.comprehension_log import ComprehensionLog
from app.models.integration import Integration
from app.models.arbitration import Arbitration
from app.models.chat_history import ChatHistory
import json
import httpx
from uuid import UUID, uuid4
import tempfile
import uuid
from app.services.avatar import avatar_service

router = APIRouter(tags=["Aalam Integration"])

load_dotenv(dotenv_path=".env")
openai.api_key = os.getenv("OPENAI_API_KEY")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
ROOM_127_ENDPOINT = os.getenv("ROOM_127_ENDPOINT", "https://room127.example.com/log")
CODEX_ENDPOINT = os.getenv("CODEX_ENDPOINT", "https://codex.example.com/analyze")
SUSPENSE_QUEUE_ENDPOINT = os.getenv("SUSPENSE_QUEUE_ENDPOINT", "https://queue.example.com/add")
TEMP_AUDIO_DIR = "temp_audio"
os.makedirs(TEMP_AUDIO_DIR, exist_ok=True)

def generate_system_prompt(text: str, model_source: ModelSource) -> str:
    base_prompt = {
        'speak': 'You are Aalam, a language tutor focused on spoken fluency. Keep responses brief and conversational.',
        'write': 'You are Aalam, helping the user practice structured writing. Offer suggestions, feedback, and alternatives.',
        'explain': 'You are Aalam, guiding the user through new ideas and language discovery. Offer insightful, unexpected responses.',
        'arbitrate': 'You are Aalam, reviewing and validating content from other AI models. Provide detailed feedback and suggestions for improvement.',
        'review': 'You are Aalam, reviewing teacher and module submissions. Ensure content quality and educational value.'
    }.get(text, 'You are Aalam, a helpful language guide.')

    if model_source != ModelSource.AALAM:
        base_prompt += f"\nYou are reviewing content from {model_source.value}. Provide constructive feedback and suggestions for improvement."
    
    return base_prompt

async def log_to_room_127(user_id: UUID, context: str, response: AalamResponse, db: Session):
    """Log interactions to Room 127 for analysis"""
    try:
        # Log to database
        feedback_log = FeedbackLog(
            user_id=user_id,
            source=response.model_source.value,
            feedback_text=response.response,
            related_module=context,
            metadata=response.metadata
        )
        db.add(feedback_log)
        db.commit()

        # Log to external service
        async with httpx.AsyncClient() as client:
            await client.post(
                ROOM_127_ENDPOINT,
                json={
                    "user_id": str(user_id),
                    "context": context,
                    "response": response.response,
                    "source": response.source,
                    "model_source": response.model_source.value,
                    "confidence": response.confidence,
                    "timestamp": response.timestamp.isoformat(),
                    "audio_file": response.audio_file,
                    "transcription": response.transcription,
                    "metadata": response.metadata,
                    "submission_status": response.submission_status.value if response.submission_status else None,
                    "review_notes": response.review_notes
                }
            )
        logger.info(f"Logged to Room 127 - User: {user_id}, Context: {context}, Model: {response.model_source.value}")
    except Exception as e:
        logger.error(f"Failed to log to Room 127: {str(e)}")

async def check_subservient_api(authorization: str, db: Session) -> bool:
    """Check if the request is from a subservient API"""
    try:
        integration = db.query(Integration).filter(
            Integration.type == "subservient",
            Integration.status == True
        ).first()
        
        if integration and integration.api_key == authorization.split(" ")[-1]:
            return True
        return False
    except Exception as e:
        logger.error(f"Failed to check subservient API: {str(e)}")
        return False

async def log_to_codex(content: str, context: str):
    """Log content to Codex for analysis"""
    try:
        async with httpx.AsyncClient() as client:
            await client.post(
                CODEX_ENDPOINT,
                json={
                    "content": content,
                    "context": context,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        logger.info(f"Logged to Codex - Context: {context}")
    except Exception as e:
        logger.error(f"Failed to log to Codex: {str(e)}")

async def add_to_suspense_queue(content: str, priority: int = 1):
    """Add content to suspense queue for processing"""
    try:
        async with httpx.AsyncClient() as client:
            await client.post(
                SUSPENSE_QUEUE_ENDPOINT,
                json={
                    "content": content,
                    "priority": priority,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        logger.info(f"Added to suspense queue - Priority: {priority}")
    except Exception as e:
        logger.error(f"Failed to add to suspense queue: {str(e)}")

async def process_arbitration_request(request: ArbitrationRequest, db: Session) -> ArbitrationResponse:
    """Process an arbitration request"""
    try:
        # Create arbitration record
        arbitration = Arbitration(
            request_id=str(uuid4()),
            content=request.content,
            context=request.context,
            model_source=request.model_source.value,
            status=SubmissionStatus.PENDING.value,
            priority=request.priority,
            metadata=request.metadata
        )
        db.add(arbitration)
        db.commit()

        # Generate system prompt for arbitration
        system_prompt = generate_system_prompt("arbitrate", request.model_source)
        
        # Call OpenAI API for review
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": request.content},
            ]
        )
        
        review_notes = response.choices[0].message.content
        
        # Update arbitration record
        arbitration.status = SubmissionStatus.NEEDS_REVISION.value
        arbitration.review_notes = review_notes
        arbitration.reviewed_at = datetime.utcnow()
        db.commit()

        return ArbitrationResponse(
            request_id=arbitration.request_id,
            content=request.content,
            context=request.context,
            model_source=request.model_source,
            status=SubmissionStatus.NEEDS_REVISION,
            review_notes=review_notes,
            metadata=request.metadata,
            timestamp=datetime.utcnow()
        )

    except Exception as e:
        logger.error(f"Arbitration processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Arbitration processing failed: {str(e)}")

@router.post("/aalam/arbitrate", response_model=ArbitrationResponse)
async def arbitrate_content(
    request: ArbitrationRequest,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """Endpoint for arbitrating content from other AI models"""
    verify_token(authorization)
    return await process_arbitration_request(request, db)

@router.post("/aalam/teacher-submit", response_model=AalamResponse)
async def teacher_submission(
    submission: TeacherSubmission,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """Endpoint for teacher content submissions"""
    verify_token(authorization)
    
    try:
        # Create arbitration request
        arbitration_request = ArbitrationRequest(
            content=submission.content,
            context=submission.context,
            model_source=ModelSource.TEACHER,
            metadata={
                **submission.metadata,
                "teacher_id": submission.teacher_id,
                "module_id": submission.module_id
            }
        )
        
        # Process the submission
        arbitration_response = await process_arbitration_request(arbitration_request, db)
        
        # Create AalamResponse
        return AalamResponse(
            user_id=submission.teacher_id,
            context=submission.context,
            response=arbitration_response.review_notes,
            source="📎 Aalam",
            confidence=1.0,
            timestamp=datetime.utcnow(),
            model_source=ModelSource.TEACHER,
            metadata=submission.metadata,
            submission_status=arbitration_response.status,
            review_notes=arbitration_response.review_notes
        )

    except Exception as e:
        logger.error(f"Teacher submission failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Teacher submission failed: {str(e)}")

@router.post("/aalam/module-submit", response_model=AalamResponse)
async def module_submission(
    submission: ModuleSubmission,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """Endpoint for module content submissions"""
    verify_token(authorization)
    
    try:
        # Create arbitration request
        arbitration_request = ArbitrationRequest(
            content=submission.content,
            context=submission.context,
            model_source=ModelSource.MODULE,
            metadata={
                **submission.metadata,
                "module_id": submission.module_id
            }
        )
        
        # Process the submission
        arbitration_response = await process_arbitration_request(arbitration_request, db)
        
        # Create AalamResponse
        return AalamResponse(
            user_id=submission.module_id,
            context=submission.context,
            response=arbitration_response.review_notes,
            source="📎 Aalam",
            confidence=1.0,
            timestamp=datetime.utcnow(),
            model_source=ModelSource.MODULE,
            metadata=submission.metadata,
            submission_status=arbitration_response.status,
            review_notes=arbitration_response.review_notes
        )

    except Exception as e:
        logger.error(f"Module submission failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Module submission failed: {str(e)}")

@router.get("/aalam/arbitration/{request_id}", response_model=ArbitrationResponse)
async def get_arbitration_status(
    request_id: str,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """Get the status of an arbitration request"""
    verify_token(authorization)
    
    try:
        arbitration = db.query(Arbitration).filter(Arbitration.request_id == request_id).first()
        if not arbitration:
            raise HTTPException(status_code=404, detail="Arbitration request not found")
            
        return ArbitrationResponse(
            request_id=arbitration.request_id,
            content=arbitration.content,
            context=arbitration.context,
            model_source=ModelSource(arbitration.model_source),
            status=SubmissionStatus(arbitration.status),
            review_notes=arbitration.review_notes,
            metadata=arbitration.metadata,
            timestamp=arbitration.created_at,
            reviewed_by=arbitration.reviewed_by,
            reviewed_at=arbitration.reviewed_at
        )
    except Exception as e:
        logger.error(f"Failed to get arbitration status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get arbitration status: {str(e)}")

@router.put("/aalam/arbitration/{request_id}/review", response_model=ArbitrationResponse)
async def review_arbitration(
    request_id: str,
    status: SubmissionStatus,
    review_notes: str,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """Review and update an arbitration request"""
    verify_token(authorization)
    
    try:
        arbitration = db.query(Arbitration).filter(Arbitration.request_id == request_id).first()
        if not arbitration:
            raise HTTPException(status_code=404, detail="Arbitration request not found")
            
        arbitration.status = status.value
        arbitration.review_notes = review_notes
        arbitration.reviewed_by = authorization.split(" ")[-1]  # Use token as reviewer ID
        arbitration.reviewed_at = datetime.utcnow()
        db.commit()
        
        return ArbitrationResponse(
            request_id=arbitration.request_id,
            content=arbitration.content,
            context=arbitration.context,
            model_source=ModelSource(arbitration.model_source),
            status=status,
            review_notes=review_notes,
            metadata=arbitration.metadata,
            timestamp=arbitration.created_at,
            reviewed_by=arbitration.reviewed_by,
            reviewed_at=arbitration.reviewed_at
        )
    except Exception as e:
        logger.error(f"Failed to review arbitration: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to review arbitration: {str(e)}")

@router.post("/aalam/tts", response_model=AalamResponse)
async def aalam_tts_endpoint(
    data: AalamTTSRequest,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """Aalam endpoint with TTS and avatar integration"""
    verify_token(authorization)

    try:
        # Check if request is from subservient API
        is_subservient = await check_subservient_api(authorization, db)
        
        # Generate system prompt based on mode and model source
        system_prompt = generate_system_prompt(data.context, data.model_source)
        
        # Call OpenAI API to generate response
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": data.text},
            ]
        )
        
        message = response.choices[0].message.content
        
        # Generate speech from the response
        audio_data = await tts_generate(
            text=message,
            voice_name=data.voice_name,
            audio_format=data.audio_format,
            speaking_rate=data.speaking_rate,
            pitch=data.pitch
        )
        
        # Generate avatar video
        avatar_result = await avatar_service.generate_avatar(
            text=message,
            voice_id=data.voice_name,  # Use the same voice ID
            style="natural",  # You can make this configurable
            emotion="neutral"  # You can make this configurable
        )
        
        # Save audio to temporary file
        temp_audio_path = f"{TEMP_AUDIO_DIR}/{uuid.uuid4()}.{data.audio_format}"
        with open(temp_audio_path, "wb") as f:
            f.write(audio_data)
        
        # Create AalamResponse object with avatar information
        aalam_response = AalamResponse(
            user_id=data.user_id,
            context=data.context,
            response=message,
            source="📎 Aalam",
            confidence=1.0,
            timestamp=datetime.utcnow(),
            model_source=data.model_source,
            metadata=data.metadata,
            audio_file=temp_audio_path,
            avatar_url=avatar_result["video_url"],  # Add avatar URL
            avatar_metadata=avatar_result["metadata"]  # Add avatar metadata
        )

        # Log interactions
        await log_to_room_127(data.user_id, data.context, aalam_response, db)
        await log_to_codex(message, data.context)
        
        if is_subservient:
            await add_to_suspense_queue(message)

        return aalam_response

    except Exception as e:
        logger.error(f"Aalam TTS failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Aalam TTS failed: {str(e)}")

@router.post("/aalam/stt", response_model=AalamResponse)
async def aalam_stt_endpoint(
    data: AalamSTTRequest,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """Aalam endpoint with STT integration"""
    verify_token(authorization)

    try:
        # Check if request is from subservient API
        is_subservient = await check_subservient_api(authorization, db)
        
        # Transcribe audio
        transcript_result = await stt_transcribe(
            data.audio_file,
            language=data.language,
            punctuate=data.punctuate,
            speaker_diarization=data.speaker_diarization,
            word_timestamps=data.word_timestamps
        )
        
        # Generate system prompt based on mode
        system_prompt = generate_system_prompt(data.context, ModelSource.AALAM)
        
        # Call OpenAI API to generate response
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": transcript_result["text"]},
            ]
        )
        
        message = response.choices[0].message.content
        
        # Create AalamResponse object
        aalam_response = AalamResponse(
            user_id=data.user_id,
            context=data.context,
            response=message,
            source="📎 Aalam",
            confidence=transcript_result["confidence"],
            timestamp=datetime.utcnow(),
            transcription=transcript_result["text"],
            word_timestamps=transcript_result.get("word_timestamps"),
            speakers=transcript_result.get("speakers"),
            model_source=ModelSource.AALAM
        )

        # Log interactions
        await log_to_room_127(data.user_id, data.context, aalam_response, db)
        await log_to_codex(message, data.context)
        
        if is_subservient:
            await add_to_suspense_queue(message)

        return aalam_response

    except Exception as e:
        logger.error(f"Aalam STT failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Aalam STT failed: {str(e)}")

@router.post("/aalam/tts-stt", response_model=AalamResponse)
async def aalam_tts_stt_endpoint(
    data: AalamSTTRequest,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """Aalam endpoint with both TTS and STT integration"""
    verify_token(authorization)

    try:
        # Check if request is from subservient API
        is_subservient = await check_subservient_api(authorization, db)
        
        # First, transcribe the audio
        transcript_result = await stt_transcribe(
            data.audio_file,
            language=data.language,
            punctuate=data.punctuate,
            speaker_diarization=data.speaker_diarization,
            word_timestamps=data.word_timestamps
        )
        
        # Generate system prompt based on mode
        system_prompt = generate_system_prompt(data.context, ModelSource.AALAM)
        
        # Call OpenAI API to generate response
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": transcript_result["text"]},
            ]
        )
        
        message = response.choices[0].message.content
        
        # Generate speech from the response
        audio_data = await tts_generate(
            text=message,
            voice_name="zh-CN-XiaoxiaoNeural",  # Default to Chinese female voice
            audio_format="mp3"
        )
        
        # Save audio to temporary file
        temp_audio_path = f"{TEMP_AUDIO_DIR}/{uuid.uuid4()}.mp3"
        with open(temp_audio_path, "wb") as f:
            f.write(audio_data)
        
        # Create AalamResponse object
        aalam_response = AalamResponse(
            user_id=data.user_id,
            context=data.context,
            response=message,
            source="📎 Aalam",
            confidence=transcript_result["confidence"],
            timestamp=datetime.utcnow(),
            audio_file=temp_audio_path,
            transcription=transcript_result["text"],
            word_timestamps=transcript_result.get("word_timestamps"),
            speakers=transcript_result.get("speakers"),
            model_source=ModelSource.AALAM
        )

        # Log interactions
        await log_to_room_127(data.user_id, data.context, aalam_response, db)
        await log_to_codex(message, data.context)
        
        if is_subservient:
            await add_to_suspense_queue(message)

        return aalam_response

    except Exception as e:
        logger.error(f"Aalam TTS-STT failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Aalam TTS-STT failed: {str(e)}")

@router.post("/aalam")
async def aalam_endpoint(
    data: AalamInput,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    verify_token(authorization)

    try:
        # Check if request is from subservient API
        is_subservient = await check_subservient_api(authorization, db)
        
        # Generate system prompt based on mode
        system_prompt = generate_system_prompt(data.context, ModelSource.AALAM)
        
        # Call OpenAI API to generate response
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": data.text},
            ]
        )
        
        message = response.choices[0].message.content
        
        # Create AalamResponse object with source tracking
        aalam_response = AalamResponse(
            content=message,
            source="📎 Aalam",
            confidence=1.0,
            model_source=ModelSource.AALAM
        )

        # Log to Room 127
        await log_to_room_127(data.user_id, data.context, aalam_response, db)

        # Log to Codex for analysis
        await log_to_codex(message, data.context)

        # Add to suspense queue if needed
        if is_subservient:
            await add_to_suspense_queue(message)

        # Return the response with source information
        return {
            "user_id": data.user_id,
            "context": data.context,
            "response": aalam_response.content,
            "source": aalam_response.source,
            "confidence": aalam_response.confidence,
            "timestamp": aalam_response.timestamp.isoformat(),
            "model_source": aalam_response.model_source.value,
            "metadata": aalam_response.metadata
        }

    except Exception as e:
        logger.error(f"Aalam failed to respond: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Aalam failed to respond: {str(e)}")

@router.post("/aalam/vet")
async def vet_content(
    data: AalamInput,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """Endpoint for teachers/modules to push content for vetting"""
    verify_token(authorization)
    
    try:
        # Create a new learning module entry
        new_module = LearningModule(
            name=f"Vetted Content - {datetime.utcnow().isoformat()}",
            status="pending"
        )
        db.add(new_module)
        db.commit()

        # Log the content for vetting
        await log_to_codex(data.text, "content_vetting")
        await add_to_suspense_queue(data.text, priority=2)

        # Create comprehension log entry
        comprehension_log = ComprehensionLog(
            user_id=data.user_id,
            material=data.text,
            comprehension_score=None  # To be filled after vetting
        )
        db.add(comprehension_log)
        db.commit()
        
        return {
            "status": "pending",
            "message": "Content submitted for vetting",
            "module_id": new_module.id,
            "comprehension_log_id": comprehension_log.id
        }
    except Exception as e:
        logger.error(f"Content vetting failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Content vetting failed: {str(e)}")

@router.get("/aalam/modules")
async def list_modules(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """List all learning modules"""
    verify_token(authorization)
    
    try:
        modules = db.query(LearningModule).all()
        return {
            "modules": [
                {
                    "id": module.id,
                    "name": module.name,
                    "status": module.status,
                    "active_users": module.active_user,
                    "last_updated": module.last_updated_at.isoformat() if module.last_updated_at else None
                }
                for module in modules
            ]
        }
    except Exception as e:
        logger.error(f"Failed to list modules: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list modules: {str(e)}")

@router.post("/aalam/chats", response_model=ChatHistoryResponse)
async def create_chat(
    chat: ChatHistoryCreate,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """Create a new chat conversation"""
    verify_token(authorization)
    
    try:
        # Create new chat history
        new_chat = ChatHistory(
            user_id=chat.user_id,
            title=chat.title,
            context=chat.context,
            model_source=chat.model_source.value,
            messages=[msg.dict() for msg in chat.messages],
            metadata=chat.metadata
        )
        db.add(new_chat)
        db.commit()
        db.refresh(new_chat)
        
        return ChatHistoryResponse(
            id=new_chat.id,
            user_id=new_chat.user_id,
            title=new_chat.title,
            context=new_chat.context,
            model_source=ModelSource(new_chat.model_source),
            messages=[Message(**msg) for msg in new_chat.messages],
            metadata=new_chat.metadata,
            created_at=new_chat.created_at,
            updated_at=new_chat.updated_at,
            is_archived=bool(new_chat.is_archived),
            last_message_at=new_chat.last_message_at
        )
    except Exception as e:
        logger.error(f"Failed to create chat: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create chat: {str(e)}")

@router.get("/aalam/chats/{chat_id}", response_model=ChatHistoryResponse)
async def get_chat(
    chat_id: str,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """Get a specific chat conversation"""
    verify_token(authorization)
    
    try:
        chat = db.query(ChatHistory).filter(ChatHistory.id == chat_id).first()
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")
            
        return ChatHistoryResponse(
            id=chat.id,
            user_id=chat.user_id,
            title=chat.title,
            context=chat.context,
            model_source=ModelSource(chat.model_source),
            messages=[Message(**msg) for msg in chat.messages],
            metadata=chat.metadata,
            created_at=chat.created_at,
            updated_at=chat.updated_at,
            is_archived=bool(chat.is_archived),
            last_message_at=chat.last_message_at
        )
    except Exception as e:
        logger.error(f"Failed to get chat: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get chat: {str(e)}")

@router.get("/aalam/chats", response_model=List[ChatHistoryResponse])
async def list_chats(
    user_id: str,
    is_archived: Optional[bool] = False,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """List all chats for a user"""
    verify_token(authorization)
    
    try:
        chats = db.query(ChatHistory).filter(
            ChatHistory.user_id == user_id,
            ChatHistory.is_archived == int(is_archived)
        ).order_by(ChatHistory.last_message_at.desc()).all()
        
        return [
            ChatHistoryResponse(
                id=chat.id,
                user_id=chat.user_id,
                title=chat.title,
                context=chat.context,
                model_source=ModelSource(chat.model_source),
                messages=[Message(**msg) for msg in chat.messages],
                metadata=chat.metadata,
                created_at=chat.created_at,
                updated_at=chat.updated_at,
                is_archived=bool(chat.is_archived),
                last_message_at=chat.last_message_at
            )
            for chat in chats
        ]
    except Exception as e:
        logger.error(f"Failed to list chats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list chats: {str(e)}")

@router.put("/aalam/chats/{chat_id}", response_model=ChatHistoryResponse)
async def update_chat(
    chat_id: str,
    update: ChatHistoryUpdate,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """Update a chat conversation"""
    verify_token(authorization)
    
    try:
        chat = db.query(ChatHistory).filter(ChatHistory.id == chat_id).first()
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")
            
        if update.title is not None:
            chat.title = update.title
        if update.messages is not None:
            chat.messages = [msg.dict() for msg in update.messages]
        if update.metadata is not None:
            chat.metadata = update.metadata
        if update.is_archived is not None:
            chat.is_archived = int(update.is_archived)
            
        db.commit()
        db.refresh(chat)
        
        return ChatHistoryResponse(
            id=chat.id,
            user_id=chat.user_id,
            title=chat.title,
            context=chat.context,
            model_source=ModelSource(chat.model_source),
            messages=[Message(**msg) for msg in chat.messages],
            metadata=chat.metadata,
            created_at=chat.created_at,
            updated_at=chat.updated_at,
            is_archived=bool(chat.is_archived),
            last_message_at=chat.last_message_at
        )
    except Exception as e:
        logger.error(f"Failed to update chat: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update chat: {str(e)}")

@router.post("/aalam/chats/{chat_id}/message", response_model=ChatMessageResponse)
async def send_message(
    chat_id: str,
    message: ChatMessageRequest,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """Send a message in a chat conversation"""
    verify_token(authorization)
    
    try:
        chat = db.query(ChatHistory).filter(ChatHistory.id == chat_id).first()
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")
            
        # Create user message
        user_message = Message(
            role="user",
            content=message.message,
            metadata=message.metadata
        )
        
        # Generate system prompt
        system_prompt = generate_system_prompt(message.context, message.model_source)
        
        # Prepare messages for OpenAI
        messages = [
            {"role": "system", "content": system_prompt},
            *[{"role": msg["role"], "content": msg["content"]} for msg in chat.messages],
            {"role": "user", "content": message.message}
        ]
        
        # Call OpenAI API
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=messages
        )
        
        # Create assistant message
        assistant_message = Message(
            role="assistant",
            content=response.choices[0].message.content,
            metadata={"model": "gpt-4"}
        )
        
        # Update chat history
        chat.messages.append(user_message.dict())
        chat.messages.append(assistant_message.dict())
        chat.last_message_at = datetime.utcnow()
        db.commit()
        
        # Log interaction
        await log_to_room_127(
            message.user_id,
            message.context,
            AalamResponse(
                user_id=message.user_id,
                context=message.context,
                response=assistant_message.content,
                source="📎 Aalam",
                confidence=1.0,
                timestamp=datetime.utcnow(),
                model_source=message.model_source,
                metadata=message.metadata
            ),
            db
        )
        
        return ChatMessageResponse(
            chat_id=chat.id,
            message=user_message,
            response=assistant_message,
            metadata=message.metadata,
            timestamp=datetime.utcnow()
        )
    except Exception as e:
        logger.error(f"Failed to send message: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to send message: {str(e)}")

@router.delete("/aalam/chats/{chat_id}")
async def delete_chat(
    chat_id: str,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """Delete a chat conversation"""
    verify_token(authorization)
    
    try:
        chat = db.query(ChatHistory).filter(ChatHistory.id == chat_id).first()
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")
            
        db.delete(chat)
        db.commit()
        
        return {"status": "success", "message": "Chat deleted successfully"}
    except Exception as e:
        logger.error(f"Failed to delete chat: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete chat: {str(e)}")
