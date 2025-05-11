from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class UserCreate(BaseModel):
    first_Name: str
    last_Name: str
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class LoginSchema(BaseModel):
    email: EmailStr
    password: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

class ModelSource(str, Enum):
    AALAM = "aalam"
    CLAUDE = "claude"
    GEMINI = "gemini"
    TEACHER = "teacher"
    MODULE = "module"

class SubmissionStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_REVISION = "needs_revision"

class AalamInput(BaseModel):
    user_id: str
    text: str
    context: str
    model_source: Optional[ModelSource] = Field(ModelSource.AALAM, description="Source of the response")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")

class AalamTTSRequest(BaseModel):
    user_id: str
    text: str
    context: str
    model_source: Optional[ModelSource] = Field(ModelSource.AALAM, description="Source of the response")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")
    voice_name: Optional[str] = Field(None, description="Voice to use for TTS")
    audio_format: Optional[str] = Field("mp3", description="Output audio format")
    speaking_rate: Optional[float] = Field(1.0, description="Speaking rate (0.5 to 2.0)")
    pitch: Optional[float] = Field(0.0, description="Voice pitch adjustment (-10 to 10)")

class AalamSTTRequest(BaseModel):
    user_id: str
    audio_file: str
    context: str
    model_source: Optional[ModelSource] = Field(ModelSource.AALAM, description="Source of the response")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")
    language: Optional[str] = Field("zh-CN", description="Language code for transcription")
    punctuate: Optional[bool] = Field(True, description="Whether to add punctuation")
    speaker_diarization: Optional[bool] = Field(False, description="Whether to identify different speakers")
    word_timestamps: Optional[bool] = Field(False, description="Whether to include word-level timestamps")

class AalamResponse(BaseModel):
    user_id: str
    context: str
    response: str
    source: str
    confidence: float
    timestamp: datetime
    model_source: ModelSource
    metadata: Dict[str, Any]
    submission_status: Optional[SubmissionStatus] = None
    review_notes: Optional[str] = None
    audio_file: Optional[str] = None
    transcription: Optional[str] = None
    word_timestamps: Optional[List[dict]] = None
    speakers: Optional[List[dict]] = None

class TeacherSubmission(BaseModel):
    teacher_id: str
    content: str
    context: str
    module_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")

class ModuleSubmission(BaseModel):
    module_id: str
    content: str
    context: str
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")

class ArbitrationRequest(BaseModel):
    content: str
    context: str
    model_source: ModelSource
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")
    priority: Optional[int] = Field(1, description="Priority level for arbitration (1-5)")

class ArbitrationResponse(BaseModel):
    request_id: str
    content: str
    context: str
    model_source: ModelSource
    status: SubmissionStatus
    review_notes: Optional[str] = None
    metadata: Dict[str, Any]
    timestamp: datetime
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None

class Message(BaseModel):
    role: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class ChatHistoryCreate(BaseModel):
    user_id: str
    title: str
    context: str
    model_source: ModelSource
    messages: List[Message]
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class ChatHistoryUpdate(BaseModel):
    title: Optional[str] = None
    messages: Optional[List[Message]] = None
    metadata: Optional[Dict[str, Any]] = None
    is_archived: Optional[bool] = None

class ChatHistoryResponse(BaseModel):
    id: str
    user_id: str
    title: str
    context: str
    model_source: ModelSource
    messages: List[Message]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: Optional[datetime]
    is_archived: bool
    last_message_at: datetime

class ChatMessageRequest(BaseModel):
    user_id: str
    chat_id: str
    message: str
    context: str
    model_source: Optional[ModelSource] = Field(ModelSource.AALAM)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class ChatMessageResponse(BaseModel):
    chat_id: str
    message: Message
    response: Message
    metadata: Dict[str, Any]
    timestamp: datetime
