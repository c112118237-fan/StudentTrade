from app.extensions import db
from datetime import datetime

class Transaction(db.Model):
    __tablename__ = 'transactions'

    # 交易狀態常數
    STATUS_PENDING = 'pending'          # 待賣家回應
    STATUS_ACCEPTED = 'accepted'        # 賣家已接受
    STATUS_IN_PROGRESS = 'in_progress'  # 交易進行中
    STATUS_COMPLETED = 'completed'      # 已完成
    STATUS_CANCELLED = 'cancelled'      # 已取消
    STATUS_REJECTED = 'rejected'        # 已拒絕
    STATUS_DISPUTED = 'disputed'        # 爭議中

    # 交易類型常數
    TYPE_SALE = 'sale'                  # 買賣
    TYPE_EXCHANGE = 'exchange'          # 交換
    TYPE_FREE = 'free'                  # 免費贈送

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), default=STATUS_PENDING)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

    # 關聯
    reviews = db.relationship('Review', backref='transaction', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def buyer(self):
        """取得買家資訊"""
        from app.models.user import User
        return User.query.get(self.buyer_id)

    @property
    def seller(self):
        """取得賣家資訊"""
        from app.models.user import User
        return User.query.get(self.seller_id)

    def can_accept(self):
        """是否可以接受交易"""
        return self.status == self.STATUS_PENDING

    def can_reject(self):
        """是否可以拒絕交易"""
        return self.status == self.STATUS_PENDING

    def can_start_progress(self):
        """是否可以開始進行交易"""
        return self.status == self.STATUS_ACCEPTED

    def can_complete(self):
        """是否可以完成交易"""
        return self.status == self.STATUS_IN_PROGRESS

    def can_cancel(self):
        """是否可以取消交易"""
        return self.status not in [self.STATUS_COMPLETED, self.STATUS_CANCELLED, self.STATUS_REJECTED]

    def can_dispute(self):
        """是否可以提出爭議"""
        return self.status in [self.STATUS_ACCEPTED, self.STATUS_IN_PROGRESS]

    def __repr__(self):
        return f'<Transaction {self.id} - {self.status}>'
