# App_Dev_Toolkit 後端服務

這是一個基於 FastAPI 的後端服務框架，為 React Native 應用程式提供常用的後端功能。

## 功能概述

- 用戶系統：註冊、登入、JWT 認證、雙因素認證、角色權限管理
- 通知系統：電子郵件、推播通知、批量發送
- 檔案存儲：基於 S3 兼容的 MinIO 的檔案上傳、管理
- 管理後台：用戶管理、角色管理

## 開發環境設置

### 前置需求

- Docker 和 Docker Compose
- Python 3.11+（本地開發時）

### 啟動服務

使用 Docker Compose 啟動所有服務：

```bash
docker-compose up -d
```

API 服務將在 http://localhost:8000 上運行。

### API 文檔

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 專案結構

```
app/
├── api/                  # API 路由和端點
│   └── api_v1/           # API 版本 1
│       └── endpoints/    # API 端點模塊
├── core/                 # 核心功能
│   ├── config.py         # 配置設置
│   ├── security.py       # 安全相關功能
│   └── db/               # 數據庫相關
├── models/               # 數據模型
├── schemas/              # Pydantic 模型/數據驗證
├── services/             # 業務邏輯服務
├── main.py               # 應用程式入口點
└── requirements.txt      # 依賴包
```

## 開發指南

### 添加新的 API 端點

1. 在 `app/api/api_v1/endpoints/` 中創建新的模塊
2. 在 `app/api/api_v1/api.py` 中註冊新的路由器

### 添加新的數據模型

1. 在 `app/models/` 中創建新的模型文件
2. 在 `app/core/db/base.py` 中導入新模型

### 環境變量

應用程式使用 `.env` 文件進行配置。可以基於以下模板創建：

```
# 基本設置
SECRET_KEY=your_secret_key_here
ENVIRONMENT=development

# 數據庫設置
POSTGRES_SERVER=db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=app_db

# MinIO 設置
S3_ENDPOINT=minio:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
S3_BUCKET=app-files

# 郵件設置
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=user@example.com
SMTP_PASSWORD=password
EMAILS_FROM_EMAIL=info@example.com
```

## 測試

運行測試：

```bash
pytest
```

## 部署

本應用程式設計為在 Docker 環境中運行，可以輕鬆部署到任何支持 Docker 的平台。 