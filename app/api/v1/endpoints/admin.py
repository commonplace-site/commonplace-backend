from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.utils import role_required
from app.db.dependencies import get_db
from app.models.audio_file import AudioFile
from app.schemas.files import FileOut

router = APIRouter(
    # prefix="/user",
    tags=["Admin"]
)


@router.get("/admin/private-audios", response_model=List[FileOut])
def get_private_audios(db: Session = Depends(get_db), user: dict = Depends(role_required(["Admin", "Teacher"]))):
    return db.query(AudioFile).filter(AudioFile.audio_type == "private").all()
