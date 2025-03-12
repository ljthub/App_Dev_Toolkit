from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from core.config import settings

# 創建異步引擎
engine = create_async_engine(
    str(settings.SQLALCHEMY_DATABASE_URI).replace("postgresql://", "postgresql+asyncpg://"), 
    echo=False, 
    future=True
)

# 創建異步會話工廠
SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """依賴注入函數：獲取資料庫會話"""
    async with SessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# 導出 get_db 函數
__all__ = ["get_db"] 