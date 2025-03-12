from typing import Dict, List, Set
import json
from fastapi import WebSocket, WebSocketDisconnect
from loguru import logger

class ConnectionManager:
    """WebSocket 連接管理器"""
    
    def __init__(self):
        # 所有活躍連接
        self.active_connections: List[WebSocket] = []
        # 用戶 ID 到 WebSocket 連接的映射
        self.user_connections: Dict[str, List[WebSocket]] = {}
        # 聊天室 ID 到 WebSocket 連接的映射
        self.room_connections: Dict[str, List[WebSocket]] = {}
        # 用戶 ID 到聊天室 ID 的映射
        self.user_rooms: Dict[str, Set[str]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str = None, room_id: str = None):
        """建立新的 WebSocket 連接"""
        await websocket.accept()
        self.active_connections.append(websocket)
        
        # 如果提供了用戶 ID，則將連接添加到用戶連接映射中
        if user_id:
            if user_id not in self.user_connections:
                self.user_connections[user_id] = []
            self.user_connections[user_id].append(websocket)
        
        # 如果提供了聊天室 ID，則將連接添加到聊天室連接映射中
        if room_id:
            if room_id not in self.room_connections:
                self.room_connections[room_id] = []
            self.room_connections[room_id].append(websocket)
            
            # 更新用戶-聊天室映射
            if user_id:
                if user_id not in self.user_rooms:
                    self.user_rooms[user_id] = set()
                self.user_rooms[user_id].add(room_id)
        
        logger.info(f"WebSocket 連接已建立: 用戶={user_id}, 聊天室={room_id}")
    
    async def disconnect(self, websocket: WebSocket, user_id: str = None, room_id: str = None):
        """關閉 WebSocket 連接"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        # 從用戶連接映射中移除
        if user_id and user_id in self.user_connections:
            if websocket in self.user_connections[user_id]:
                self.user_connections[user_id].remove(websocket)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
        
        # 從聊天室連接映射中移除
        if room_id and room_id in self.room_connections:
            if websocket in self.room_connections[room_id]:
                self.room_connections[room_id].remove(websocket)
            if not self.room_connections[room_id]:
                del self.room_connections[room_id]
                
                # 更新用戶-聊天室映射
                if user_id and user_id in self.user_rooms and room_id in self.user_rooms[user_id]:
                    self.user_rooms[user_id].remove(room_id)
                    if not self.user_rooms[user_id]:
                        del self.user_rooms[user_id]
        
        logger.info(f"WebSocket 連接已關閉: 用戶={user_id}, 聊天室={room_id}")
    
    async def send_personal_message(self, message: dict, user_id: str):
        """向特定用戶發送消息"""
        if user_id in self.user_connections:
            for connection in self.user_connections[user_id]:
                await connection.send_text(json.dumps(message))
            logger.info(f"已向用戶 {user_id} 發送個人消息")
            return True
        logger.warning(f"用戶 {user_id} 不在線，無法發送消息")
        return False
    
    async def broadcast_to_room(self, message: dict, room_id: str):
        """向聊天室中的所有用戶廣播消息"""
        if room_id in self.room_connections:
            for connection in self.room_connections[room_id]:
                await connection.send_text(json.dumps(message))
            logger.info(f"已向聊天室 {room_id} 廣播消息")
            return True
        logger.warning(f"聊天室 {room_id} 不存在或沒有活躍連接")
        return False
    
    async def broadcast(self, message: dict):
        """向所有連接的客戶端廣播消息"""
        for connection in self.active_connections:
            await connection.send_text(json.dumps(message))
        logger.info("已向所有連接的客戶端廣播消息")
    
    def get_user_rooms(self, user_id: str) -> Set[str]:
        """獲取用戶加入的所有聊天室"""
        return self.user_rooms.get(user_id, set())
    
    def get_room_users(self, room_id: str) -> Set[str]:
        """獲取聊天室中的所有用戶"""
        users = set()
        for user_id, rooms in self.user_rooms.items():
            if room_id in rooms:
                users.add(user_id)
        return users

# 創建全局連接管理器實例
manager = ConnectionManager() 