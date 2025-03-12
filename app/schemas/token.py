from typing import Optional
from pydantic import BaseModel


class Token(BaseModel):
    """令牌模型"""
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    """令牌載荷模型"""
    sub: Optional[str] = None
    exp: Optional[int] = None
    role: Optional[str] = None 