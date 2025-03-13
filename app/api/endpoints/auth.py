from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime
import uuid
from typing import Optional
from pydantic import BaseModel

from app.core.security import (
    verify_password, 
    get_password_hash, 
    create_access_token, 
    create_verification_token, 
    create_user_id
)
from app.models.user import UserCreate, User, Token, EmailVerificationRequest
from app.api.dependencies import get_users_db, save_users_db, get_user, get_user_by_id, get_current_active_user
from app.services.email_service import EmailService, get_email_service
from app.core.config import settings

router = APIRouter(tags=["認證"])

@router.post("/auth/register", response_model=User)
async def register(
    user_in: UserCreate,
    background_tasks: BackgroundTasks,
    email_service: EmailService = Depends(get_email_service)
):
    """
    註冊新使用者
    """
    users_db = get_users_db()
    
    # 檢查電子郵件是否已存在
    if get_user(email=user_in.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="此電子郵件已註冊"
        )
    
    # 創建新使用者
    user_id = create_user_id()
    hashed_password = get_password_hash(user_in.password)
    
    user = {
        "id": user_id,
        "email": user_in.email,
        "username": user_in.username,
        "hashed_password": hashed_password,
        "is_active": True,
        "is_verified": False,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": None
    }
    
    users_db[user_id] = user
    save_users_db(users_db)
    
    # 發送驗證電子郵件
    verification_token = create_verification_token(user_id)
    verification_url = f"{settings.FRONTEND_VERIFICATION_URL}?token={verification_token}"
    
    email_subject = f"歡迎註冊 {settings.APP_NAME} - 請驗證您的電子郵件"
    email_body = f"""
    親愛的 {user_in.username}，

    感謝您註冊 {settings.APP_NAME}！
    
    請點擊以下連結驗證您的電子郵件：
    {verification_url}
    
    此連結將在 {settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS} 小時後失效。
    
    如果您沒有註冊此帳號，請忽略此郵件。

    祝您使用愉快，
    {settings.EMAILS_FROM_NAME} 團隊
    """
    
    html_content = f"""
    <html>
      <body>
        <h2>歡迎註冊 {settings.APP_NAME}！</h2>
        <p>親愛的 <strong>{user_in.username}</strong>，</p>
        <p>感謝您註冊 {settings.APP_NAME}！</p>
        <p>請點擊以下按鈕驗證您的電子郵件：</p>
        <p>
          <a href="{verification_url}" style="padding: 10px 20px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 5px;">
            驗證電子郵件
          </a>
        </p>
        <p>或者，您可以複製以下連結並在瀏覽器中打開：</p>
        <p>{verification_url}</p>
        <p>此連結將在 {settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS} 小時後失效。</p>
        <p>如果您沒有註冊此帳號，請忽略此郵件。</p>
        <p>祝您使用愉快，<br>
        {settings.EMAILS_FROM_NAME} 團隊</p>
      </body>
    </html>
    """
    
    # 在背景任務中發送電子郵件
    background_tasks.add_task(
        email_service.send_email,
        to=[user_in.email],
        subject=email_subject,
        body=email_body,
        html_content=html_content
    )
    
    return User(
        id=user_id,
        email=user_in.email,
        username=user_in.username,
        is_active=True,
        is_verified=False,
        created_at=datetime.fromisoformat(user["created_at"]),
        updated_at=None
    )

