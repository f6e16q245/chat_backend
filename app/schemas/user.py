from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr
    nickname: str
    bio: str
    avatar: str 
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ProfileUpdate(BaseModel):
    nickname: str | None = Field(default=None, min_length=2, max_length=50)
    bio: str | None = Field(default=None, max_length=500)
    avatar: str | None = Field(default=None, max_length=10)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class EmailVerifyRequest(BaseModel):
    email: EmailStr
    code: str = Field(min_length=6, max_length=6)


class ResendCodeRequest(BaseModel):
    email: EmailStr

class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=72)


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    email: EmailStr
    code: str = Field(min_length=6, max_length=6)
    new_password: str = Field(min_length=8, max_length=72)


class AccountDelete(BaseModel):
    password: str  # 본인 확인용