from datetime import timedelta
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from core.config import settings
from core.db.session import get_db
from core.security import (
    create_access_token,
    get_password_hash,
    verify_password,
    verify_totp,
    generate_totp_secret,
    get_current_user,
)
from core.limiter import rate_limit
from models.user import User
from schemas.auth import (
    AccessToken,
    TokenData,
    UserCreate,
    UserLogin,
    TotpVerify,
    TotpSetup,
    UserVerifyEmail,
    ResetPassword,
    ChangePassword,
)
from schemas.token import Token
from schemas.user import UserResponse
from services.user import (
    get_user_by_email,
    create_user,
    activate_user,
    send_verification_email,
    send_password_reset_email,
    reset_user_password,
)

router = APIRouter()

@router.post("/register", response_model=AccessToken)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)) -> Any:
    """註冊新用戶並返回訪問令牌"""
    # 檢查用戶是否已存在
    existing_user = await get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="此電子郵件已被註冊",
        )
    
    # 建立新用戶
    user = await create_user(db, user_data)
    
    # 發送確認郵件
    await send_verification_email(user)
    
    # 生成訪問令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=AccessToken)
@rate_limit(settings.RATE_LIMIT_AUTH)
async def login(form_data: UserLogin, request: Request, db: AsyncSession = Depends(get_db)) -> Any:
    """登入並返回訪問令牌"""
    # 驗證用戶
    user = await get_user_by_email(db, form_data.email)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="電子郵件或密碼不正確",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 檢查用戶是否啟用
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用戶未啟用",
        )
    
    # 檢查是否需要雙因素驗證
    if user.is_2fa_enabled and not form_data.totp_code:
        return {"require_2fa": True}
    
    # 驗證雙因素驗證碼
    if user.is_2fa_enabled:
        if not verify_totp(user.totp_secret, form_data.totp_code):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="雙因素驗證碼不正確",
            )
    
    # 生成訪問令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/verify-email", response_model=dict)
async def verify_email(data: UserVerifyEmail, db: AsyncSession = Depends(get_db)) -> Any:
    """確認用戶電子郵件"""
    # 在真實系統中，這裡應該驗證令牌並啟用用戶帳戶
    user = await get_user_by_email(db, data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用戶不存在",
        )
    
    # 激活用戶
    await activate_user(db, user)
    
    return {"message": "電子郵件已驗證"}

@router.post("/2fa/setup", response_model=TotpSetup)
async def setup_2fa(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    """設置雙因素驗證"""
    # 生成 TOTP 秘鑰
    secret = generate_totp_secret()
    
    # 更新用戶記錄
    current_user.totp_secret = secret
    db.add(current_user)
    await db.commit()
    
    # 生成 QR 碼配置鏈接
    qr_code_uri = f"otpauth://totp/{settings.PROJECT_NAME}:{current_user.email}?secret={secret}&issuer={settings.PROJECT_NAME}"
    
    return {"secret": secret, "qr_code_uri": qr_code_uri}

@router.post("/2fa/verify", response_model=AccessToken)
async def verify_2fa(data: TotpVerify, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    """驗證雙因素驗證並啟用它"""
    if not verify_totp(current_user.totp_secret, data.totp_code):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="雙因素驗證碼不正確",
        )
    
    # 啟用雙因素驗證
    current_user.is_2fa_enabled = True
    db.add(current_user)
    await db.commit()
    
    # 生成訪問令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": current_user.email}, expires_delta=access_token_expires)
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/password-reset/request", response_model=dict)
async def request_password_reset(email: str, db: AsyncSession = Depends(get_db)) -> Any:
    """請求密碼重置"""
    user = await get_user_by_email(db, email)
    if user:
        # 發送密碼重置郵件
        await send_password_reset_email(user)
    
    # 不透露用戶是否存在
    return {"message": "如果帳戶存在，我們已發送密碼重置郵件"}

@router.post("/password-reset/confirm", response_model=dict)
async def confirm_password_reset(data: ResetPassword, db: AsyncSession = Depends(get_db)) -> Any:
    """確認密碼重置"""
    # 在真實系統中，這裡應該驗證令牌並重置密碼
    await reset_user_password(db, data.email, data.token, data.new_password)
    
    return {"message": "密碼已重置"}

@router.post("/signup", response_model=UserResponse)
@rate_limit(settings.RATE_LIMIT_SIGNUP)
async def create_user_signup(
    *,
    request: Request,
    db: Session = Depends(get_db),
    user_in: UserCreate,
) -> Any:
    """
    創建新用戶
    """
    # ... 現有代碼 ...

# ... 其他現有端點 ... 