@router.post("/auth/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    使用者登入並獲取訪問令牌
    """
    user = get_user(email=form_data.username)  # 在OAuth2中，username欄位用於電子郵件
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="電子郵件或密碼錯誤",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="電子郵件或密碼錯誤",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="使用者帳號已停用"
        )
    
    # 建立訪問令牌
    access_token = create_access_token(user.id)
    
    return Token(access_token=access_token)

@router.post("/auth/verify-email")
async def verify_email(
    verification_data: EmailVerificationRequest
):
    """
    驗證使用者電子郵件
    """
    try:
        from jose import jwt, JWTError
        
        # 解析驗證令牌
        payload = jwt.decode(
            verification_data.token, 
            settings.SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: str = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="無效的驗證令牌"
            )
        
        # 更新使用者為已驗證
        users_db = get_users_db()
        if user_id not in users_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="找不到使用者"
            )
        
        users_db[user_id]["is_verified"] = True
        users_db[user_id]["updated_at"] = datetime.utcnow().isoformat()
        save_users_db(users_db)
        
        return {"message": "電子郵件驗證成功"}
    
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="無效的驗證令牌"
        )

@router.post("/auth/resend-verification")
async def resend_verification(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    email_service: EmailService = Depends(get_email_service)
):
    """
    重新發送驗證電子郵件
    """
    if current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="使用者已經完成驗證"
        )
    
    # 發送驗證電子郵件
    verification_token = create_verification_token(current_user.id)
    verification_url = f"{settings.FRONTEND_VERIFICATION_URL}?token={verification_token}"
    
    email_subject = f"{settings.APP_NAME} - 電子郵件驗證"
    email_body = f"""
    親愛的 {current_user.username}，

    請點擊以下連結驗證您的電子郵件：
    {verification_url}
    
    此連結將在 {settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS} 小時後失效。

    祝您使用愉快，
    {settings.EMAILS_FROM_NAME} 團隊
    """
    
    html_content = f"""
    <html>
      <body>
        <h2>{settings.APP_NAME} - 電子郵件驗證</h2>
        <p>親愛的 <strong>{current_user.username}</strong>，</p>
        <p>請點擊以下按鈕驗證您的電子郵件：</p>
        <p>
          <a href="{verification_url}" style="padding: 10px 20px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 5px;">
            驗證電子郵件
          </a>
        </p>
        <p>或者，您可以複製以下連結並在瀏覽器中打開：</p>
        <p>{verification_url}</p>
        <p>此連結將在 {settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS} 小時後失效。</p>
        <p>祝您使用愉快，<br>
        {settings.EMAILS_FROM_NAME} 團隊</p>
      </body>
    </html>
    """
    
    # 在背景任務中發送電子郵件
    background_tasks.add_task(
        email_service.send_email,
        to=[current_user.email],
        subject=email_subject,
        body=email_body,
        html_content=html_content
    )
    
    return {"message": "驗證電子郵件已重新發送"}

@router.get("/auth/me", response_model=User)
async def get_me(
    current_user: User = Depends(get_current_active_user)
):
    """
    獲取當前登入使用者的資料
    """
    return current_user 

# 用於公開重新發送驗證郵件的模型
class PublicResendVerificationRequest(BaseModel):
    email: str

@router.post("/auth/public/resend-verification")
async def public_resend_verification(
    verification_request: PublicResendVerificationRequest,
    background_tasks: BackgroundTasks,
    email_service: EmailService = Depends(get_email_service)
):
    """
    公開API：重新發送驗證電子郵件，不需要登入，但需要提供電子郵件地址
    """
    # 檢查電子郵件是否存在
    user = get_user(email=verification_request.email)
    if not user:
        # 為了安全考慮，不透露用戶是否存在
        return {"message": "如果電子郵件已註冊，驗證郵件已發送"}
    
    # 檢查使用者是否已經驗證
    if user.is_verified:
        # 同樣，不透露用戶已驗證
        return {"message": "如果電子郵件已註冊，驗證郵件已發送"}
    
    # 發送驗證電子郵件
    verification_token = create_verification_token(user.id)
    verification_url = f"{settings.FRONTEND_VERIFICATION_URL}?token={verification_token}"
    
    email_subject = f"{settings.APP_NAME} - 電子郵件驗證"
    email_body = f"""
    親愛的 {user.username}，

    請點擊以下連結驗證您的電子郵件：
    {verification_url}
    
    此連結將在 {settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS} 小時後失效。

    祝您使用愉快，
    {settings.EMAILS_FROM_NAME} 團隊
    """
    
    html_content = f"""
    <html>
      <body>
        <h2>{settings.APP_NAME} - 電子郵件驗證</h2>
        <p>親愛的 <strong>{user.username}</strong>，</p>
        <p>請點擊以下按鈕驗證您的電子郵件：</p>
        <p>
          <a href="{verification_url}" style="padding: 10px 20px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 5px;">
            驗證電子郵件
          </a>
        </p>
        <p>或者，您可以複製以下連結並在瀏覽器中打開：</p>
        <p>{verification_url}</p>
        <p>此連結將在 {settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS} 小時後失效。</p>
        <p>祝您使用愉快，<br>
        {settings.EMAILS_FROM_NAME} 團隊</p>
      </body>
    </html>
    """
    
    # 在背景任務中發送電子郵件
    background_tasks.add_task(
        email_service.send_email,
        to=[user.email],
        subject=email_subject,
        body=email_body,
        html_content=html_content
    )
    
    return {"message": "如果電子郵件已註冊，驗證郵件已發送"} 