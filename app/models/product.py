from app.extensions import db
from datetime import datetime

class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    condition = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default='active')
    exchange_preference = db.Column(db.String(200))
    location = db.Column(db.String(200))
    transaction_method = db.Column(db.String(200))
    view_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 關聯
    images = db.relationship('ProductImage', backref='product', lazy='dynamic', cascade='all, delete-orphan')
    transactions = db.relationship('Transaction', backref='product', lazy='dynamic')
    messages = db.relationship('Message', backref='product', lazy='dynamic')

    @property
    def primary_image(self):
        """取得主要圖片"""
        img = self.images.filter_by(is_primary=True).first()
        return img.image_url if img else '/static/images/placeholders/product-placeholder.png'

    def increment_view_count(self):
        """增加瀏覽次數"""
        self.view_count += 1
        db.session.commit()

    def __repr__(self):
        return f'<Product {self.title}>'
