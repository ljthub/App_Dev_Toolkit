from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, DateTime, func
import datetime

# 創建所有 SQLAlchemy 模型的基類
Base = declarative_base()

class BaseModel(Base):
    """抽象基礎模型，提供共同欄位"""
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

# 從這裡導入所有模型，以便 init_db 可以找到它們
# 這樣可以確保所有的表在初始化時都被創建

# 用戶模型
from models.user import User, UserRole

# 通知模型
from models.notification import Notification

# 其他模型
# 根據需要添加導入 