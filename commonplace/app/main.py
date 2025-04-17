from fastapi import FastAPI 
from fastapi.middleware.cors import CORSMiddleware


app=FastAPI(
    title="Language Learning Ai  Backend",
    description="Backend services for Ai-powered language Learning, roleplay, and teacher support.",
    version="1.0.0"
)


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

@app.get("/")
def read_root():
    return{"message": "Welcome to the Language Learning Ai Backend"}