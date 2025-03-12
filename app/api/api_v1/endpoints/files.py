from typing import Any, List, Optional
import os
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from sqlalchemy.ext.asyncio import AsyncSession
from aiobotocore.session import get_session

from core.db.session import get_db
from core.security import get_current_user
from core.config import settings
from models.user import User

router = APIRouter()

@router.post("/upload", response_model=dict)
async def upload_file(
    file: UploadFile = File(...),
    folder: Optional[str] = Form("default"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """上傳文件到S3兼容存儲"""
    try:
        # 生成唯一文件名
        file_ext = os.path.splitext(file.filename)[1] if file.filename else ""
        file_name = f"{folder}/{uuid.uuid4()}{file_ext}"
        
        # 讀取文件內容
        content = await file.read()
        
        # 上傳到S3
        session = get_session()
        async with session.create_client(
            's3',
            endpoint_url=f"http://{settings.S3_ENDPOINT}",
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            region_name=settings.S3_REGION,
        ) as client:
            await client.put_object(
                Bucket=settings.S3_BUCKET,
                Key=file_name,
                Body=content,
                ContentType=file.content_type
            )
        
        # 構建URL
        file_url = f"http://{settings.S3_ENDPOINT}/{settings.S3_BUCKET}/{file_name}"
        
        return {
            "message": "文件上傳成功",
            "file_name": file_name,
            "file_url": file_url,
            "file_size": len(content),
            "content_type": file.content_type
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件上傳失敗: {str(e)}",
        )

@router.get("/list", response_model=dict)
async def list_files(
    folder: Optional[str] = Query("default"),
    prefix: Optional[str] = Query(None),
    limit: int = Query(100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """列出S3儲存桶中的文件"""
    try:
        session = get_session()
        async with session.create_client(
            's3',
            endpoint_url=f"http://{settings.S3_ENDPOINT}",
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            region_name=settings.S3_REGION,
        ) as client:
            # 構建前綴
            prefix_path = f"{folder}/"
            if prefix:
                prefix_path += prefix
            
            # 列出對象
            response = await client.list_objects_v2(
                Bucket=settings.S3_BUCKET,
                Prefix=prefix_path,
                MaxKeys=limit
            )
            
            files = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    file_key = obj['Key']
                    file_url = f"http://{settings.S3_ENDPOINT}/{settings.S3_BUCKET}/{file_key}"
                    files.append({
                        "key": file_key,
                        "url": file_url,
                        "size": obj['Size'],
                        "last_modified": obj['LastModified'].isoformat(),
                    })
            
            return {
                "files": files,
                "count": len(files)
            }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"獲取文件列表失敗: {str(e)}",
        )

@router.delete("/{file_key:path}", response_model=dict)
async def delete_file(
    file_key: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """刪除S3儲存桶中的文件"""
    try:
        session = get_session()
        async with session.create_client(
            's3',
            endpoint_url=f"http://{settings.S3_ENDPOINT}",
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            region_name=settings.S3_REGION,
        ) as client:
            await client.delete_object(
                Bucket=settings.S3_BUCKET,
                Key=file_key
            )
            
        return {"message": "文件刪除成功"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件刪除失敗: {str(e)}",
        ) 