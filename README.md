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