import base64
import os
import json
from typing import List, Dict, Optional
from fastapi import HTTPException
from loguru import logger
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

from core.config import settings

# 獲取 OAuth 憑證
def get_credentials():
    """獲取 Google OAuth 憑證"""
    creds = None
    token_path = settings.EMAIL_TOKEN_PATH  # OAuth 驗證後的 Token 路徑
    
    if os.path.exists(token_path):
        try:
            creds = Credentials.from_authorized_user_file(token_path)
        except Exception as e:
            logger.error(f"讀取憑證錯誤: {str(e)}")
            raise HTTPException(status_code=500, detail=f"無法讀取憑證: {str(e)}")
    else:
        logger.error(f"憑證文件 {token_path} 不存在")
        raise HTTPException(status_code=500, detail="郵件服務憑證不存在，請參閱文檔進行設置")
    
    return creds

async def send_email(
    to: str, 
    subject: str, 
    body: str, 
    html_content: Optional[str] = None,
    attachments: List[Dict] = None
) -> bool:
    """
    發送電子郵件
    
    參數:
        to: 收件人電子郵件地址
        subject: 郵件主題
        body: 郵件純文本內容
        html_content: 郵件 HTML 內容 (可選)
        attachments: 附件列表，格式為 [{"filename": "xxx.pdf", "content": "base64_encoded_content"}]
    
    返回:
        成功發送返回 True，失敗拋出異常
    """
    try:
        creds = get_credentials()
        service = build("gmail", "v1", credentials=creds)
        
        # 創建郵件
        message = MIMEMultipart("alternative")
        message["to"] = to
        message["subject"] = subject
        
        # 添加純文本內容
        plain_part = MIMEText(body, 'plain', 'utf-8')
        message.attach(plain_part)
        
        # 如果提供了 HTML 內容，也添加它
        if html_content:
            html_part = MIMEText(html_content, 'html', 'utf-8')
            message.attach(html_part)
        
        # 處理附件
        if attachments:
            # 如果有附件，將郵件轉換為 mixed 型式
            mixed_message = MIMEMultipart("mixed")
            for header, value in message.items():
                mixed_message[header] = value
            
            for part in message.get_payload():
                mixed_message.attach(part)
            
            message = mixed_message
            
            for attachment in attachments:
                filename = attachment.get("filename")
                content = attachment.get("content")
                
                if filename and content:
                    try:
                        # 解碼 base64 內容
                        file_content = base64.b64decode(content)
                        part = MIMEApplication(file_content, _subtype="octet-stream")
                        part.add_header('Content-Disposition', 'attachment', filename=filename)
                        message.attach(part)
                    except Exception as e:
                        logger.error(f"附件處理錯誤: {str(e)}")
                        raise ValueError(f"附件處理錯誤: {str(e)}")
        
        # 編碼郵件
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
        
        # 發送郵件
        service.users().messages().send(
            userId="me",
            body={"raw": raw_message}
        ).execute()
        
        logger.info(f"已成功發送郵件到 {to}")
        return True
        
    except Exception as e:
        logger.error(f"發送郵件失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=f"發送郵件失敗: {str(e)}")

# 封裝特定類型的郵件發送
async def send_verification_email(email: str, username: str, token: str) -> None:
    """發送電子郵件驗證郵件"""
    subject = f"{settings.PROJECT_NAME} - 請驗證您的電子郵件"
    verification_url = f"{settings.FRONTEND_URL}/auth/verify-email?token={token}"
    
    # 純文本內容
    body = f"""
您好 {username}，

感謝您註冊 {settings.PROJECT_NAME}！請點擊以下鏈接驗證您的電子郵件地址：

{verification_url}

此鏈接將在24小時後過期。

如果您沒有註冊帳戶，請忽略此郵件。

祝好，
{settings.PROJECT_NAME} 團隊
"""

    # HTML 內容
    html_content = f"""
<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    <h2 style="color: #333;">驗證您的電子郵件</h2>
    <p>您好 {username}，</p>
    <p>感謝您註冊 {settings.PROJECT_NAME}！請點擊以下按鈕驗證您的電子郵件地址：</p>
    <div style="text-align: center; margin: 30px 0;">
        <a href="{verification_url}" style="background-color: #4CAF50; color: white; padding: 12px 20px; text-decoration: none; border-radius: 4px; font-weight: bold;">驗證電子郵件</a>
    </div>
    <p>或者，您可以複製以下鏈接到瀏覽器地址欄：</p>
    <p style="word-break: break-all; color: #666;">{verification_url}</p>
    <p>此鏈接將在24小時後過期。</p>
    <p>如果您沒有註冊帳戶，請忽略此郵件。</p>
    <p>祝好，<br>{settings.PROJECT_NAME} 團隊</p>
</div>
"""
    
    await send_email(
        to=email,
        subject=subject,
        body=body,
        html_content=html_content
    )

async def send_password_reset_email(email: str, username: str, token: str) -> None:
    """發送密碼重置郵件"""
    subject = f"{settings.PROJECT_NAME} - 密碼重置請求"
    reset_url = f"{settings.FRONTEND_URL}/auth/reset-password?token={token}&email={email}"
    
    # 純文本內容
    body = f"""
您好 {username}，

我們收到了重置您 {settings.PROJECT_NAME} 帳戶密碼的請求。請點擊以下鏈接重置您的密碼：

{reset_url}

此鏈接將在1小時後過期。

如果您沒有請求重置密碼，請忽略此郵件，您的帳戶安全沒有受到影響。

祝好，
{settings.PROJECT_NAME} 團隊
"""

    # HTML 內容
    html_content = f"""
<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    <h2 style="color: #333;">重置您的密碼</h2>
    <p>您好 {username}，</p>
    <p>我們收到了重置您 {settings.PROJECT_NAME} 帳戶密碼的請求。請點擊以下按鈕重置您的密碼：</p>
    <div style="text-align: center; margin: 30px 0;">
        <a href="{reset_url}" style="background-color: #2196F3; color: white; padding: 12px 20px; text-decoration: none; border-radius: 4px; font-weight: bold;">重置密碼</a>
    </div>
    <p>或者，您可以複製以下鏈接到瀏覽器地址欄：</p>
    <p style="word-break: break-all; color: #666;">{reset_url}</p>
    <p>此鏈接將在1小時後過期。</p>
    <p>如果您沒有請求重置密碼，請忽略此郵件，您的帳戶安全沒有受到影響。</p>
    <p>祝好，<br>{settings.PROJECT_NAME} 團隊</p>
</div>
"""
    
    await send_email(
        to=email,
        subject=subject,
        body=body,
        html_content=html_content
    ) 