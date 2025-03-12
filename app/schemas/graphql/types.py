import strawberry
from typing import List, Optional
from datetime import datetime

@strawberry.type
class User:
    id: str
    email: str
    full_name: Optional[str] = None
    is_active: bool
    is_superuser: bool
    created_at: datetime

@strawberry.type
class Notification:
    id: str
    title: str
    content: str
    user_id: str
    read: bool
    created_at: datetime

@strawberry.type
class File:
    id: str
    filename: str
    path: str
    content_type: str
    user_id: str
    size: int
    created_at: datetime

@strawberry.input
class UserInput:
    email: str
    password: str
    full_name: Optional[str] = None

@strawberry.input
class NotificationInput:
    title: str
    content: str
    user_id: str 