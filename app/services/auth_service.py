from app.extensions import db
from app.models.user import User
from sqlalchemy import func, or_
from app.utils.validators import (
    validate_student_email,
    validate_password_strength,
    validate_username,
    validate_student_id,
    validate_phone
)
from datetime import datetime

class AuthService:
    """認證服務類別"""

    @staticmethod
    def register_user(email, password, username, student_id=None, phone=None, department=None):
        """註冊新使用者

        Args:
            email: 學校信箱
            password: 密碼
            username: 使用者名稱
            student_id: 學號（選填）
            phone: 手機號碼（選填）
            department: 科系（選填）

        Returns:
            (success: bool, user: User or error_message: str)
        """
        # 驗證 email
        is_valid, error = validate_student_email(email)
        if not is_valid:
            return False, error

        # 檢查 email 是否已註冊
        if User.query.filter_by(email=email).first():
            return False, '此信箱已被註冊'

        # 驗證密碼強度
        is_valid, error = validate_password_strength(password)
        if not is_valid:
            return False, error

        # 驗證使用者名稱
        is_valid, error = validate_username(username)
        if not is_valid:
            return False, error

        # 驗證學號
        is_valid, error = validate_student_id(student_id)
        if not is_valid:
            return False, error

        # 驗證手機號碼
        is_valid, error = validate_phone(phone)
        if not is_valid:
            return False, error

        try:
            # 建立新使用者
            user = User(
                email=email,
                username=username,
                student_id=student_id,
                phone=phone,
                department=department
            )
            user.set_password(password)

            db.session.add(user)
            db.session.commit()

            return True, user
        except Exception as e:
            db.session.rollback()
            return False, f'註冊失敗：{str(e)}'

    @staticmethod
    def login_user(identifier, password):
        """使用者登入，支援 email 或使用者名稱

        Args:
            identifier: 信箱或使用者名稱
            password: 密碼

        Returns:
            (success: bool, user: User or error_message: str)
        """
        identifier_lower = identifier.lower()

        # 查詢使用者（忽略大小寫）
        user = User.query.filter(
            or_(
                func.lower(User.email) == identifier_lower,
                func.lower(User.username) == identifier_lower
            )
        ).first()

        if not user:
            return False, '信箱或密碼錯誤'

        # 驗證密碼
        if not user.check_password(password):
            return False, '信箱或密碼錯誤'

        # 更新最後登入時間
        user.last_login = datetime.utcnow()
        db.session.commit()

        return True, user

    @staticmethod
    def update_profile(user, username=None, student_id=None, phone=None,
                      department=None, bio=None, avatar_url=None):
        """更新使用者資料

        Args:
            user: User 物件
            username: 使用者名稱
            student_id: 學號
            phone: 手機號碼
            department: 科系
            bio: 個人簡介
            avatar_url: 頭像 URL

        Returns:
            (success: bool, user: User or error_message: str)
        """
        try:
            # 驗證使用者名稱
            if username is not None:
                is_valid, error = validate_username(username)
                if not is_valid:
                    return False, error
                user.username = username

            # 驗證學號
            if student_id is not None:
                is_valid, error = validate_student_id(student_id)
                if not is_valid:
                    return False, error
                user.student_id = student_id

            # 驗證手機號碼
            if phone is not None:
                is_valid, error = validate_phone(phone)
                if not is_valid:
                    return False, error
                user.phone = phone

            # 更新其他欄位
            if department is not None:
                user.department = department

            if bio is not None:
                user.bio = bio

            if avatar_url is not None:
                user.avatar_url = avatar_url

            db.session.commit()
            return True, user

        except Exception as e:
            db.session.rollback()
            return False, f'更新失敗：{str(e)}'

    @staticmethod
    def change_password(user, old_password, new_password):
        """變更密碼

        Args:
            user: User 物件
            old_password: 舊密碼
            new_password: 新密碼

        Returns:
            (success: bool, message: str)
        """
        # 驗證舊密碼
        if not user.check_password(old_password):
            return False, '舊密碼錯誤'

        # 驗證新密碼強度
        is_valid, error = validate_password_strength(new_password)
        if not is_valid:
            return False, error

        # 檢查新舊密碼是否相同
        if old_password == new_password:
            return False, '新密碼不能與舊密碼相同'

        try:
            user.set_password(new_password)
            db.session.commit()
            return True, '密碼已成功變更'
        except Exception as e:
            db.session.rollback()
            return False, f'變更失敗：{str(e)}'

    @staticmethod
    def verify_email(user):
        """驗證信箱（標記為已驗證）

        Args:
            user: User 物件

        Returns:
            (success: bool, message: str)
        """
        try:
            user.is_verified = True
            db.session.commit()
            return True, '信箱驗證成功'
        except Exception as e:
            db.session.rollback()
            return False, f'驗證失敗：{str(e)}'

    @staticmethod
    def get_user_stats(user):
        """取得使用者統計資料

        Args:
            user: User 物件

        Returns:
            dict: 統計資料
        """
        from app.models.product import Product
        from app.models.transaction import Transaction
        from app.models.review import Review

        # 商品數量
        active_products = Product.query.filter_by(
            seller_id=user.id,
            status='active'
        ).count()

        sold_products = Product.query.filter_by(
            seller_id=user.id,
            status='sold'
        ).count()

        # 交易數量
        purchases = Transaction.query.filter_by(
            buyer_id=user.id,
            status='completed'
        ).count()

        sales = Transaction.query.filter_by(
            seller_id=user.id,
            status='completed'
        ).count()

        # 評價統計
        reviews = Review.query.filter_by(reviewee_id=user.id).all()
        avg_rating = sum(r.rating for r in reviews) / len(reviews) if reviews else 0
        review_count = len(reviews)

        return {
            'active_products': active_products,
            'sold_products': sold_products,
            'total_purchases': purchases,
            'total_sales': sales,
            'avg_rating': round(avg_rating, 1),
            'review_count': review_count
        }
