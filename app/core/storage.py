import os 
from uuid import uuid4

from fastapi import UploadFile
UPLOAD_DIR="uploads/audio"

# def save_audio_file(file,audio_type:str):
#     os.makedirs(f"{UPLOAD_DIR}/{audio_type}",exist_ok=True)
#     filename=f"{uuid4()}_{file.filename}"
#     path=f"{UPLOAD_DIR}/{audio_type}/{filename}"
#     with open(path,"wb")as buffer:
#         buffer.write(file.file.read())
#         return path
    
    
# def save_audio_file_to_s3(file: UploadFile, audio_type: str):
#     file_ext = file.filename.split(".")[-1]
#     file_key = f"{audio_type}/{uuid4()}.{file_ext}"

#     file.file.seek(0)  # Important: Reset file pointer before upload

#     try:
#         s3.upload_fileobj(
#             file.file,
#             settings.AWS_BUCKET_NAME,
#             file_key,
#             ExtraArgs={"ContentType": file.content_type}
#         )
#         s3_url = f"https://{AWS_BUCKET_NAME}.s3.{REGION}.amazonaws.com/{file_key}"
#         return s3_url
#     except NoCredentialsError:
#         raise Exception("AWS credentials not configured properly.")