import tempfile
from fastapi import APIRouter, Depends, UploadFile, File
import os
import openai
import whisper 
from app.core.utils import get_current_user


router=APIRouter(tags=["ShadowBank"])

model = whisper.load_model("base")

@router.post("/shadowbank/upload")
async def upload_voice(
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user)
):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    result = model.transcribe(tmp_path, language="zh")
    transcript = result["text"]

    os.remove(tmp_path)

    prompt = f"""你是中文口语老师。学生说了：\n\n"{transcript}"\n\n
请给予发音和流利度的反馈，指出一个可以改进的地方，用简洁、鼓励性的语言回复。"""

    gpt_response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    feedback = gpt_response.choices[0].message.content.strip()
    return {"transcript": transcript, "feedback": feedback}
