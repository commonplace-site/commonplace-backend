
import os
from fastapi import APIRouter, HTTPException, Header
from openai import OpenAI
from dotenv import load_dotenv
import openai
from app.core.utils import verify_token
from app.schemas.user import AalamInput

router = APIRouter(tags=["Aalam Integration"])

load_dotenv(dotenv_path=".env")

# Correct OpenAI client initialization
# client = openai(os.getenv("OPENAI_API_KEY"))
openai.api_key = os.getenv("OPENAI_API_KEY")
# api_key = os.getenv("OPENAI_API_KEY")


# client = OpenAI(api_key=openai_api_key)

def generate_system_prompt(text: str) -> str:
    if text == 'speak':
        return 'You are Aalam, a language tutor focused on spoken fluency. Keep responses brief and conversational.'
    elif text == 'write':
        return 'You are Aalam, helping the user practice structured writing. Offer suggestions, feedback, and alternatives.'
    elif text == 'explore':
        return 'You are Aalam, guiding the user through new ideas and language discovery. Offer insightful, unexpected responses.'
    else:
        return 'You are Aalam, a helpful language guide.'

# /api/aalam endpoint
# @router.post("/aalam")
# async def aalam_endpoint(data: AalamInput, authorization: str = Header(None)):
#     verify_token(authorization)

#     try:
#         response =  openai.chat.completions.create(
#             model="gpt-4",
#             # model="gpt-3.5-turbo",
#             messages=[
#                 {"role": "system", "content": f"You are Aalam, an AI guide helping users in context: {data.context}"},
#                 {"role": "user", "content": data.text},
#             ]
#         )
#         message = response.choices[0].message.content

#         return {
#             "user_id": data.user_id,
#             "context": data.context,
#             "response": message
#         }

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Aalam failed to respond: {str(e)}")

@router.post("/aalam")
async def aalam_endpoint(data: AalamInput, authorization: str = Header(None)):
    verify_token(authorization)  # Assuming the function verify_token exists

    try:
        # Generate system prompt based on mode
        system_prompt = generate_system_prompt(data.text)
        
        # Call OpenAI API to generate response
        response = openai.chat.completions.create(
            model="gpt-4",  # Or gpt-3.5-turbo based on your preference
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": data.text},
            ]
        )
        
        message = response.choices[0].message.content

        # Return the response
        return {
            "user_id": data.user_id,
            "context": data.context,
            "response": message
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Aalam failed to respond: {str(e)}")



# /api/reflect endpoint
@router.post("/reflect")
async def reflect_endpoint(data: AalamInput, authorization: str = Header(None)):
    verify_token(authorization)

    try:
        response =  openai.chat.completions.create(
            # model="gpt-4",
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a diagnostic assistant. Summarize the user's concern and recommend relevant modules."},
                {"role": "user", "content": data.text},
            ]
        )
        content = response.choices[0].message.content

        structured_response = {
            "summary": content.split("\n")[0],
            "recommended_modules": ["i1-radio", "shadowbank"]  # Optional: parse from response dynamically
        }

        return structured_response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reflection failed: {str(e)}")
