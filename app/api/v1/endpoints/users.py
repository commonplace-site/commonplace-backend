from fastapi import APIRouter

router = APIRouter(
    # prefix="/user",
    tags=["User"]
)

@router.get("/userinfo")
def userinfo():
    return{"message":"User info route from /user prefix"}