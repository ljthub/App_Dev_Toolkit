from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from typing import Optional, Dict
import json
import os
from datetime import datetime

from app.core.config import settings
from app.models.user import User, UserInDB, TokenData

# OAuth2 密碼流程
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

# 模擬資料庫 - 在實際開發中應使用真實資料庫
USERS_FILE = "users.json"

def get_users_db() -> Dict[str, dict]:
    """
    獲取使用者資料庫
    """
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users_db(users_db: Dict[str, dict]) -> None:
    """
    保存使用者資料庫
    """
    with open(USERS_FILE, "w") as f:
        json.dump(users_db, f)

def get_user(email: str) -> Optional[UserInDB]:
    """
    通過電子郵件獲取使用者
    """
    users_db = get_users_db()
    for user_id, user_data in users_db.items():
        if user_data["email"] == email:
            return UserInDB(**user_data)
    return None

def get_user_by_id(user_id: str) -> Optional[UserInDB]:
    """
    通過ID獲取使用者
    """
    users_db = get_users_db()
    if user_id in users_db:
        return UserInDB(**users_db[user_id])
    return None

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    獲取當前登入的使用者
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="無效的認證憑證",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=user_id, exp=datetime.fromtimestamp(payload.get("exp")))
    except JWTError:
        raise credentials_exception
    
    user = get_user_by_id(user_id=token_data.user_id)
    if user is None:
        raise credentials_exception
    
    return User(
        id=user.id,
        email=user.email,
        username=user.username,
        is_active=user.is_active,
        is_verified=user.is_verified,
        created_at=user.created_at,
        updated_at=user.updated_at
    )

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    獲取當前活躍的使用者
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="帳號已停用")
    return current_user

async def get_current_verified_user(current_user: User = Depends(get_current_active_user)) -> User:
    """
    獲取當前已驗證的使用者
    """
    if not current_user.is_verified:
        raise HTTPException(status_code=400, detail="帳號尚未驗證")
    return current_user 