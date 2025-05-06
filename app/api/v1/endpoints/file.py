from fastapi import APIRouter, UploadFile, File, Form, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.files import FileOut
# from db.SessionLocal import AsyncSessionLocal
from db.database import AsyncSessionLocal
from models.files import FileMetadata
from services.s3 import upload_to_s3
from utils.folder_classifier import classify_file_path


router = APIRouter()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.post("/upload", response_model=FileOut)
async def upload_file(
    user_id: str = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    #user = get_user_from_token(token)
    folder = classify_file_path(file.filename)
    s3_url = await upload_to_s3(file, folder)

    new_file = FileMetadata(
        filename=file.filename,
        s3_url=s3_url,
        uploaded_by=user_id,
        filetype=file.content_type,
    )
    db.add(new_file)
    await db.commit()
    await db.refresh(new_file)
    return new_file
