from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    username: str

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class OTPRequest(BaseModel):
    username: str

class OTPVerify(BaseModel):
    username: str
    otp: str
