import json
from typing import Optional
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, Query, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from api.api_v1.endpoints.websocket.connection import manager
from core.db.session import get_db
from core.security import get_current_user, get_token_from_query
from models.user import User

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """通用 WebSocket 端點"""
    # 嘗試驗證用戶
    user = None
    user_id = None
    
    if token:
        try:
            user = await get_current_user(token=token, db=db)
            user_id = str(user.id)
        except HTTPException:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
    
    # 接受連接
    await manager.connect(websocket, user_id=user_id)
    
    try:
        while True:
            # 接收消息
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                
                # 處理不同類型的消息
                message_type = message.get("type")
                
                if message_type == "ping":
                    # 心跳檢測
                    await websocket.send_text(json.dumps({"type": "pong"}))
                
                elif message_type == "broadcast":
                    # 廣播消息（僅限已認證用戶）
                    if not user:
                        await websocket.send_text(json.dumps({
                            "type": "error",
                            "message": "未授權的操作"
                        }))
                        continue
                    
                    await manager.broadcast({
                        "type": "message",
                        "sender": user_id,
                        "content": message.get("content", ""),
                        "timestamp": message.get("timestamp")
                    })
                
                else:
                    # 未知消息類型
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": "未知的消息類型"
                    }))
            
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "無效的 JSON 格式"
                }))
    
    except WebSocketDisconnect:
        # 處理連接斷開
        await manager.disconnect(websocket, user_id=user_id)

@router.websocket("/ws/chat/{room_id}")
async def chat_websocket_endpoint(
    websocket: WebSocket,
    room_id: str,
    token: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """聊天室 WebSocket 端點"""
    # 嘗試驗證用戶
    user = None
    user_id = None
    
    if token:
        try:
            user = await get_current_user(token=token, db=db)
            user_id = str(user.id)
        except HTTPException:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
    else:
        # 聊天室需要認證
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    
    # 接受連接
    await manager.connect(websocket, user_id=user_id, room_id=room_id)
    
    # 通知聊天室其他用戶有新用戶加入
    await manager.broadcast_to_room({
        "type": "system",
        "action": "join",
        "user_id": user_id,
        "room_id": room_id,
        "timestamp": str(datetime.now())
    }, room_id)
    
    try:
        while True:
            # 接收消息
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                
                # 處理不同類型的消息
                message_type = message.get("type")
                
                if message_type == "chat":
                    # 聊天消息
                    await manager.broadcast_to_room({
                        "type": "chat",
                        "sender": user_id,
                        "content": message.get("content", ""),
                        "room_id": room_id,
                        "timestamp": message.get("timestamp")
                    }, room_id)
                
                elif message_type == "typing":
                    # 正在輸入
                    await manager.broadcast_to_room({
                        "type": "typing",
                        "user_id": user_id,
                        "room_id": room_id
                    }, room_id)
                
                else:
                    # 未知消息類型
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": "未知的消息類型"
                    }))
            
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "無效的 JSON 格式"
                }))
    
    except WebSocketDisconnect:
        # 處理連接斷開
        await manager.disconnect(websocket, user_id=user_id, room_id=room_id)
        
        # 通知聊天室其他用戶有用戶離開
        await manager.broadcast_to_room({
            "type": "system",
            "action": "leave",
            "user_id": user_id,
            "room_id": room_id,
            "timestamp": str(datetime.now())
        }, room_id)

@router.get("/chat/rooms", tags=["聊天"])
async def get_available_rooms(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """獲取用戶可用的聊天室"""
    user_id = str(current_user.id)
    rooms = manager.get_user_rooms(user_id)
    return {"rooms": list(rooms)}

@router.get("/chat/rooms/{room_id}/users", tags=["聊天"])
async def get_room_users(
    room_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """獲取聊天室中的用戶"""
    users = manager.get_room_users(room_id)
    return {"users": list(users)} 