from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
from typing import Dict, List, Any
import os
from fastapi.responses import RedirectResponse

from app.api.endpoints import email_router, auth_router

app = FastAPI(
    title="App_Dev_Toolkit API",
    description="基於 Docker 的 App 開發工具箱 API 服務",
    version="0.1.0"
)

# 配置 CORS 中間件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生產環境中應該限制為特定來源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 註冊路由
app.include_router(email_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")

# redirect to /docs
@app.get("/")
async def redirect_to_docs():
    return RedirectResponse(url="/docs")

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 