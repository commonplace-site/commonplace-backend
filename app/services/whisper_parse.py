# # import whisper
# import tempfile
# from typing import Tuple, List
# from app.services.s3 import upload_to_s3

# # model = whisper.load_model("base")  


# FOLLOW_UP_STARTERS = ["为什么", "怎么", "可以", "能不能", "请问", "那", "还有", "你能", "是否", "有没有"]

# def parse_audio_with_whisper(file, bucket_name: str) -> Tuple[str, List[str]]:
    
#     file_url = upload_to_s3(file, bucket_name, file.filename)


#     with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
#         contents = file.file.read()
#         temp_audio.write(contents)
#         temp_audio_path = temp_audio.name

 
#     # result = model.transcribe(temp_audio_path, language="zh")
#     # transcript = result["text"]


#     tags = []
#     sentences = [s.strip() for s in transcript.replace("？", "。").split("。") if s.strip()]
#     for sentence in sentences:
#         if any(sentence.startswith(start) for start in FOLLOW_UP_STARTERS):
#             tags.append("follow-up")
#         else:
#             tags.append("original")

#     return transcript.strip(), tags, file_url
