from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """使用者基本資料模型"""
    email: EmailStr
    username: str


class UserCreate(UserBase):
    """使用者創建模型"""
    password: str


class UserLogin(BaseModel):
    """使用者登入模型"""
    email: EmailStr
    password: str


class User(UserBase):
    """使用者模型"""
    id: str
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserInDB(User):
    """資料庫中的使用者模型"""
    hashed_password: str


class Token(BaseModel):
    """令牌模型"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """令牌資料模型"""
    user_id: Optional[str] = None
    exp: Optional[datetime] = None


class EmailVerificationRequest(BaseModel):
    """電子郵件驗證請求模型"""
    token: str 