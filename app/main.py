from fastapi import FastAPI, Depends
import uvicorn

from core.config import settings
from api.api_v1.api import api_router
from core.db.init_db import init_db
from core.middleware import setup_middlewares
from core.limiter import setup_limiter
from services.email_init import initialize_email_service

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="App開發工具箱API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# 設置中間件
setup_middlewares(app)

# 包含API路由
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def startup_event():
    """應用程式啟動時執行的事件"""
    # 初始化數據庫
    await init_db()
    
    # 設置 API 限流器
    await setup_limiter(app)
    
    # 初始化電子郵件服務
    await initialize_email_service()

@app.get("/", tags=["健康檢查"])
async def health_check():
    """API健康檢查端點"""
    return {"status": "healthy", "message": "App Development Toolkit API運行中"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 