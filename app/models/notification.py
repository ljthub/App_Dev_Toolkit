from sqlalchemy import Column, String, Text, Boolean, Integer, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
import enum

from core.db.base import BaseModel

class NotificationType(str, enum.Enum):
    EMAIL = "email"
    PUSH = "push"
    SMS = "sms"
    IN_APP = "in_app"

class NotificationStatus(str, enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"

class Notification(BaseModel):
    """通知模型"""
    __tablename__ = "notifications"

    # 基本資訊
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    type = Column(Enum(NotificationType), nullable=False)
    status = Column(Enum(NotificationStatus), default=NotificationStatus.PENDING)
    
    # 發送設置
    scheduled_at = Column(String, nullable=True)  # ISO 格式的時間字符串
    sent_at = Column(String, nullable=True)  # ISO 格式的時間字符串
    
    # 關聯
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user = relationship("User", back_populates="notifications")
    
    # 目標信息
    target_email = Column(String(255), nullable=True)
    target_device = Column(String(255), nullable=True)  # FCM Token 或設備ID
    
    # 額外資料
    notification_metadata = Column(JSON, nullable=True)  # 存儲平台特定的元數據
    
    # 跟踪狀態
    is_read = Column(Boolean, default=False)
    is_delivered = Column(Boolean, default=False)
    error_message = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<Notification {self.id} - {self.type} - {self.status}>" 