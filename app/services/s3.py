from io import BytesIO
import json
import uuid
import boto3, os
from uuid import uuid4

from app.core.config import Settings

s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
    aws_secret_access_key=os.getenv("AWS_SECRET_KEY"),
    region_name="us-west-2"
)

BUCKET_NAME = os.getenv("AWS_BUCKET_NAME", "commonplace-uploads")

async def upload_to_s3(file, folder: str):
    # filename = f"{folder}/{uuid4()}_{file.filename}"
    # s3.upload_fileobj(file.file, BUCKET_NAME, filename)
    # return f"https://{BUCKET_NAME}.s3.amazonaws.com/{filename}"
    ext = file.filename.split('-')[-1]
    unique_name=f"{uuid.uuid4()}.{ext}"
    key=f"{folder}/{unique_name}"
    file.file.seek(0)
    s3.upload_fileobj(
        file.file,
        Settings.AWS_BUCKET_NAME,
        key,ExtraArgs={
            "ContentType":file.content_type,
        }
    )
    return key



def upload_metadata_to_s3(metadata: dict, folder: str) -> str:
    file_buffer = BytesIO()
    file_buffer.write(json.dumps(metadata).encode("utf-8"))
    
    filename = f"{folder}/{uuid4()}.json"
    content_type = "application/json"
    
    file_buffer.seek(0)
    s3.upload_fileobj(
        file_buffer,
        Settings.AWS_BUCKET_NAME,
        filename,
        ExtraArgs={"ContentType": content_type}
    )

    return f"https://{Settings.AWS_BUCKET_NAME}.s3.{Settings.AWS_REGION}.amazonaws.com/{filename}"