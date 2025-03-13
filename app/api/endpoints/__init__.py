from app.api.endpoints.email import router as email_router
from app.api.endpoints.auth import router as auth_router

__all__ = ["email_router", "auth_router"] 