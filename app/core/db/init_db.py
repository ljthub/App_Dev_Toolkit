from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from loguru import logger

from core.config import settings
from core.db.base import Base
from models.user import User, Role

# 創建異步引擎
engine = create_async_engine(
    str(settings.SQLALCHEMY_DATABASE_URI),
    echo=False,
    future=True,
)

# 創建異步會話工廠
async_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

async def init_db():
    """初始化數據庫"""
    try:
        # 創建所有表
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("數據庫表已成功創建")
        
    except Exception as e:
        logger.error(f"初始化數據庫時出錯: {str(e)}")
        raise

async def get_db():
    """獲取數據庫會話"""
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def init_minio():
    """初始化MinIO儲存服務，確保存儲桶存在"""
    try:
        from aiobotocore.session import get_session
        
        session = get_session()
        async with session.create_client(
            's3',
            endpoint_url=f"http://{settings.S3_ENDPOINT}",
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            region_name=settings.S3_REGION,
        ) as client:
            try:
                logger.info(f"檢查MinIO儲存桶是否存在: {settings.S3_BUCKET}")
                await client.head_bucket(Bucket=settings.S3_BUCKET)
            except Exception:
                logger.info(f"建立MinIO儲存桶: {settings.S3_BUCKET}")
                await client.create_bucket(Bucket=settings.S3_BUCKET)
                
        logger.info("MinIO初始化成功")
    except Exception as e:
        logger.error(f"MinIO初始化失敗: {e}")
        # 不要導致整個應用程序在MinIO失敗時無法啟動
        # 只記錄錯誤訊息 