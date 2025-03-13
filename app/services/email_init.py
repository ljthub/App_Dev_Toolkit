"""
郵件服務初始化模塊
用於在應用啟動時設置 Gmail API 認證
"""

import os
import json
import base64
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from loguru import logger

from core.config import settings

async def initialize_email_service():
    """初始化電子郵件服務"""
    token_path = settings.EMAIL_TOKEN_PATH
    client_secret_file = settings.GOOGLE_CLIENT_SECRET_FILE

    logger.info(f"token_path: {token_path} {os.path.exists(token_path)}")
    logger.info(f"client_secret_file: {client_secret_file} {os.path.exists(client_secret_file)}")
    
    # 檢查憑證文件是否存在
    if not client_secret_file or not os.path.exists(client_secret_file):
        logger.warning(f"Google API 客戶端憑證文件不存在: {client_secret_file}")
        logger.warning("電子郵件功能將不可用。請參閱README文件獲取設置指南。")
        return False
    
    # 如果令牌存在，嘗試驗證它
    if os.path.exists(token_path):
        try:
            # 先讀取 token 文件確認是否包含所需欄位
            with open(token_path, 'r') as token_file:
                token_data = json.load(token_file)
                
            # 檢查是否缺少關鍵欄位
            if 'refresh_token' not in token_data:
                logger.error("OAuth令牌缺少必要的 refresh_token 欄位")
                logger.error("請重新執行 generate_token.py 腳本，確保設置了 access_type='offline'")
                return False
                
            # 如果所有欄位正確，再建立憑證
            creds = Credentials.from_authorized_user_file(token_path)
            if creds and not creds.expired:
                logger.info("Gmail API 認證成功")
                return True
            else:
                logger.error("Gmail API 認證已過期")
                return False
                
        except Exception as e:
            logger.error(f"讀取OAuth令牌失敗: {str(e)}")
    
    # 如果令牌不存在或已過期，則直接報錯
    logger.error("Gmail API 認證令牌不存在或已過期")
    logger.error("請按照文檔說明設置有效的OAuth認證令牌")
    return False

# 提供一個服務帳號認證的替代方法 (如果有服務帳號JSON文件)
async def create_service_account_token(service_account_file, token_path):
    """使用服務帳號創建令牌"""
    try:
        SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
        
        # 從服務帳號文件創建憑證
        credentials = service_account.Credentials.from_service_account_file(
            service_account_file, scopes=SCOPES)
            
        # 將憑證轉換為JSON格式並保存
        creds_data = {
            "token": "",
            "refresh_token": "",
            "token_uri": credentials.token_uri,
            "client_id": credentials.service_account_email,
            "client_secret": "",
            "scopes": credentials.scopes,
            "expiry": "2099-12-31T23:59:59.999Z"
        }
        
        with open(token_path, "w") as token_file:
            json.dump(creds_data, token_file)
            
        logger.info(f"Gmail API 服務帳號令牌已創建並保存至 {token_path}")
        return True
        
    except Exception as e:
        logger.error(f"服務帳號令牌創建失敗: {str(e)}")
        return False 