from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from core.config import settings
from api.api_v1.api import api_router
from core.db.init_db import init_db

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="App開發工具箱API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# 設置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含API路由
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def startup_event():
    """應用程式啟動時執行的事件"""
    await init_db()

@app.get("/", tags=["健康檢查"])
async def health_check():
    """API健康檢查端點"""
    return {"status": "healthy", "message": "App Development Toolkit API運行中"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 