from app.extensions import db, socketio
from app.models.notification import Notification
from app.models.review import Review
from app.models.transaction import Transaction
from app.models.user import User

class NotificationService:
    """通知服務類別"""

    @staticmethod
    def create_notification(user_id, type, content, link=None):
        """建立通知

        Args:
            user_id: 使用者 ID
            type: 通知類型
            content: 通知內容
            link: 連結（選填）

        Returns:
            (success: bool, notification: Notification or error_message: str)
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

            try:
                unread_count = NotificationService.get_unread_count(user_id)
                socketio.emit(
                    'update_notification_count',
                    {'count': unread_count},
                    room=f'user_{user_id}'
                )
                socketio.emit(
                    'new_notification',
                    {
                        'type': type,
                        'content': content,
                        'link': link,
                        'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M')
                    },
                    room=f'user_{user_id}'
                )
            except Exception:
                pass

            return True, notification

        except Exception as e:
            db.session.rollback()
            return False, f'建立通知失敗：{str(e)}'

    @staticmethod
    def get_user_notifications(user_id, unread_only=False, page=1, per_page=20):
        """取得使用者的通知列表

        Args:
            user_id: 使用者 ID
            unread_only: 是否只顯示未讀通知
            page: 頁數
            per_page: 每頁數量

        Returns:
            Pagination 物件
        """
        query = Notification.query.filter_by(user_id=user_id)

        if unread_only:
            query = query.filter_by(is_read=False)

        query = query.order_by(Notification.created_at.desc())

        return query.paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def mark_as_read(notification_id, user_id):
        """標記通知為已讀

        Args:
            notification_id: 通知 ID
            user_id: 使用者 ID（驗證權限）

        Returns:
            (success: bool, message: str)
        """
        try:
            notification = Notification.query.get(notification_id)

            if not notification:
                return False, '通知不存在'

            # 驗證權限
            if notification.user_id != user_id:
                return False, '您沒有權限操作此通知'

            notification.is_read = True
            db.session.commit()

            return True, '已標記為已讀'

        except Exception as e:
            db.session.rollback()
            return False, f'標記失敗：{str(e)}'

    @staticmethod
    def mark_all_as_read(user_id):
        """標記所有通知為已讀

        Args:
            user_id: 使用者 ID

        Returns:
            (success: bool, count: int or error_message: str)
        """
        try:
            notifications = Notification.query.filter_by(
                user_id=user_id,
                is_read=False
            ).all()

            count = 0
            for notification in notifications:
                notification.is_read = True
                count += 1

            db.session.commit()

            return True, count

        except Exception as e:
            db.session.rollback()
            return False, f'標記失敗：{str(e)}'

    @staticmethod
    def get_unread_count(user_id):
        """取得未讀通知數量

        Args:
            user_id: 使用者 ID

        Returns:
            int: 未讀通知數量
        """
        return Notification.query.filter_by(
            user_id=user_id,
            is_read=False
        ).count()

    @staticmethod
    def delete_notification(notification_id, user_id):
        """刪除通知

        Args:
            notification_id: 通知 ID
            user_id: 使用者 ID（驗證權限）

        Returns:
            (success: bool, message: str)
        """
        try:
            notification = Notification.query.get(notification_id)

            if not notification:
                return False, '通知不存在'

            # 驗證權限
            if notification.user_id != user_id:
                return False, '您沒有權限刪除此通知'

            db.session.delete(notification)
            db.session.commit()

            return True, '通知已刪除'

        except Exception as e:
            db.session.rollback()
            return False, f'刪除失敗：{str(e)}'


class ReviewService:
    """評價服務類別"""

    @staticmethod
    def create_review(transaction_id, reviewer_id, rating, comment=None):
        """建立評價

        Args:
            transaction_id: 交易 ID
            reviewer_id: 評價者 ID
            rating: 評分（1-5 星）
            comment: 評論內容（選填）

        Returns:
            (success: bool, review: Review or error_message: str)
        """
        try:
            # 取得交易
            transaction = Transaction.query.get(transaction_id)

            if not transaction:
                return False, '交易不存在'

            # 驗證交易已完成
            if transaction.status != 'completed':
                return False, '只能對已完成的交易進行評價'

            # 僅允許買家評價賣家
            if reviewer_id != transaction.buyer_id:
                return False, '只有買家可以評價賣家'

            reviewee_id = transaction.seller_id

            # 檢查是否已經評價過
            existing_review = Review.query.filter_by(
                transaction_id=transaction_id,
                reviewer_id=reviewer_id
            ).first()

            if existing_review:
                return False, '您已經評價過此交易'

            # 驗證評分
            if not (1 <= rating <= 5):
                return False, '評分必須在 1-5 星之間'

            # 建立評價
            review = Review(
                transaction_id=transaction_id,
                reviewer_id=reviewer_id,
                reviewee_id=reviewee_id,
                rating=rating,
                comment=comment.strip() if comment else None
            )

            db.session.add(review)
            db.session.commit()

            # 建立通知給被評價者
            reviewee = User.query.get(reviewee_id)
            NotificationService.create_notification(
                user_id=reviewee_id,
                type='new_review',
                content=f'您收到來自 {transaction.product.title} 的新評價（{rating} 星）',
                link=f'/reviews/users/{reviewee_id}'
            )

            return True, review

        except Exception as e:
            db.session.rollback()
            return False, f'建立評價失敗：{str(e)}'

    @staticmethod
    def get_user_reviews(user_id, page=1, per_page=12):
        """取得使用者收到的評價列表

        Args:
            user_id: 使用者 ID（被評價者）
            page: 頁數
            per_page: 每頁數量

        Returns:
            Pagination 物件
        """
        query = Review.query.filter_by(reviewee_id=user_id)
        query = query.order_by(Review.created_at.desc())

        return query.paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def get_transaction_reviews(transaction_id):
        """取得交易的所有評價

        Args:
            transaction_id: 交易 ID

        Returns:
            list: 評價列表
        """
        return Review.query.filter_by(transaction_id=transaction_id).all()

    @staticmethod
    def can_review(transaction_id, user_id):
        """檢查使用者是否可以評價此交易

        Args:
            transaction_id: 交易 ID
            user_id: 使用者 ID

        Returns:
            (can_review: bool, message: str)
        """
        transaction = Transaction.query.get(transaction_id)

        if not transaction:
            return False, '交易不存在'

        # 檢查交易狀態
        if transaction.status != 'completed':
            return False, '只能對已完成的交易進行評價'

        # 檢查是否為買家
        if user_id != transaction.buyer_id:
            return False, '只有買家可以評價賣家'

        # 檢查是否已評價
        existing_review = Review.query.filter_by(
            transaction_id=transaction_id,
            reviewer_id=user_id
        ).first()

        if existing_review:
            return False, '您已經評價過此交易'

        return True, '可以評價'

    @staticmethod
    def get_user_stats(user_id):
        """取得使用者的評價統計

        Args:
            user_id: 使用者 ID

        Returns:
            dict: 評價統計資料
        """
        reviews = Review.query.filter_by(reviewee_id=user_id).all()

        if not reviews:
            return {
                'total_reviews': 0,
                'average_rating': 0,
                'rating_distribution': {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
            }

        total_reviews = len(reviews)
        total_rating = sum(r.rating for r in reviews)
        average_rating = total_rating / total_reviews

        # 評分分布
        rating_distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for review in reviews:
            rating_distribution[review.rating] += 1

        return {
            'total_reviews': total_reviews,
            'average_rating': round(average_rating, 1),
            'rating_distribution': rating_distribution
        }
