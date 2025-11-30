"""
SocketIO 事件處理器 - 訊息相關
"""
from flask import request
from flask_login import current_user
from flask_socketio import emit, join_room, leave_room
from app.extensions import socketio
from app.services.message_service import MessageService


@socketio.on('connect')
def handle_connect():
    """處理 WebSocket 連接"""
    if current_user.is_authenticated:
        print(f'User {current_user.username} connected to WebSocket')
    else:
        print('Anonymous user connected to WebSocket')


@socketio.on('disconnect')
def handle_disconnect():
    """處理 WebSocket 斷開連接"""
    if current_user.is_authenticated:
        print(f'User {current_user.username} disconnected from WebSocket')


@socketio.on('join_conversation')
def handle_join_conversation(data):
    """加入對話房間"""
    if not current_user.is_authenticated:
        return
    
    other_user_id = data.get('other_user_id')
    if not other_user_id:
        return
    
    # 創建唯一的房間名稱（使用兩個用戶ID的較小值-較大值格式）
    user_ids = sorted([current_user.id, int(other_user_id)])
    room = f"chat_{user_ids[0]}_{user_ids[1]}"
    
    join_room(room)
    print(f'User {current_user.username} joined room: {room}')
    
    # 通知用戶已加入房間
    emit('joined_conversation', {'room': room})


@socketio.on('leave_conversation')
def handle_leave_conversation(data):
    """離開對話房間"""
    if not current_user.is_authenticated:
        return
    
    other_user_id = data.get('other_user_id')
    if not other_user_id:
        return
    
    user_ids = sorted([current_user.id, int(other_user_id)])
    room = f"chat_{user_ids[0]}_{user_ids[1]}"
    
    leave_room(room)
    print(f'User {current_user.username} left room: {room}')


@socketio.on('send_message')
def handle_send_message(data):
    """處理發送訊息"""
    if not current_user.is_authenticated:
        return
    
    receiver_id = data.get('receiver_id')
    content = data.get('content')
    
    if not receiver_id or not content:
        emit('error', {'message': '缺少必要參數'})
        return
    
    # 保存訊息到資料庫
    success, result = MessageService.send_message(
        sender_id=current_user.id,
        receiver_id=int(receiver_id),
        content=content.strip()
    )
    
    if not success:
        emit('error', {'message': result})
        return
    
    message = result
    
    # 創建房間名稱
    user_ids = sorted([current_user.id, int(receiver_id)])
    room = f"chat_{user_ids[0]}_{user_ids[1]}"
    
    # 準備訊息數據
    message_data = {
        'id': message.id,
        'sender_id': message.sender_id,
        'receiver_id': message.receiver_id,
        'content': message.content,
        'created_at': message.created_at.strftime('%H:%M'),
        'sender_username': current_user.username
    }
    
    # 發送訊息到房間（包括發送者和接收者）
    emit('new_message', message_data, room=room)
    
    # 更新未讀計數給接收者
    unread_count = MessageService.get_unread_count(int(receiver_id))
    emit('update_unread_count', {'count': unread_count}, room=f"user_{receiver_id}")


@socketio.on('mark_as_read')
def handle_mark_as_read(data):
    """標記訊息為已讀"""
    if not current_user.is_authenticated:
        return
    
    other_user_id = data.get('other_user_id')
    if not other_user_id:
        return
    
    # 標記與該用戶的所有訊息為已讀
    MessageService.mark_conversation_as_read(current_user.id, int(other_user_id))
    
    # 更新未讀計數
    unread_count = MessageService.get_unread_count(current_user.id)
    emit('update_unread_count', {'count': unread_count})


@socketio.on('join_user_room')
def handle_join_user_room():
    """用戶加入自己的專屬房間（用於接收未讀通知）"""
    if not current_user.is_authenticated:
        return
    
    room = f"user_{current_user.id}"
    join_room(room)
    print(f'User {current_user.username} joined personal room: {room}')
