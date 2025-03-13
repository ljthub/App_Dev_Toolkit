# 🚀 **App_Dev_Toolkit**

> 基於 Docker 的 App 開發工具箱，讓 React Native 開發者可以快速配置常用後端服務

## 📋 功能列表

### 👤 使用者系統
 - [x] 🔐 註冊/登入功能
 - [x] 🔑 JWT 身份驗證
 - [x] ✉️ Email 確認機制

### 📬 通知系統
 - [x] 📧 Email 發信功能

### 💾 資料存儲服務
 - [ ] 🗃️ 關聯式資料庫 (MySQL, PostgreSQL)
 - [ ] 📄 NoSQL 資料庫 (MongoDB, Redis)

### 🔄 API 服務
 - [x] 🛣️ RESTful API 路由


## 🔧 使用方法

使用 Docker Compose 一鍵啟動所需服務：

```bash
docker-compose up -d
```

## 📱 Demo 應用

在 `./demo` 目錄中提供了一個基於 Expo React Native 的示範應用，用於展示本工具箱的功能：

### 功能演示
- 👤 使用者註冊與登入
- 🔑 JWT 身份驗證流程
- ✉️ 電子郵件驗證流程

### 運行 Demo

1. 安裝依賴：
```bash
cd demo
npm install
```

2. 啟動開發伺服器：
```bash
npx expo start
```

3. 使用 Expo Go 應用掃描 QR Code，或在模擬器中運行

### 設定 API 連接

在 `demo/constants/Config.ts` 文件中配置 API 連接資訊：
```typescript
export const API_URL = "http://localhost:8000";  // 調整為您的 API 伺服器位址
```

### 關於 token.json

`token.json` 是 Gmail API 的 OAuth 認證令牌，用於授權系統發送電子郵件。在我們的系統中有兩種方式可以獲得：

#### 1. 真實 OAuth 令牌（生產環境）

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