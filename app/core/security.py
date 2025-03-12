from datetime import datetime, timedelta
from typing import Any, Optional, Union

import pyotp
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.db.session import get_db
from models.user import User
from schemas.auth import TokenData

# JWT 相關配置
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

# 密碼加密
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """驗證密碼"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """生成密碼哈希"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """生成 JWT 令牌"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")

async def get_current_user(
    db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    """獲取當前已驗證的用戶"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="無法驗證憑證",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # 解碼 JWT 令牌
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except (JWTError, ValidationError):
        raise credentials_exception
    
    # 從資料庫中獲取用戶
    user = await get_user_by_email(db, token_data.email)
    if user is None:
        raise credentials_exception
    return user

# TOTP (雙因素認證) 相關功能
def generate_totp_secret() -> str:
    """生成TOTP秘鑰"""
    return pyotp.random_base32()

def verify_totp(secret: str, token: str) -> bool:
    """驗證TOTP令牌"""
    totp = pyotp.TOTP(secret)
    return totp.verify(token)

# 用戶服務依賴函數
async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """通過電子郵件獲取用戶"""
    from services.user import get_user_by_email as get_user
    return await get_user(db, email) 