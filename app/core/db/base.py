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

# 注意：不要在這裡導入模型，以避免循環導入
# 相反，在 init_db.py 中導入所有模型 