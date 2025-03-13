from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from pydantic import BaseModel, EmailStr
from typing import List, Optional

from app.services.email_service import EmailService, get_email_service

router = APIRouter(tags=["電子郵件"])

class EmailSchema(BaseModel):
    to: List[EmailStr]
    subject: str
    body: str
    html_content: Optional[str] = None

@router.post("/email/send", status_code=status.HTTP_202_ACCEPTED)
async def send_email(
    email_data: EmailSchema,
    background_tasks: BackgroundTasks,
    email_service: EmailService = Depends(get_email_service)
):
    """
    發送電子郵件
    
    在後台任務中處理郵件發送，不會阻塞請求
    """
    try:
        # 將郵件發送添加為後台任務
        background_tasks.add_task(
            email_service.send_email,
            to=email_data.to,
            subject=email_data.subject,
            body=email_data.body,
            html_content=email_data.html_content
        )
        return {"message": "電子郵件已加入發送隊列"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"發送電子郵件時發生錯誤: {str(e)}"
        ) 