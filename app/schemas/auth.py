from typing import Optional, Union, List
from pydantic import BaseModel, EmailStr, Field, validator

class TokenData(BaseModel):
    """令牌數據"""
    email: str

class AccessToken(BaseModel):
    """訪問令牌"""
    access_token: str
    token_type: str
    require_2fa: Optional[bool] = None

class UserBase(BaseModel):
    """用戶基礎模型"""
    email: EmailStr
    username: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    """用戶創建模型"""
    password: str
    password_confirm: str
    
    @validator('password_confirm')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('密碼不匹配')
        return v

class UserLogin(BaseModel):
    """用戶登錄模型"""
    email: EmailStr
    password: str
    totp_code: Optional[str] = None

class UserInDB(UserBase):
    """數據庫中的用戶模型"""
    id: int
    is_active: bool
    is_verified: bool
    is_2fa_enabled: bool
    roles: List[str] = []
    
    class Config:
        orm_mode = True

class UserResponse(UserBase):
    """用戶響應模型"""
    id: int
    is_active: bool
    is_verified: bool
    is_2fa_enabled: bool
    
    class Config:
        orm_mode = True

class UserVerifyEmail(BaseModel):
    """用戶郵箱驗證模型"""
    email: EmailStr
    token: str

class TotpSetup(BaseModel):
    """TOTP設置模型"""
    secret: str
    qr_code_uri: str

class TotpVerify(BaseModel):
    """TOTP驗證模型"""
    totp_code: str

class ResetPassword(BaseModel):
    """重置密碼模型"""
    email: EmailStr
    token: str
    new_password: str
    new_password_confirm: str
    
    @validator('new_password_confirm')
    def passwords_match(cls, v, values, **kwargs):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('密碼不匹配')
        return v

class ChangePassword(BaseModel):
    """修改密碼模型"""
    current_password: str
    new_password: str
    new_password_confirm: str
    
    @validator('new_password_confirm')
    def passwords_match(cls, v, values, **kwargs):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('密碼不匹配')
        return v 