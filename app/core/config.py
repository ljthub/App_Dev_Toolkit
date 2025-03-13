import os
import secrets
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from typing import List

# 加載環境變數
load_dotenv()

class Settings(BaseSettings):
    """應用程序設置"""
    
    # 應用基本設置
    APP_NAME: str = "App_Dev_Toolkit"
    API_V1_STR: str = "/api/v1"
    
    # 安全設置
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS: int = 48
    
    # Email 設置
    TOKEN_PATH: str = os.getenv("TOKEN_PATH", "token.json")
    EMAILS_FROM_EMAIL: str = os.getenv("EMAILS_FROM_EMAIL", "noreply@example.com")
    EMAILS_FROM_NAME: str = os.getenv("EMAILS_FROM_NAME", "App_Dev_Toolkit")
    SERVER_HOST: str = os.getenv("SERVER_HOST", "localhost")
    
    # 驗證URL (前端頁面URL)
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:8081")
    FRONTEND_VERIFICATION_URL: str = os.getenv("FRONTEND_VERIFICATION_URL", "http://localhost:8081/(tabs)/verifyemail")
    
    # Gmail API設定
    GMAIL_TOKEN_PATH: str = os.getenv("GMAIL_TOKEN_PATH", "app/token.json")
    GMAIL_CREDENTIALS_PATH: str = os.getenv("GMAIL_CREDENTIALS_PATH", "client_secret.json")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# 創建全局設置實例
settings = Settings() 