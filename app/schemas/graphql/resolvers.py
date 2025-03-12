from typing import List, Optional
import strawberry
from sqlalchemy.orm import Session
from strawberry.types import Info

from models.user import User as UserModel
from models.notification import Notification as NotificationModel
from schemas.graphql.types import User, Notification, File, UserInput, NotificationInput
from core.db.session import get_db
from services.user import create_user as create_user_service
from services.notification import create_notification as create_notification_service
from core.security import get_current_user

async def get_db_session(info: Info) -> Session:
    """獲取數據庫會話"""
    return next(get_db())

async def get_users(db: Session) -> List[User]:
    """獲取所有用戶"""
    users = db.query(UserModel).all()
    return [
        User(
            id=str(user.id),
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
            created_at=user.created_at
        )
        for user in users
    ]

async def get_user_by_id(user_id: str, db: Session) -> Optional[User]:
    """根據ID獲取用戶"""
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        return None
    return User(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        created_at=user.created_at
    )

async def get_notifications(user_id: str, db: Session) -> List[Notification]:
    """獲取用戶的通知"""
    notifications = db.query(NotificationModel).filter(NotificationModel.user_id == user_id).all()
    return [
        Notification(
            id=str(notification.id),
            title=notification.title,
            content=notification.content,
            user_id=str(notification.user_id),
            read=notification.read,
            created_at=notification.created_at
        )
        for notification in notifications
    ]

async def create_user(user_input: UserInput, db: Session) -> User:
    """創建新用戶"""
    user = await create_user_service(
        db=db,
        email=user_input.email,
        password=user_input.password,
        full_name=user_input.full_name
    )
    return User(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        created_at=user.created_at
    )

async def create_notification(notification_input: NotificationInput, db: Session) -> Notification:
    """創建新通知"""
    notification = await create_notification_service(
        db=db,
        title=notification_input.title,
        content=notification_input.content,
        user_id=notification_input.user_id
    )
    return Notification(
        id=str(notification.id),
        title=notification.title,
        content=notification.content,
        user_id=str(notification.user_id),
        read=notification.read,
        created_at=notification.created_at
    ) 