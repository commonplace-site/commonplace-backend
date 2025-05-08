import os
from dotenv import load_dotenv
from fastapi import FastAPI ,APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from app.api.v1 import router as all_routes


load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 1))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SYNESTHESIA_API_KEY = os.getenv("SYNESTHESIA_API_KEY")



app=FastAPI(
    title="Language Learning Ai  Backend",
    description="Backend services for Ai-powered language Learning, roleplay, and teacher support.",
    version="1.0.0",
)
api_router=APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
# origins=[
#     "http://localhost",
#     "http://localhost:3000",
#     "site Domain"
# ]

TEMP_AUDIO_DIR = "./tmp_audio"
os.makedirs(TEMP_AUDIO_DIR, exist_ok=True)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.include_router(auth.router,prefix='/auth',tags=["Auth"])
# app.include_router(users.router,prefix="/users",tags=["Users"])
app.include_router(all_routes,prefix="/api")

@app.get("/")
def read_root():
    return{"message": "Welcome to the Language Learning Ai Backend"}
























