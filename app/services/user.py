from typing import Optional, List, Any
from fastapi import HTTPException, status
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from itsdangerous import URLSafeTimedSerializer
from loguru import logger

from models.user import User, Role, RoleEnum
from schemas.auth import UserCreate, UserInDB
from core.security import get_password_hash
from core.config import settings
from services.email import send_verification_email as send_email_verification
from services.email import send_password_reset_email as send_email_reset

# 創建一個加密令牌的序列化器
serializer = URLSafeTimedSerializer(settings.SECRET_KEY)

async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """根據電子郵件獲取用戶"""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().first()

async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    """根據用戶名獲取用戶"""
    result = await db.execute(select(User).where(User.username == username))
    return result.scalars().first()

async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    """根據ID獲取用戶"""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalars().first()

async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
    """創建新用戶"""
    # 創建新的用戶對象
    user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        is_active=True,  # 可以根據需要設置為False，直到郵箱驗證
        is_verified=False
    )
    
    # 將新用戶添加到資料庫
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    # 獲取預設角色
    result = await db.execute(select(Role).where(Role.role_type == RoleEnum.USER))
    default_role = result.scalars().first()
    
    # 如果默認角色不存在，創建它
    if not default_role:
        default_role = Role(
            name="用戶",
            description="標準用戶角色",
            role_type=RoleEnum.USER
        )
        db.add(default_role)
        await db.commit()
        await db.refresh(default_role)
    
    # 使用直接的SQL語句關聯用戶和角色
    await db.execute(
        text("INSERT INTO user_role (user_id, role_id) VALUES (:user_id, :role_id)"),
        {"user_id": user.id, "role_id": default_role.id}
    )
    await db.commit()
    
    return user

async def activate_user(db: AsyncSession, user: User) -> User:
    """啟用用戶帳戶（電子郵件驗證後）"""
    user.is_verified = True
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def update_user(db: AsyncSession, user: User, update_data: dict) -> User:
    """更新用戶資料"""
    for key, value in update_data.items():
        # 確保不更新密碼
        if key != "password" and hasattr(user, key):
            setattr(user, key, value)
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def delete_user(db: AsyncSession, user: User) -> None:
    """刪除用戶"""
    await db.delete(user)
    await db.commit()

async def change_password(db: AsyncSession, user: User, new_password: str) -> User:
    """更改用戶密碼"""
    user.hashed_password = get_password_hash(new_password)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

# 郵件相關功能
async def send_verification_email(user: User) -> None:
    """發送電子郵件驗證郵件"""
    # 生成驗證令牌
    token = serializer.dumps(user.email, salt="email-verify")
    
    try:
        # 使用電子郵件服務發送驗證郵件
        await send_email_verification(
            email=user.email,
            username=user.username,
            token=token
        )
        logger.info(f"已發送驗證郵件到 {user.email}")
    except Exception as e:
        # 如果發送失敗，記錄錯誤但不中斷流程
        logger.error(f"發送驗證郵件失敗: {str(e)}")
        # 備用方案: 仍然打印令牌用於開發測試
        logger.debug(f"驗證令牌: {token}")

async def send_password_reset_email(user: User) -> None:
    """發送密碼重置郵件"""
    # 生成重置令牌
    token = serializer.dumps(user.email, salt="password-reset")
    
    try:
        # 使用電子郵件服務發送重置郵件
        await send_email_reset(
            email=user.email,
            username=user.username,
            token=token
        )
        logger.info(f"已發送密碼重置郵件到 {user.email}")
    except Exception as e:
        # 如果發送失敗，記錄錯誤但不中斷流程
        logger.error(f"發送密碼重置郵件失敗: {str(e)}")
        # 備用方案: 仍然打印令牌用於開發測試
        logger.debug(f"重置令牌: {token}")

async def reset_user_password(db: AsyncSession, email: str, token: str, new_password: str) -> None:
    """重置用戶密碼"""
    try:
        # 驗證令牌
        email_from_token = serializer.loads(token, salt="password-reset", max_age=3600)  # 1小時有效期
        
        # 檢查令牌中的電子郵件是否與提供的電子郵件匹配
        if email_from_token != email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="無效的令牌",
            )
        
        # 獲取用戶
        user = await get_user_by_email(db, email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用戶不存在",
            )
        
        # 更新密碼
        await change_password(db, user, new_password)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="無效的令牌或令牌已過期",
        ) 