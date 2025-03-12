from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from core.db.session import get_db
from core.security import get_current_user
from models.user import User, UserRole, RoleEnum
from models.notification import Notification

router = APIRouter()

# 權限檢查函數
async def check_admin_permission(current_user: User = Depends(get_current_user)):
    """檢查用戶是否具有管理員權限"""
    admin_roles = [role for role in current_user.roles if role.role_type == RoleEnum.ADMIN]
    if not admin_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理員權限",
        )
    return current_user

@router.get("/users", response_model=dict)
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(check_admin_permission),
) -> Any:
    """獲取所有用戶（管理員專用）"""
    # 獲取總數
    total_query = select(func.count(User.id))
    total = await db.execute(total_query)
    total_count = total.scalar()
    
    # 獲取用戶列表
    users_query = select(User).offset(skip).limit(limit)
    result = await db.execute(users_query)
    users = result.scalars().all()
    
    # 格式化響應
    users_data = []
    for user in users:
        role_names = [role.name for role in user.roles] if user.roles else []
        users_data.append({
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "roles": role_names,
            "created_at": user.created_at.isoformat() if user.created_at else None,
        })
    
    return {
        "items": users_data,
        "total": total_count
    }

@router.post("/users/{user_id}/activate", response_model=dict)
async def activate_user_admin(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(check_admin_permission),
) -> Any:
    """激活用戶（管理員專用）"""
    # 獲取用戶
    user_query = select(User).where(User.id == user_id)
    result = await db.execute(user_query)
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用戶不存在",
        )
    
    # 更新用戶狀態
    user.is_active = True
    db.add(user)
    await db.commit()
    
    return {"message": f"用戶 {user.username} 已激活"}

@router.post("/users/{user_id}/deactivate", response_model=dict)
async def deactivate_user_admin(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(check_admin_permission),
) -> Any:
    """禁用用戶（管理員專用）"""
    # 獲取用戶
    user_query = select(User).where(User.id == user_id)
    result = await db.execute(user_query)
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用戶不存在",
        )
    
    # 確保不能禁用自己
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能禁用自己的帳戶",
        )
    
    # 更新用戶狀態
    user.is_active = False
    db.add(user)
    await db.commit()
    
    return {"message": f"用戶 {user.username} 已禁用"}

@router.get("/roles", response_model=dict)
async def list_roles(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(check_admin_permission),
) -> Any:
    """獲取所有角色（管理員專用）"""
    query = select(UserRole)
    result = await db.execute(query)
    roles = result.scalars().all()
    
    roles_data = [{
        "id": role.id,
        "name": role.name,
        "description": role.description,
        "role_type": role.role_type,
    } for role in roles]
    
    return {
        "items": roles_data,
        "total": len(roles_data)
    }

@router.post("/roles", response_model=dict)
async def create_role(
    name: str,
    description: Optional[str] = None,
    role_type: RoleEnum = RoleEnum.USER,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(check_admin_permission),
) -> Any:
    """創建新角色（管理員專用）"""
    # 檢查角色名稱是否已存在
    existing_query = select(UserRole).where(UserRole.name == name)
    existing = await db.execute(existing_query)
    if existing.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="角色名稱已存在",
        )
    
    # 創建新角色
    role = UserRole(
        name=name,
        description=description,
        role_type=role_type
    )
    
    db.add(role)
    await db.commit()
    await db.refresh(role)
    
    return {
        "message": "角色創建成功",
        "id": role.id,
        "name": role.name,
        "role_type": role.role_type
    }

@router.post("/users/{user_id}/roles/{role_id}", response_model=dict)
async def assign_role_to_user(
    user_id: int,
    role_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(check_admin_permission),
) -> Any:
    """為用戶分配角色（管理員專用）"""
    # 獲取用戶
    user_query = select(User).where(User.id == user_id)
    user_result = await db.execute(user_query)
    user = user_result.scalars().first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用戶不存在",
        )
    
    # 獲取角色
    role_query = select(UserRole).where(UserRole.id == role_id)
    role_result = await db.execute(role_query)
    role = role_result.scalars().first()
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在",
        )
    
    # 檢查用戶是否已有該角色
    if role in user.roles:
        return {"message": f"用戶 {user.username} 已具有角色 {role.name}"}
    
    # 分配角色
    user.roles.append(role)
    db.add(user)
    await db.commit()
    
    return {"message": f"角色 {role.name} 已分配給用戶 {user.username}"} 