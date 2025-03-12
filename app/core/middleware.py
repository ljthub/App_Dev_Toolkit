from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
import time
from loguru import logger
import re
import ipaddress
from typing import List, Dict, Set, Optional

from core.config import settings

class APISecurityMiddleware(BaseHTTPMiddleware):
    """API 安全中間件"""
    
    def __init__(
        self, 
        app: FastAPI, 
        blocked_ips: Set[str] = None,
        blocked_user_agents: List[str] = None,
        blocked_paths: List[str] = None,
        max_request_size: int = 10 * 1024 * 1024,  # 10MB
    ):
        super().__init__(app)
        self.blocked_ips = blocked_ips or set()
        self.blocked_user_agents = blocked_user_agents or []
        self.blocked_paths = blocked_paths or []
        self.max_request_size = max_request_size
        
        # 編譯正則表達式
        self.blocked_user_agent_patterns = [re.compile(pattern) for pattern in self.blocked_user_agents]
        self.blocked_path_patterns = [re.compile(pattern) for pattern in self.blocked_paths]
    
    async def dispatch(self, request: Request, call_next):
        """處理請求"""
        # 檢查 IP 地址
        client_ip = request.client.host
        if self._is_ip_blocked(client_ip):
            logger.warning(f"阻止來自被封禁 IP 的請求: {client_ip}")
            return Response(content="拒絕訪問", status_code=403)
        
        # 檢查 User-Agent
        user_agent = request.headers.get("user-agent", "")
        if self._is_user_agent_blocked(user_agent):
            logger.warning(f"阻止來自被封禁 User-Agent 的請求: {user_agent}")
            return Response(content="拒絕訪問", status_code=403)
        
        # 檢查路徑
        path = request.url.path
        if self._is_path_blocked(path):
            logger.warning(f"阻止對被封禁路徑的請求: {path}")
            return Response(content="拒絕訪問", status_code=403)
        
        # 檢查請求大小
        content_length = request.headers.get("content-length", "0")
        if content_length.isdigit() and int(content_length) > self.max_request_size:
            logger.warning(f"阻止過大的請求: {content_length} bytes")
            return Response(content="請求體過大", status_code=413)
        
        # 記錄請求開始時間
        start_time = time.time()
        
        # 處理請求
        response = await call_next(request)
        
        # 計算處理時間
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
    
    def _is_ip_blocked(self, ip: str) -> bool:
        """檢查 IP 是否被封禁"""
        if not ip:
            return False
        
        # 檢查確切的 IP 地址
        if ip in self.blocked_ips:
            return True
        
        # 檢查 IP 範圍
        try:
            client_ip = ipaddress.ip_address(ip)
            for blocked_ip in self.blocked_ips:
                if "/" in blocked_ip:  # CIDR 表示法
                    if client_ip in ipaddress.ip_network(blocked_ip, strict=False):
                        return True
        except ValueError:
            pass
        
        return False
    
    def _is_user_agent_blocked(self, user_agent: str) -> bool:
        """檢查 User-Agent 是否被封禁"""
        if not user_agent:
            return False
        
        for pattern in self.blocked_user_agent_patterns:
            if pattern.search(user_agent):
                return True
        
        return False
    
    def _is_path_blocked(self, path: str) -> bool:
        """檢查路徑是否被封禁"""
        if not path:
            return False
        
        for pattern in self.blocked_path_patterns:
            if pattern.search(path):
                return True
        
        return False

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """請求日誌中間件"""
    
    async def dispatch(self, request: Request, call_next):
        """記錄請求和響應"""
        # 記錄請求
        logger.info(f"請求: {request.method} {request.url.path}")
        
        # 處理請求
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # 記錄響應
        logger.info(f"響應: {request.method} {request.url.path} - 狀態碼: {response.status_code}, 處理時間: {process_time:.4f}s")
        
        return response

def setup_middlewares(app: FastAPI):
    """設置中間件"""
    # 添加 CORS 中間件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 添加可信主機中間件
    if settings.ENVIRONMENT != "development":
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.ALLOWED_HOSTS,
        )
    
    # 添加 API 安全中間件
    app.add_middleware(
        APISecurityMiddleware,
        blocked_ips=settings.BLOCKED_IPS,
        blocked_user_agents=settings.BLOCKED_USER_AGENTS,
        blocked_paths=settings.BLOCKED_PATHS,
        max_request_size=settings.MAX_REQUEST_SIZE,
    )
    
    # 添加請求日誌中間件
    app.add_middleware(RequestLoggingMiddleware) 