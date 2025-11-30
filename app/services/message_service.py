from app.extensions import db
from app.models.message import Message
from app.models.notification import Notification
from app.models.user import User
from sqlalchemy import or_, and_
from datetime import datetime

class MessageService:
    """訊息服務類別"""

    @staticmethod
    def send_message(sender_id, receiver_id, content, product_id=None):
        """發送訊息

        Args:
            sender_id: 發送者 ID
            receiver_id: 接收者 ID
            content: 訊息內容
            product_id: 相關商品 ID（選填）

        Returns:
            (success: bool, message: Message or error_message: str)
        """
        try:
            # 驗證接收者存在
            receiver = User.query.get(receiver_id)
            if not receiver:
                return False, '接收者不存在'

            # 驗證不能發送給自己
            if sender_id == receiver_id:
                return False, '無法發送訊息給自己'

            # 驗證內容不為空
            if not content or not content.strip():
                return False, '訊息內容不能為空'

            # 建立訊息
            message = Message(
                sender_id=sender_id,
                receiver_id=receiver_id,
                content=content.strip(),
                product_id=product_id
            )

            db.session.add(message)
            db.session.commit()

            # 建立通知給接收者
            MessageService._create_notification(
                user_id=receiver_id,
                type='new_message',
                content=f'您收到來自 {message.sender.username} 的新訊息',
                link=f'/messages/{sender_id}'
            )

            return True, message

        except Exception as e:
            db.session.rollback()
            return False, f'發送訊息失敗：{str(e)}'

    @staticmethod
    def get_conversation(user_id, other_user_id, page=1, per_page=50):
        """取得兩個使用者之間的對話

        Args:
            user_id: 當前使用者 ID
            other_user_id: 對話對象 ID
            page: 頁數
            per_page: 每頁數量

        Returns:
            Pagination 物件
        """
        query = Message.query.filter(
            or_(
                and_(Message.sender_id == user_id, Message.receiver_id == other_user_id),
                and_(Message.sender_id == other_user_id, Message.receiver_id == user_id)
            )
        ).order_by(Message.created_at.asc())

        return query.paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def get_conversations_list(user_id):
        """取得使用者的對話列表（每個對話顯示最後一則訊息）

        Args:
            user_id: 使用者 ID

        Returns:
            list: 對話列表（包含對象資訊和最後一則訊息）
        """
        # 找出所有與該使用者有對話的其他使用者
        sent_to = db.session.query(Message.receiver_id).filter_by(sender_id=user_id).distinct()
        received_from = db.session.query(Message.sender_id).filter_by(receiver_id=user_id).distinct()

        # 合併並去重
        other_user_ids = set()
        for row in sent_to:
            other_user_ids.add(row[0])
        for row in received_from:
            other_user_ids.add(row[0])

        # 建立對話列表
        conversations = []
        for other_user_id in other_user_ids:
            # 取得與該使用者的最後一則訊息
            last_message = Message.query.filter(
                or_(
                    and_(Message.sender_id == user_id, Message.receiver_id == other_user_id),
                    and_(Message.sender_id == other_user_id, Message.receiver_id == user_id)
                )
            ).order_by(Message.created_at.desc()).first()

            # 取得未讀訊息數量
            unread_count = Message.query.filter_by(
                sender_id=other_user_id,
                receiver_id=user_id,
                is_read=False
            ).count()

            # 取得對話對象資訊
            other_user = User.query.get(other_user_id)

            conversations.append({
                'user': other_user,
                'last_message': last_message,
                'unread_count': unread_count
            })

        # 按最後訊息時間排序
        conversations.sort(key=lambda x: x['last_message'].created_at, reverse=True)

        return conversations

    @staticmethod
    def mark_as_read(message_id, user_id):
        """標記訊息為已讀

        Args:
            message_id: 訊息 ID
            user_id: 使用者 ID（必須是接收者）

        Returns:
            (success: bool, message: str)
        """
        try:
            message = Message.query.get(message_id)

            if not message:
                return False, '訊息不存在'

            # 驗證權限（只有接收者可以標記為已讀）
            if message.receiver_id != user_id:
                return False, '您沒有權限操作此訊息'

            # 標記為已讀
            message.is_read = True
            db.session.commit()

            return True, '已標記為已讀'

        except Exception as e:
            db.session.rollback()
            return False, f'標記失敗：{str(e)}'

    @staticmethod
    def mark_conversation_as_read(user_id, other_user_id):
        """標記與某個使用者的所有訊息為已讀

        Args:
            user_id: 當前使用者 ID
            other_user_id: 對話對象 ID

        Returns:
            (success: bool, count: int or error_message: str)
        """
        try:
            # 找出所有未讀的訊息
            messages = Message.query.filter_by(
                sender_id=other_user_id,
                receiver_id=user_id,
                is_read=False
            ).all()

            # 標記為已讀
            count = 0
            for message in messages:
                message.is_read = True
                count += 1

            db.session.commit()

            return True, count

        except Exception as e:
            db.session.rollback()
            return False, f'標記失敗：{str(e)}'

    @staticmethod
    def get_unread_count(user_id):
        """取得未讀訊息總數

        Args:
            user_id: 使用者 ID

        Returns:
            int: 未讀訊息數量
        """
        return Message.query.filter_by(
            receiver_id=user_id,
            is_read=False
        ).count()

    @staticmethod
    def delete_message(message_id, user_id):
        """刪除訊息（只有發送者可以刪除）

        Args:
            message_id: 訊息 ID
            user_id: 使用者 ID（必須是發送者）

        Returns:
            (success: bool, message: str)
        """
        try:
            message = Message.query.get(message_id)

            if not message:
                return False, '訊息不存在'

            # 驗證權限（只有發送者可以刪除）
            if message.sender_id != user_id:
                return False, '您沒有權限刪除此訊息'

            db.session.delete(message)
            db.session.commit()

            return True, '訊息已刪除'

        except Exception as e:
            db.session.rollback()
            return False, f'刪除失敗：{str(e)}'

    @staticmethod
    def _create_notification(user_id, type, content, link):
        """建立通知（內部方法）

        Args:
            user_id: 使用者 ID
            type: 通知類型
            content: 通知內容
            link: 連結
        """
        try:
            notification = Notification(
                user_id=user_id,
                type=type,
                content=content,
                link=link
            )
            db.session.add(notification)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
