from sqlalchemy import Boolean, Column, String, Integer, ForeignKey, Table, Text, Enum
from sqlalchemy.orm import relationship
import enum

from core.db.base import BaseModel

# 用戶角色枚舉
class RoleEnum(str, enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"

# 用戶-角色關聯表
user_role = Table(
    "user_role",
    BaseModel.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
)

class User(BaseModel):
    """用戶模型"""
    __tablename__ = "users"

    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # 個人資料
    full_name = Column(String(100), nullable=True)
    phone_number = Column(String(20), nullable=True)
    profile_image = Column(String(255), nullable=True)
    
    # 雙因素認證
    is_2fa_enabled = Column(Boolean, default=False)
    totp_secret = Column(String(255), nullable=True)
    
    # 關聯
    roles = relationship("UserRole", secondary=user_role, back_populates="users")
    notifications = relationship("Notification", back_populates="user")
    
    # OAuth2 相關
    oauth_provider = Column(String(20), nullable=True)
    oauth_user_id = Column(String(255), nullable=True)
    
    def __repr__(self):
        return f"<User {self.username}>"


class UserRole(BaseModel):
    """角色模型"""
    __tablename__ = "roles"

    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    role_type = Column(Enum(RoleEnum), nullable=False, default=RoleEnum.USER)
    
    # 關聯
    users = relationship("User", secondary=user_role, back_populates="roles")
    
    def __repr__(self):
        return f"<Role {self.name}>" 