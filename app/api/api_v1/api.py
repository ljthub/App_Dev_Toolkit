from fastapi import APIRouter

from api.api_v1.endpoints import auth, users, notifications, files, admin

api_router = APIRouter()

# 身份驗證相關路由
api_router.include_router(auth.router, prefix="/auth", tags=["認證"])

# 用戶相關路由
api_router.include_router(users.router, prefix="/users", tags=["用戶"])

# 通知相關路由
api_router.include_router(notifications.router, prefix="/notifications", tags=["通知"])

# 檔案相關路由
api_router.include_router(files.router, prefix="/files", tags=["檔案"])

# 管理員路由
api_router.include_router(admin.router, prefix="/admin", tags=["管理員"]) 