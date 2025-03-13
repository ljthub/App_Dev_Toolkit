# 🚀 **App_Dev_Toolkit**

> 基於 Docker 的 App 開發工具箱，讓 React Native 開發者可以快速配置常用後端服務

## 📋 功能列表

### 👤 使用者系統
 - [x] 🔐 註冊/登入功能
 - [x] 🔑 JWT 身份驗證
 - [x] ✉️ Email 確認機制
 - [x] 🔢 TOTP/HOTP 雙重驗證
 - [x] 👥 角色與權限管理
 - [x] 🔄 OAuth 第三方登入 (Google, Facebook, Apple)

### 📬 通知系統
 - [x] 📧 Email 發信功能
 - [x] 📱 推播通知 (Firebase Cloud Messaging, Apple Push Notification)
 - [x] 📊 後台管理介面
 - [x] ⏱️ 定時批量發送
 - [x] 📝 通知模板管理

### 💾 資料存儲服務
 - [x] 🗃️ 關聯式資料庫 (MySQL, PostgreSQL)
 - [x] 📄 NoSQL 資料庫 (MongoDB, Redis)
 - [x] 📁 檔案存儲系統 (S3 兼容)
 - [ ] 🔄 資料同步機制
 - [ ] 📤 資料匯出/匯入工具
 - [ ] 💾 資料備份與還原

### 🔄 API 服務
 - [x] 🛣️ RESTful API 路由
 - [x] ⚡ GraphQL 支援
 - [x] 🔌 WebSocket 即時通訊
 - [x] 🚧 API 限流與保護
 - [x] 📖 自動生成 API 文檔

### 💬 即時通訊
 - [x] 💭 聊天系統 (個人/群組)
 - [x] 👍 反應與互動
 - [ ] 📎 多媒體訊息支援
 - [x] 📡 在線狀態偵測
 - [x] 📝 已讀/未讀狀態

### 💰 支付系統
 - [ ] 💳 多種支付方式整合 (信用卡, PayPal)
 - [ ] 📊 交易記錄追蹤
 - [ ] 🧾 發票生成
 - [ ] 💱 多幣別支援
 - [ ] 🔐 支付安全保障

### 📊 分析與監控
 - [ ] 📈 用戶行為分析
 - [ ] 🔍 搜尋引擎
 - [ ] 🚥 系統健康監控
 - [ ] 📝 日誌收集與分析
 - [ ] 🧪 A/B 測試框架

### 🌐 其他實用工具
 - [ ] 🌍 多語言本地化支援
 - [ ] 🗺️ 地理位置服務
 - [ ] 🔗 社交媒體整合
 - [ ] 🧩 內容管理系統 (CMS)
 - [ ] 🔒 安全性工具 (防 DDoS, 防 XSS)

## 🔧 使用方法

使用 Docker Compose 一鍵啟動所需服務：

```bash
docker-compose up -d
```

API 文檔可在以下地址訪問：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- GraphQL Playground: http://localhost:8000/api/v1/graphql/playground

## 🛠️ 技術架構

- 容器化: Docker 🐳
- 編排: Docker Compose
- 前端範例: React Native
- 後端: Python, FastAPI
- 資料庫: MongoDB, Redis, PostgreSQL
- 快取: Redis
- 訊息佇列: RabbitMQ
- 檔案儲存: MinIO (S3 兼容)
- API: RESTful, GraphQL
- 即時通訊: WebSocket
- 安全: API 限流, IP 封鎖, 請求過濾

## 🧰 環境變數配置

應用程式使用 `.env` 文件進行配置，主要設置如下：

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

# 安全設置
ALLOWED_HOSTS=localhost,127.0.0.1
RATE_LIMIT_DEFAULT=100/minute
RATE_LIMIT_AUTH=20/minute
RATE_LIMIT_SIGNUP=5/minute
```

## 📧 電子郵件服務配置

系統使用 Google Gmail API 發送電子郵件，需要配置 Google Cloud Platform 憑證：

### 取得 Google API 憑證

1. 前往 [Google Cloud Console](https://console.cloud.google.com/)
2. 建立新專案或選擇現有專案
3. 啟用 Gmail API
   - 點擊 "API 和服務" > "程式庫"
   - 搜尋 "Gmail API" 並啟用
4. 建立 OAuth 憑證
   - 點擊 "API 和服務" > "憑證"
   - 點擊 "建立憑證" > "OAuth 客戶端 ID"
   - 應用程式類型選擇 "Web 應用程式"
   - 名稱輸入 "App Dev Toolkit Email Service"
   - 新增授權重新導向 URI: `http://localhost:8080`
   - 點擊 "建立"
