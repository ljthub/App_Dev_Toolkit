from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi_limiter import FastAPILimiter
import redis.asyncio as redis
from loguru import logger

from core.config import settings

# 創建基於 IP 地址的限流器
limiter = Limiter(key_func=get_remote_address)

async def setup_limiter(app: FastAPI):
    """設置 API 限流器"""
    try:
        # 連接 Redis
        redis_connection = redis.from_url(
            f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"
        )
        
        # 初始化 FastAPI Limiter
        await FastAPILimiter.init(redis_connection)
        
        # 添加異常處理器
        app.state.limiter = limiter
        app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
        
        logger.info("API 限流器已成功設置")
    except Exception as e:
        logger.error(f"設置 API 限流器時出錯: {str(e)}")
        
        # 如果 Redis 連接失敗，使用內存限流器
        logger.warning("使用內存限流器作為備用")
        app.state.limiter = limiter
        app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 自定義限流裝飾器
def rate_limit(limit: str, key_func=None):
    """
    自定義限流裝飾器
    
    參數:
        limit: 限流規則，例如 "5/minute"
        key_func: 自定義鍵函數，默認使用 IP 地址
    """
    if key_func is None:
        key_func = get_remote_address
    
    return limiter.limit(limit, key_func=key_func)

# 自定義限流響應
async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """自定義限流響應處理器"""
    return JSONResponse(
        status_code=429,
        content={
            "detail": "請求過於頻繁，請稍後再試",
            "limit": str(exc.limit),
            "reset_at": exc.reset_at.isoformat() if exc.reset_at else None
        }
    ) 