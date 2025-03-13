from google_auth_oauthlib.flow import InstalledAppFlow
import os

# 設定 Gmail API 權限範圍
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

# 指定 client_secret.json 位置
client_secret_file = "client_secret.json"

# 初始化 OAuth 流程，並設置 access_type 為 offline 以獲取 refresh token
flow = InstalledAppFlow.from_client_secrets_file(
    client_secret_file,
    SCOPES,
    redirect_uri='http://localhost:8080'
)

# 直接在 run_local_server 方法中設置所需參數
# 啟動本地授權伺服器
print("請在瀏覽器中完成 Google 帳號授權...")
creds = flow.run_local_server(
    port=8080,
    access_type='offline',
    prompt='consent'  # 強制顯示同意頁面以確保獲取 refresh token
)

# 保存令牌到文件
with open("app/token.json", "w") as token_file:
    token_file.write(creds.to_json())

print("OAuth 令牌已成功生成並保存至 token.json")
print(f"Refresh token 是否存在: {'refresh_token' in creds.to_json()}")