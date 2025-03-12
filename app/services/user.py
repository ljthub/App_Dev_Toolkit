from typing import Optional, List, Any
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from itsdangerous import URLSafeTimedSerializer

from models.user import User, Role, RoleEnum
from schemas.auth import UserCreate, UserInDB
from core.security import get_password_hash
from core.config import settings

# 創建一個加密令牌的序列化器
serializer = URLSafeTimedSerializer(settings.SECRET_KEY)

async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """根據電子郵件獲取用戶"""
    result = await db.execute(select(User).where(User.email == email))
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
    
    # 分配角色給用戶
    user.roles.append(default_role)
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
    
    # 在實際應用中，這裡應該連接到電子郵件服務
    # 例如使用 fastapi-mail 或其他電子郵件客戶端
    # 這裡只是模擬郵件發送
    
    print(f"發送驗證郵件到 {user.email} 的令牌是: {token}")

async def send_password_reset_email(user: User) -> None:
    """發送密碼重置郵件"""
    # 生成重置令牌
    token = serializer.dumps(user.email, salt="password-reset")
    
    # 在實際應用中，這裡應該連接到電子郵件服務
    # 這裡只是模擬郵件發送
    
    print(f"發送密碼重置郵件到 {user.email} 的令牌是: {token}")

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