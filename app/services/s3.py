import boto3, os
from uuid import uuid4

s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
    aws_secret_access_key=os.getenv("AWS_SECRET_KEY"),
    region_name="us-west-2"
)

BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "commonplace-uploads")

async def upload_to_s3(file, folder: str):
    filename = f"{folder}/{uuid4()}_{file.filename}"
    s3.upload_fileobj(file.file, BUCKET_NAME, filename)
    return f"https://{BUCKET_NAME}.s3.amazonaws.com/{filename}"
