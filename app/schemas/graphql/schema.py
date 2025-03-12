from typing import List, Optional
import strawberry
from strawberry.types import Info
from sqlalchemy.orm import Session

from schemas.graphql.types import User, Notification, File, UserInput, NotificationInput
from schemas.graphql.resolvers import (
    get_db_session, 
    get_users, 
    get_user_by_id, 
    get_notifications,
    create_user,
    create_notification
)

@strawberry.type
class Query:
    @strawberry.field
    async def users(self, info: Info) -> List[User]:
        """獲取所有用戶"""
        db = await get_db_session(info)
        return await get_users(db)
    
    @strawberry.field
    async def user(self, info: Info, id: str) -> Optional[User]:
        """根據ID獲取用戶"""
        db = await get_db_session(info)
        return await get_user_by_id(id, db)
    
    @strawberry.field
    async def notifications(self, info: Info, user_id: str) -> List[Notification]:
        """獲取用戶的通知"""
        db = await get_db_session(info)
        return await get_notifications(user_id, db)

@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_user(self, info: Info, user_input: UserInput) -> User:
        """創建新用戶"""
        db = await get_db_session(info)
        return await create_user(user_input, db)
    
    @strawberry.mutation
    async def create_notification(self, info: Info, notification_input: NotificationInput) -> Notification:
        """創建新通知"""
        db = await get_db_session(info)
        return await create_notification(notification_input, db)

# 創建 schema
schema = strawberry.Schema(query=Query, mutation=Mutation) 