import os
import base64
from typing import List, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import googleapiclient.discovery
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError

from app.core.config import settings


class EmailService:
    """Gmail API 電子郵件服務"""
    
    def __init__(self, token_path: str = settings.TOKEN_PATH):
        """
        初始化 Gmail API 服務
        
        Args:
            token_path: OAuth 令牌文件路徑
        """
        self.token_path = token_path
        self.service = self._build_service()
    
    def _build_service(self):
        """建立 Gmail API 服務"""
        # 檢查令牌是否存在
        if not os.path.exists(self.token_path):
            raise FileNotFoundError(f"找不到 OAuth 令牌文件：{self.token_path}")
        
        try:
            # 從令牌文件加載憑證
            creds = Credentials.from_authorized_user_info(
                info=self._load_token(),
                scopes=["https://www.googleapis.com/auth/gmail.send"]
            )
            
            # 檢查憑證是否過期
            if creds.expired and creds.refresh_token:
                creds.refresh(Request())
                # 更新令牌文件
                with open(self.token_path, "w") as token_file:
                    token_file.write(creds.to_json())
            
            # 建立 Gmail API 服務
            return googleapiclient.discovery.build("gmail", "v1", credentials=creds)
        
        except RefreshError:
            raise Exception("令牌已過期且無法刷新，請重新生成 OAuth 令牌")
        except Exception as e:
            raise Exception(f"初始化 Gmail API 服務時發生錯誤: {str(e)}")
    
    def _load_token(self):
        """從文件加載 OAuth 令牌"""
        with open(self.token_path, "r") as token_file:
            return eval(token_file.read())
    
    def _create_message(self, to: List[str], subject: str, body: str, html_content: Optional[str] = None):
        """
        創建郵件訊息
        
        Args:
            to: 收件人列表
            subject: 郵件主題
            body: 純文本郵件內容
            html_content: HTML 格式郵件內容（可選）
        
        Returns:
            字典格式的郵件訊息
        """
        message = MIMEMultipart("alternative")
        message["to"] = ", ".join(to)
        message["subject"] = subject
        
        # 添加純文本內容
        message.attach(MIMEText(body, "plain"))
        
        # 如果提供了 HTML 內容，則添加 HTML 部分
        if html_content:
            message.attach(MIMEText(html_content, "html"))
        
        # 將訊息轉換為字典格式
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
        return {"raw": raw_message}
    
    async def send_email(self, to: List[str], subject: str, body: str, html_content: Optional[str] = None):
        """
        發送電子郵件
        
        Args:
            to: 收件人列表
            subject: 郵件主題
            body: 純文本郵件內容
            html_content: HTML 格式郵件內容（可選）
        
        Returns:
            發送結果訊息
        """
        try:
            # 創建郵件訊息
            message = self._create_message(to, subject, body, html_content)
            
            # 發送郵件
            result = self.service.users().messages().send(userId="me", body=message).execute()
            return result
        
        except Exception as e:
            raise Exception(f"發送電子郵件時發生錯誤: {str(e)}")


# 依賴注入函數
def get_email_service() -> EmailService:
    """
    獲取 EmailService 實例用於依賴注入
    
    Returns:
        EmailService 實例
    """
    return EmailService() 