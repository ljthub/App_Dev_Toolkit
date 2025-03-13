import os
import secrets
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# 加載環境變數
load_dotenv()

class Settings(BaseSettings):
    """應用程序設置"""
    
    # 應用基本設置
    APP_NAME: str = "App_Dev_Toolkit API"
    API_V1_STR: str = "/api/v1"
    
    # 安全設置
    SECRET_KEY: str = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS: int = 24
    
    # Email 設置
    TOKEN_PATH: str = os.getenv("TOKEN_PATH", "token.json")
    EMAILS_FROM_NAME: str = os.getenv("EMAILS_FROM_NAME", "App_Dev_Toolkit")
    SERVER_HOST: str = os.getenv("SERVER_HOST", "localhost")
    
    # 驗證URL (前端頁面URL)
    FRONTEND_VERIFICATION_URL: str = os.getenv("FRONTEND_VERIFICATION_URL", "http://localhost:3000/verify")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# 創建全局設置實例
settings = Settings() 