

# import os
# import shutil
# from fastapi import APIRouter, Depends, UploadFile
# from app.core.utils import get_current_user, stt_transcribe
# from app.models.users import User

# router = APIRouter(
#     # prefix="/auth",
#     tags=["stt"]
# )




# @router.post("/stt/")
# async def speech_to_text(file: UploadFile = File(...), current_user: User = Depends(get_current_user)):
#     temp_file_path = f"{TEMP_AUDIO_DIR}/{uuid.uuid4()}.wav"
#     with open(temp_file_path, "wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)

#     transcript = await stt_transcribe(temp_file_path)
#     os.remove(temp_file_path)
#     return {"transcript": transcript}




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
 