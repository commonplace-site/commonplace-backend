# Aalam API Documentation

## Overview
The Aalam API provides a comprehensive set of endpoints for natural language processing, code generation, speech-to-text, text-to-speech, and chat functionality.

## Authentication
All endpoints require authentication using a Bearer token in the Authorization header:
```
Authorization: Bearer your_token_here
```

## Base URL
```
http://localhost:8000/api
```

## Endpoints

### 1. Basic Aalam Interaction
```http
POST /aalam
```
Processes text input and returns Aalam's response.

**Request Body:**
```json
{
    "user_id": "string",
    "text": "string",
    "context": "string",
    "model_source": "AALAM",
    "metadata": {}
}
```

**Response:**
```json
{
    "user_id": "string",
    "context": "string",
    "response": "string",
    "source": "📎 Aalam",
    "confidence": 1.0,
    "timestamp": "string",
    "model_source": "string",
    "metadata": {}
}
```

### 2. Speech-to-Text (STT)
```http
POST /aalam/stt
```
Converts speech to text.

**Request Body:**
```json
{
    "user_id": "string",
    "audio_file": "file",
    "language": "string",
    "context": "string",
    "punctuate": true,
    "speaker_diarization": false,
    "word_timestamps": false
}
```

**Response:**
```json
{
    "user_id": "string",
    "context": "string",
    "response": "string",
    "transcription": "string",
    "confidence": 0.0,
    "word_timestamps": [],
    "speakers": []
}
```

### 3. Text-to-Speech (TTS)
```http
POST /aalam/tts
```
Converts text to speech.

**Request Body:**
```json
{
    "user_id": "string",
    "text": "string",
    "context": "string",
    "voice_name": "string",
    "audio_format": "string",
    "speaking_rate": 1.0,
    "pitch": 0.0
}
```

**Response:**
```json
{
    "user_id": "string",
    "context": "string",
    "response": "string",
    "audio_file": "string",
    "avatar_url": "string",
    "avatar_metadata": {}
}
```

### 4. Combined STT-TTS
```http
POST /aalam/tts-stt
```
Handles both speech-to-text and text-to-speech in one call.

**Request Body:**
```json
{
    "user_id": "string",
    "audio_file": "file",
    "language": "string",
    "context": "string",
    "voice_name": "string",
    "audio_format": "string"
}
```

**Response:**
```json
{
    "user_id": "string",
    "context": "string",
    "response": "string",
    "audio_file": "string",
    "transcription": "string",
    "avatar_url": "string"
}
```

### 5. Conversation
```http
POST /aalam/conversation
```
Handles complete conversation flow with STT, processing, and TTS.

**Request Body (Form Data):**
```
audio_file: file
user_id: string
context: string
model_source: string
language: string
voice_name: string
audio_format: string
```

**Response:**
```json
{
    "user_id": "string",
    "context": "string",
    "response": "string",
    "audio_file": "string",
    "transcription": "string",
    "avatar_url": "string",
    "avatar_metadata": {}
}
```

### 6. Chat Management

#### Create Chat
```http
POST /aalam/chats
```
Creates a new chat conversation.

**Request Body:**
```json
{
    "user_id": "string",
    "title": "string",
    "context": "string",
    "model_source": "string",
    "messages": [],
    "metadata": {}
}
```

#### Get Chat
```http
GET /aalam/chats/{chat_id}
```
Retrieves a specific chat conversation.

#### List Chats
```http
GET /aalam/chats?user_id={user_id}&is_archived={boolean}
```
Lists all chats for a user.

#### Update Chat
```http
PUT /aalam/chats/{chat_id}
```
Updates a chat conversation.

#### Send Message
```http
POST /aalam/chats/{chat_id}/message
```
Sends a message in a chat conversation.

#### Delete Chat
```http
DELETE /aalam/chats/{chat_id}
```
Deletes a chat conversation.

### 7. Content Management

#### Content Vetting
```http
POST /aalam/vet
```
Submits content for vetting.

**Request Body:**
```json
{
    "user_id": "string",
    "text": "string",
    "context": "string",
    "metadata": {}
}
```

#### List Modules
```http
GET /aalam/modules
```
Lists all learning modules.

#### Teacher Submission
```http
POST /aalam/teacher-submit
```
Submits teacher content.

#### Module Submission
```http
POST /aalam/module-submit
```
Submits module content.

### 8. Arbitration

#### Arbitrate Content
```http
POST /aalam/arbitrate
```
Arbitrates content from other AI models.

#### Get Arbitration Status
```http
GET /aalam/arbitration/{request_id}
```
Gets the status of an arbitration request.

#### Review Arbitration
```http
PUT /aalam/arbitration/{request_id}/review
```
Reviews and updates an arbitration request.

## Error Handling
All endpoints return appropriate HTTP status codes:
- 200: Success
- 400: Bad Request
- 401: Unauthorized
- 404: Not Found
- 500: Internal Server Error

Error responses include a detail message:
```json
{
    "detail": "Error message"
}
```

## Rate Limiting
API calls are rate-limited to prevent abuse. The current limits are:
- 100 requests per minute per user
- 1000 requests per hour per user

## Best Practices
1. Always include proper error handling in your requests
2. Use appropriate content types in headers
3. Implement retry logic for failed requests
4. Cache responses when appropriate
5. Monitor your API usage

## Examples

### Basic Text Processing
```python
import requests

response = requests.post(
    "http://localhost:8000/api/aalam",
    headers={
        "Authorization": "Bearer your_token_here",
        "Content-Type": "application/json"
    },
    json={
        "user_id": "user123",
        "text": "Hello, how are you?",
        "context": "speak",
        "model_source": "AALAM"
    }
)
```

### Speech Processing
```python
import requests

with open("audio.wav", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/aalam/conversation",
        headers={
            "Authorization": "Bearer your_token_here"
        },
        files={"audio_file": f},
        data={
            "user_id": "user123",
            "context": "speak",
            "language": "en-US",
            "voice_name": "en-US-JennyNeural"
        }
    )
```

## Support
For API support or to report issues, please contact:
- Email: support@aalam.ai
- Documentation: https://docs.aalam.ai
- GitHub: https://github.com/aalam/backend 