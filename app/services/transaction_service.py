from app.extensions import db
from app.models.transaction import Transaction
from app.models.product import Product
from app.models.notification import Notification
from datetime import datetime

class TransactionService:
    """交易服務類別"""

    @staticmethod
    def create_transaction(product_id, buyer_id, transaction_type, amount, notes=None):
        """建立交易請求

        Args:
            product_id: 商品 ID
            buyer_id: 買家 ID
            transaction_type: 交易類型（sale, exchange, free）
            amount: 交易金額
            notes: 備註

        Returns:
            (success: bool, transaction: Transaction or error_message: str)
        """
        try:
            # 取得商品
            product = Product.query.get(product_id)

            if not product:
                return False, '商品不存在'

            # 檢查商品狀態
            if product.status != 'active':
                return False, '此商品目前無法交易'

            # 檢查買家不能是賣家
            if product.user_id == buyer_id:
                return False, '無法購買自己的商品'

            # 檢查是否已有進行中的交易
            existing_transaction = Transaction.query.filter_by(
                product_id=product_id,
                status='pending'
            ).first()

            if existing_transaction:
                return False, '此商品已有進行中的交易'

            # 建立交易
            transaction = Transaction(
                product_id=product_id,
                buyer_id=buyer_id,
                seller_id=product.user_id,
                transaction_type=transaction_type,
                amount=amount,
                status='pending',
                notes=notes
            )

            # 更新商品狀態
            product.status = 'pending'

            db.session.add(transaction)
            db.session.commit()

            # 建立通知給賣家
            TransactionService._create_notification(
                user_id=product.user_id,
                type='transaction_request',
                content=f'您的商品「{product.title}」收到新的交易請求',
                link=f'/transactions/{transaction.id}'
            )

            return True, transaction

        except Exception as e:
            db.session.rollback()
            return False, f'建立交易失敗：{str(e)}'

    @staticmethod
    def accept_transaction(transaction_id, seller_id):
        """接受交易請求

        Args:
            transaction_id: 交易 ID
            seller_id: 賣家 ID（驗證權限）

        Returns:
            (success: bool, transaction: Transaction or error_message: str)
        """
        try:
            transaction = Transaction.query.get(transaction_id)

            if not transaction:
                return False, '交易不存在'

            # 驗證權限
            if transaction.seller_id != seller_id:
                return False, '您沒有權限操作此交易'

            # 檢查交易狀態
            if not transaction.can_accept():
                return False, '此交易無法接受'

            # 更新交易狀態為已接受
            transaction.status = Transaction.STATUS_ACCEPTED

            db.session.commit()

            # 建立通知給買家
            TransactionService._create_notification(
                user_id=transaction.buyer_id,
                type='transaction_accepted',
                content=f'您的交易請求「{transaction.product.title}」已被賣家接受',
                link=f'/transactions/{transaction.id}'
            )

            return True, transaction

        except Exception as e:
            db.session.rollback()
            return False, f'接受交易失敗：{str(e)}'

    @staticmethod
    def reject_transaction(transaction_id, seller_id, reason=None):
        """拒絕交易請求

        Args:
            transaction_id: 交易 ID
            seller_id: 賣家 ID（驗證權限）
            reason: 拒絕原因

        Returns:
            (success: bool, message: str)
        """
        try:
            transaction = Transaction.query.get(transaction_id)

            if not transaction:
                return False, '交易不存在'

            # 驗證權限
            if transaction.seller_id != seller_id:
                return False, '您沒有權限操作此交易'

            # 檢查交易狀態
            if not transaction.can_reject():
                return False, '此交易無法拒絕'

            # 更新交易狀態
            transaction.status = Transaction.STATUS_REJECTED
            if reason:
                transaction.notes = f"拒絕原因：{reason}"

            # 恢復商品狀態
            transaction.product.status = 'active'

            db.session.commit()

            # 建立通知給買家
            TransactionService._create_notification(
                user_id=transaction.buyer_id,
                type='transaction_rejected',
                content=f'您的交易請求「{transaction.product.title}」已被賣家拒絕',
                link=f'/transactions/{transaction.id}'
            )

            return True, '交易已拒絕'

        except Exception as e:
            db.session.rollback()
            return False, f'拒絕交易失敗：{str(e)}'

    @staticmethod
    def complete_transaction(transaction_id, user_id):
        """完成交易

        Args:
            transaction_id: 交易 ID
            user_id: 操作者 ID（買家或賣家）

        Returns:
            (success: bool, message: str)
        """
        try:
            transaction = Transaction.query.get(transaction_id)

            if not transaction:
                return False, '交易不存在'

            # 驗證權限（買家或賣家都可以完成交易）
            if transaction.buyer_id != user_id and transaction.seller_id != user_id:
                return False, '您沒有權限操作此交易'

            # 檢查交易狀態
            if not transaction.can_complete():
                return False, '此交易無法完成'

            # 更新交易狀態
            transaction.status = Transaction.STATUS_COMPLETED
            transaction.completed_at = datetime.utcnow()

            # 更新商品狀態為已售出
            transaction.product.status = 'sold'

            db.session.commit()

            # 建立通知給對方
            other_user_id = transaction.seller_id if user_id == transaction.buyer_id else transaction.buyer_id
            TransactionService._create_notification(
                user_id=other_user_id,
                type='transaction_completed',
                content=f'交易「{transaction.product.title}」已完成',
                link=f'/transactions/{transaction.id}'
            )

            return True, '交易已完成'

        except Exception as e:
            db.session.rollback()
            return False, f'完成交易失敗：{str(e)}'

    @staticmethod
    def cancel_transaction(transaction_id, user_id, reason=None):
        """取消交易

        Args:
            transaction_id: 交易 ID
            user_id: 操作者 ID（買家或賣家）
            reason: 取消原因

        Returns:
            (success: bool, message: str)
        """
        try:
            transaction = Transaction.query.get(transaction_id)

            if not transaction:
                return False, '交易不存在'

            # 驗證權限
            if transaction.buyer_id != user_id and transaction.seller_id != user_id:
                return False, '您沒有權限操作此交易'

            # 檢查交易狀態
            if not transaction.can_cancel():
                return False, '此交易無法取消'

            # 更新交易狀態
            transaction.status = Transaction.STATUS_CANCELLED
            if reason:
                current_notes = transaction.notes or ''
                transaction.notes = f"{current_notes}\n取消原因：{reason}" if current_notes else f"取消原因：{reason}"

            # 恢復商品狀態
            transaction.product.status = 'active'

            db.session.commit()

            # 建立通知給對方
            other_user_id = transaction.seller_id if user_id == transaction.buyer_id else transaction.buyer_id
            TransactionService._create_notification(
                user_id=other_user_id,
                type='transaction_cancelled',
                content=f'交易「{transaction.product.title}」已被取消',
                link=f'/transactions/{transaction.id}'
            )

            return True, '交易已取消'

        except Exception as e:
            db.session.rollback()
            return False, f'取消交易失敗：{str(e)}'

    @staticmethod
    def get_transaction_by_id(transaction_id):
        """取得交易詳情

        Args:
            transaction_id: 交易 ID

        Returns:
            Transaction 或 None
        """
        return Transaction.query.get(transaction_id)

    @staticmethod
    def get_user_transactions(user_id, role='all', status=None, page=1, per_page=12):
        """取得使用者的交易列表

        Args:
            user_id: 使用者 ID
            role: 角色（all, buyer, seller）
            status: 交易狀態
            page: 頁數
            per_page: 每頁數量

        Returns:
            Pagination 物件
        """
        query = Transaction.query

        # 篩選買家或賣家
        if role == 'buyer':
            query = query.filter_by(buyer_id=user_id)
        elif role == 'seller':
            query = query.filter_by(seller_id=user_id)
        else:  # all
            query = query.filter(
                (Transaction.buyer_id == user_id) | (Transaction.seller_id == user_id)
            )

        # 篩選狀態
        if status:
            query = query.filter_by(status=status)

        # 排序（最新的在前）
        query = query.order_by(Transaction.created_at.desc())

        return query.paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def start_progress(transaction_id, user_id):
        """開始進行交易

        Args:
            transaction_id: 交易 ID
            user_id: 操作者 ID（買家或賣家）

        Returns:
            (success: bool, message: str)
        """
        try:
            transaction = Transaction.query.get(transaction_id)

            if not transaction:
                return False, '交易不存在'

            # 驗證權限
            if transaction.buyer_id != user_id and transaction.seller_id != user_id:
                return False, '您沒有權限操作此交易'

            # 檢查交易狀態
            if not transaction.can_start_progress():
                return False, '此交易無法開始進行'

            # 更新交易狀態
            transaction.status = Transaction.STATUS_IN_PROGRESS

            db.session.commit()

            # 建立通知給對方
            other_user_id = transaction.seller_id if user_id == transaction.buyer_id else transaction.buyer_id
            TransactionService._create_notification(
                user_id=other_user_id,
                type='transaction_in_progress',
                content=f'交易「{transaction.product.title}」已開始進行',
                link=f'/transactions/{transaction.id}'
            )

            return True, '交易已開始進行'

        except Exception as e:
            db.session.rollback()
            return False, f'開始交易失敗：{str(e)}'

    @staticmethod
    def create_dispute(transaction_id, user_id, reason):
        """提出交易爭議

        Args:
            transaction_id: 交易 ID
            user_id: 操作者 ID（買家或賣家）
            reason: 爭議原因

        Returns:
            (success: bool, message: str)
        """
        try:
            transaction = Transaction.query.get(transaction_id)

            if not transaction:
                return False, '交易不存在'

            # 驗證權限
            if transaction.buyer_id != user_id and transaction.seller_id != user_id:
                return False, '您沒有權限操作此交易'

            # 檢查交易狀態
            if not transaction.can_dispute():
                return False, '此交易無法提出爭議'

            # 更新交易狀態
            transaction.status = Transaction.STATUS_DISPUTED
            current_notes = transaction.notes or ''
            transaction.notes = f"{current_notes}\n爭議原因：{reason}" if current_notes else f"爭議原因：{reason}"

            db.session.commit()

            # 建立通知給對方
            other_user_id = transaction.seller_id if user_id == transaction.buyer_id else transaction.buyer_id
            TransactionService._create_notification(
                user_id=other_user_id,
                type='transaction_disputed',
                content=f'交易「{transaction.product.title}」有爭議待處理',
                link=f'/transactions/{transaction.id}'
            )

            return True, '爭議已提交，將由管理員處理'

        except Exception as e:
            db.session.rollback()
            return False, f'提交爭議失敗：{str(e)}'

    @staticmethod
    def resolve_dispute(transaction_id, admin_id, resolution, action='cancel'):
        """解決交易爭議（管理員功能）

        Args:
            transaction_id: 交易 ID
            admin_id: 管理員 ID
            resolution: 解決方案說明
            action: 處理動作 (cancel, complete, refund)

        Returns:
            (success: bool, message: str)
        """
        try:
            transaction = Transaction.query.get(transaction_id)

            if not transaction:
                return False, '交易不存在'

            # 檢查交易狀態
            if transaction.status != Transaction.STATUS_DISPUTED:
                return False, '此交易不在爭議狀態'

            # 根據處理動作更新狀態
            if action == 'cancel':
                transaction.status = Transaction.STATUS_CANCELLED
                transaction.product.status = 'active'
            elif action == 'complete':
                transaction.status = Transaction.STATUS_COMPLETED
                transaction.completed_at = datetime.utcnow()
                transaction.product.status = 'sold'

            # 記錄解決方案
            current_notes = transaction.notes or ''
            transaction.notes = f"{current_notes}\n管理員處理：{resolution}"

            db.session.commit()

            # 通知雙方
            TransactionService._create_notification(
                user_id=transaction.buyer_id,
                type='dispute_resolved',
                content=f'交易「{transaction.product.title}」的爭議已處理',
                link=f'/transactions/{transaction.id}'
            )
            TransactionService._create_notification(
                user_id=transaction.seller_id,
                type='dispute_resolved',
                content=f'交易「{transaction.product.title}」的爭議已處理',
                link=f'/transactions/{transaction.id}'
            )

            return True, '爭議已處理完成'

        except Exception as e:
            db.session.rollback()
            return False, f'處理爭議失敗：{str(e)}'

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
