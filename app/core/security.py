from datetime import datetime, timedelta
from typing import Optional
import uuid
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

# 密碼加密
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_user_id() -> str:
    """生成唯一的使用者ID"""
    return str(uuid.uuid4())

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """驗證密碼"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """獲取密碼雜湊值"""
    return pwd_context.hash(password)

def create_token(user_id: str, expires_delta: timedelta) -> str:
    """創建JWT令牌"""
    expire = datetime.utcnow() + expires_delta
    to_encode = {"sub": user_id, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def create_access_token(user_id: str) -> str:
    """創建訪問令牌"""
    return create_token(
        user_id=user_id,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

def create_verification_token(user_id: str) -> str:
    """創建電子郵件驗證令牌"""
    return create_token(
        user_id=user_id,
        expires_delta=timedelta(hours=settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS)
    ) 