
# from fastapi import APIRouter

# router = APIRouter(
#     # prefix="/user",
#     tags=["User"]
# )


# # Set your OpenAI API key here
# openai.api_key = "your-openai-api-key"

# @router.post("/avatar/")
# async def avatar_generate(text: str = Form(...), current_user: User = Depends(get_current_user)):
#     # Communicate with ChatGPT
#     response = openai.ChatCompletion.create(
#         model="gpt-4",  # or "gpt-3.5-turbo"
#         messages=[
#             {"role": "system", "content": "You are a helpful, human-like avatar assistant."},
#             {"role": "user", "content": text}
#         ]
#     )
    
#     reply = response['choices'][0]['message']['content']
#     return {"reply": reply}

















































































































