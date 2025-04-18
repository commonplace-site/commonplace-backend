from fastapi import APIRouter

router = APIRouter(
    # prefix="/auth",
    tags=["auth"]
)



@router.get("/login")
def login():
    return {"message":"message user login will be here"}

