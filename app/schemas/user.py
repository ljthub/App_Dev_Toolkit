from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """用戶基本模型"""
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    is_active: Optional[bool] = True
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    profile_image: Optional[str] = None


class UserCreate(UserBase):
    """用戶創建模型"""
    email: EmailStr
    username: str
    password: str


class UserUpdate(UserBase):
    """用戶更新模型"""
    password: Optional[str] = None


class UserInDBBase(UserBase):
    """數據庫中的用戶模型基類"""
    id: Optional[int] = None

    class Config:
        from_attributes = True


class UserInDB(UserInDBBase):
    """數據庫中的用戶模型（包含密碼）"""
    hashed_password: str


class UserResponse(UserInDBBase):
    """用戶響應模型"""
    pass


class UserRoleBase(BaseModel):
    """角色基本模型"""
    name: str
    description: Optional[str] = None


class UserRoleCreate(UserRoleBase):
    """角色創建模型"""
    pass


class UserRoleUpdate(UserRoleBase):
    """角色更新模型"""
    name: Optional[str] = None


class UserRoleInDBBase(UserRoleBase):
    """數據庫中的角色模型基類"""
    id: Optional[int] = None

    class Config:
        from_attributes = True


class UserRoleResponse(UserRoleInDBBase):
    """角色響應模型"""
    pass 