
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


# /api/aalam endpoint
@router.post("/aalam")
async def aalam_endpoint(data: AalamInput, authorization: str = Header(None)):
    verify_token(authorization)

    try:
        response =  openai.chat.completions.create(
            model="gpt-4",
            # model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"You are Aalam, an AI guide helping users in context: {data.context}"},
                {"role": "user", "content": data.text},
            ]
        )
        message = response.choices[0].message.content

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
