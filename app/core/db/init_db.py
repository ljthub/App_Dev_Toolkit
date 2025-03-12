import asyncio
from loguru import logger

from core.db.session import engine, SessionLocal
from core.db.base import Base
from core.config import settings

async def init_db() -> None:
    """初始化數據庫，創建所有表並填充初始數據"""
    try:
        # 創建所有SQLAlchemy表
        async with engine.begin() as conn:
            logger.info("正在創建資料庫表...")
            await conn.run_sync(Base.metadata.create_all)
        logger.info("資料庫表創建成功")

        # 初始化MinIO (S3相容儲存)
        await init_minio()
        
        # 這裡可以添加其他數據庫初始化操作
        # 例如創建管理員帳戶、填充基本數據等
        
    except Exception as e:
        logger.error(f"資料庫初始化失敗: {e}")
        raise

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