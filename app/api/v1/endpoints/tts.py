
from fastapi import APIRouter, Depends, Form

from app.core.utils import get_current_user

router = APIRouter(
    # prefix="/user",
    tags=["User"]
)


@router.post("/tts")
async def text_to_speech(text: str = Form(...), current_user: User = Depends(get_current_user)):
    cache_key = f"tts-{text}"
    if cache_key in session_cache:
        return {"cached_audio_url": session_cache[cache_key]}
    
    response = await tts_generate(text)
    temp_audio_path = f"{TEMP_AUDIO_DIR}/{uuid.uuid4()}.mp3"
    with open(temp_audio_path, "wb") as f:
        f.write(await response.read())

    session_cache[cache_key] = temp_audio_path
    return {"audio_file": temp_audio_path}



# @router.post("/avatar/")
# async def avatar_generate(text: str = Form(...), current_user: User = Depends(get_current_user)):
#     video_url = await generate_avatar_speech(text)
#     return {"video_url": video_url}
