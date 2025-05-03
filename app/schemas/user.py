from pydantic import BaseModel,EmailStr

class UserCreate(BaseModel):
    first_Name:str
    last_Name:str
    email:EmailStr
    password:str

class Token(BaseModel):
    access_token: str
    token_type: str


class LoginSchema(BaseModel):
    email: EmailStr
    password: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str



class AalamInput(BaseModel):
    user_id: str
    text: str
    context: str
