import secrets
import json
from typing import Any, Dict, List, Optional, Union, Set

from pydantic import AnyHttpUrl, EmailStr, PostgresDsn, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    # CORS設置
    CORS_ORIGINS: Union[List[str], str] = ["*"]

    @field_validator("CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str):
            if v == "*":
                return ["*"]
            elif v.startswith("[") and v.endswith("]"):
                # 嘗試作為 JSON 解析
                try:
                    return json.loads(v)
                except:
                    pass
            # 否則按逗號分隔
            return [i.strip() for i in v.split(",") if i.strip()]
        return v

    PROJECT_NAME: str = "App Development Toolkit"
    
    # 環境設置
    ENVIRONMENT: str = "development"
    
    # 安全設置
    ALLOWED_HOSTS: List[str] = ["*"]
    
    @field_validator("ALLOWED_HOSTS", mode="before")
    def assemble_allowed_hosts(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if v == "*":
                return ["*"]
            # 按逗號分隔
            return [i.strip() for i in v.split(",") if i.strip()]
        return v
        
    BLOCKED_IPS: Set[str] = set()
    BLOCKED_USER_AGENTS: List[str] = [
        r".*[Ss]canner.*",
        r".*[Ss]craper.*",
        r".*[Bb]ot.*",
        r".*[Ss]pider.*",
        r".*[Cc]rawler.*",
    ]
    BLOCKED_PATHS: List[str] = [
        r".*\.php$",
        r".*\.asp$",
        r".*\.aspx$",
        r".*\.jsp$",
        r".*\.cgi$",
        r".*wp-admin.*",
        r".*wp-login.*",
    ]
    MAX_REQUEST_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # API 限流設置
    RATE_LIMIT_DEFAULT: str = "100/minute"
    RATE_LIMIT_AUTH: str = "20/minute"
    RATE_LIMIT_SIGNUP: str = "5/minute"
    
    # PostgreSQL 配置
    POSTGRES_SERVER: str = "db"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "app_db"
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    @field_validator("SQLALCHEMY_DATABASE_URI", mode="before")
    def assemble_db_connection(cls, v: Optional[str], info) -> Any:
        if isinstance(v, str):
            return v
        
        # 在 Pydantic V2 中，我們需要直接從類獲取值，而不是從 values 參數
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=cls.model_fields["POSTGRES_USER"].default,
            password=cls.model_fields["POSTGRES_PASSWORD"].default,
            host=cls.model_fields["POSTGRES_SERVER"].default,
            path=f"{cls.model_fields['POSTGRES_DB'].default or ''}",
        )

    # MongoDB 配置
    MONGO_SERVER: str = "mongo"
    MONGO_USER: str = "mongo"
    MONGO_PASSWORD: str = "mongo"
    MONGO_DB: str = "app_db"
    MONGO_URI: Optional[str] = None

    @field_validator("MONGO_URI", mode="before")
    def assemble_mongo_connection(cls, v: Optional[str], info) -> Any:
        if isinstance(v, str):
            return v
        
        # 在 Pydantic V2 中，我們需要直接從類獲取值
        user = cls.model_fields["MONGO_USER"].default
        password = cls.model_fields["MONGO_PASSWORD"].default
        server = cls.model_fields["MONGO_SERVER"].default
        db = cls.model_fields["MONGO_DB"].default
        return f"mongodb://{user}:{password}@{server}/{db}"

    # Redis 配置
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_URI: Optional[str] = None

    @field_validator("REDIS_URI", mode="before")
    def assemble_redis_connection(cls, v: Optional[str], info) -> Any:
        if isinstance(v, str):
            return v
        
        # 在 Pydantic V2 中，我們需要直接從類獲取值
        host = cls.model_fields["REDIS_HOST"].default
        port = cls.model_fields["REDIS_PORT"].default
        db = cls.model_fields["REDIS_DB"].default
        return f"redis://{host}:{port}/{db}"

    # S3 / MinIO 配置
    S3_ENDPOINT: str = "minio:9000"
    S3_ACCESS_KEY: str = "minioadmin"
    S3_SECRET_KEY: str = "minioadmin"
    S3_BUCKET: str = "app-files"
    S3_REGION: str = "us-east-1"
    
    # 前端 URL
    FRONTEND_URL: str = "http://localhost:8000/api/v1/"
    
    # Google API 配置
    GOOGLE_CLIENT_SECRET_FILE: Optional[str] = None
    EMAIL_TOKEN_PATH: str = "token.json"
    
    # Email 設置
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = 587
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[EmailStr] = None
    EMAILS_FROM_NAME: Optional[str] = None

    # RabbitMQ 設置
    RABBITMQ_URI: str = "amqp://guest:guest@rabbitmq:5672/"

    # FCM (Firebase Cloud Messaging) 配置
    FCM_CREDENTIALS_FILE: Optional[str] = None

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings() 