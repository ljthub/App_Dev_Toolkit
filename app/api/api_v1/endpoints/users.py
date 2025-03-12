from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.db.session import get_db
from core.security import get_current_user
from models.user import User
from schemas.auth import UserResponse, ChangePassword
from services.user import get_user_by_id, update_user, delete_user, change_password

router = APIRouter()

@router.get("/me", response_model=UserResponse)
async def read_current_user(current_user: User = Depends(get_current_user)) -> Any:
    """獲取當前用戶資料"""
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_current_user(
    update_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """更新當前用戶資料"""
    # 確保只能更新允許的字段
    allowed_fields = {"username", "full_name", "phone_number", "profile_image"}
    filtered_data = {k: v for k, v in update_data.items() if k in allowed_fields}
    
    return await update_user(db, current_user, filtered_data)

@router.post("/me/change-password", response_model=dict)
async def change_current_user_password(
    password_data: ChangePassword,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """更改當前用戶密碼"""
    # 驗證當前密碼
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="當前密碼不正確",
        )
    
    # 變更密碼
    await change_password(db, current_user, password_data.new_password)
    
    return {"message": "密碼已更新成功"}

@router.delete("/me", response_model=dict)
async def delete_current_user(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """刪除當前用戶帳戶"""
    await delete_user(db, current_user)
    return {"message": "帳戶已刪除"}

# 以下是管理員端點，可以根據需要添加權限控制
@router.get("/{user_id}", response_model=UserResponse)
async def read_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """獲取特定用戶（需要管理員權限）"""
    # 這裡應該添加權限檢查，確認當前用戶是否有權訪問其他用戶信息
    
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用戶不存在",
        )
    return user 