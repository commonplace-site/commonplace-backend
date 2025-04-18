import os
from fastapi import FastAPI ,APIRouter
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import router as all_routes




app=FastAPI(
    title="Language Learning Ai  Backend",
    description="Backend services for Ai-powered language Learning, roleplay, and teacher support.",
    version="1.0.0",
)
api_router=APIRouter()

origins=[
    "http://localhost",
    "http://localhost:3000",
    "site Domain"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
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