5. 下載 JSON 格式的憑證
   - 在憑證頁面找到剛建立的 OAuth 客戶端 ID
   - 點擊下載 JSON 按鈕
   - 將檔案重命名為 `client_secret.json`

### 配置 Docker Compose

將下載的 `client_secret.json` 文件放在專案根目錄，然後修改 `docker-compose.yml`：

```yaml
services:
  api:
    # ... 其他設定 ...
    volumes:
      - ./app:/app
      - ./client_secret.json:/app/client_secret.json
    environment:
      # ... 其他環境變數 ...
      - GOOGLE_CLIENT_SECRET_FILE=/app/client_secret.json
      - EMAIL_TOKEN_PATH=/app/token.json
```

### 關於 token.json

`token.json` 是 Gmail API 的 OAuth 認證令牌，用於授權系統發送電子郵件。在我們的系統中有兩種方式可以獲得：

#### 1. 自動生成模擬令牌（開發環境）

在開發環境中，系統會自動生成一個模擬令牌：

- 啟動服務後，當系統偵測到 `token.json` 不存在時，會自動創建一個模擬令牌
- 模擬令牌允許系統正常運行，但不會實際發送電子郵件
- 所有"發送"的電子郵件會被記錄到日誌中，並儲存在 `app/mock_emails/` 目錄下
- 您可以通過檢查日誌查看電子郵件內容：`docker-compose logs api | grep "模擬郵件"`

#### 2. 真實 OAuth 令牌（生產環境）

如需要實際發送電子郵件（如在生產環境），請遵循以下步驟獲取真實的 OAuth 令牌：

1. 在本地環境中安裝必要的套件：
   ```bash
   pip install google-auth-oauthlib google-api-python-client
   ```
   
2. 創建一個 Python 腳本 `generate_token.py`:
   ```python
   from google_auth_oauthlib.flow import InstalledAppFlow
   import os
   
   # 設定 Gmail API 權限範圍
   SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
   
   # 指定 client_secret.json 位置
   client_secret_file = "client_secret.json"
   
   # 初始化 OAuth 流程
   flow = InstalledAppFlow.from_client_secrets_file(
       client_secret_file,
       SCOPES,
       redirect_uri='http://localhost:8080'
   )
   
   # 啟動本地授權伺服器
   print("請在瀏覽器中完成 Google 帳號授權...")
   creds = flow.run_local_server(port=8080)
   
   # 保存令牌到文件
   with open("app/token.json", "w") as token_file:
       token_file.write(creds.to_json())
   
   print("OAuth 令牌已成功生成並保存至 token.json")
   ```
   
3. 執行此腳本：
   ```bash
   python generate_token.py
   ```
   
4. 按照提示在瀏覽器中授權您的應用程式
   - 您會被重定向到 Google 登入頁面
   - 登入後，授權您的應用程式訪問 Gmail
   - 成功授權後，瀏覽器會自動重定向到 localhost
   
5. 授權完成後，`token.json` 文件會自動保存到當前目錄
   
6. 將生成的 `token.json` 文件複製到項目根目錄，確保 docker-compose 可以掛載它

注意：OAuth 令牌有一定的有效期，通常需要定期刷新。在生產環境中，您可能需要實現令牌刷新機制，或定期手動更新令牌。

## 👨‍💻 開發中功能

以下功能正在開發中：
- 聊天系統多媒體支援
- 支付系統整合
- 資料分析與監控
- 多語言本地化支援

歡迎提出建議和貢獻！

## 📂 專案結構

```
app/
├── api/                  # API 路由和端點
│   └── api_v1/           # API 版本 1
│       └── endpoints/    # API 端點模塊
│           └── websocket/ # WebSocket 相關模塊
├── core/                 # 核心功能
│   ├── config.py         # 配置設置
│   ├── security.py       # 安全相關功能
│   ├── middleware.py     # 中間件和請求過濾
│   ├── limiter.py        # API 限流
│   └── db/               # 數據庫相關
├── models/               # 數據模型
├── schemas/              # Pydantic 模型/數據驗證
│   └── graphql/          # GraphQL 相關模型
├── services/             # 業務邏輯服務
├── main.py               # 應用程式入口點
└── requirements.txt      # 依賴包
```