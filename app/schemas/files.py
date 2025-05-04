from pydantic import BaseModel
from datetime import datetime

class FileOut(BaseModel):
    id: str
    filename: str
    s3_url: str
    uploaded_by: str
    folder: str
    filetype: str
    uploaded_at: datetime

    class Config:
        orm_mode = True
