from functools import wraps
from flask import flash, redirect, url_for, abort
from flask_login import current_user

def login_required(f):
    """要求使用者必須登入"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('請先登入', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def anonymous_required(f):
    """要求使用者必須未登入（用於登入、註冊頁面）"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            return redirect(url_for('products.index'))
        return f(*args, **kwargs)
    return decorated_function

def verified_required(f):
    """要求使用者必須已驗證信箱"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('請先登入', 'warning')
            return redirect(url_for('auth.login'))

        if not current_user.is_verified:
            flash('請先驗證您的信箱', 'warning')
            return redirect(url_for('auth.profile'))

        return f(*args, **kwargs)
    return decorated_function

def ownership_required(model_class, id_param='id', owner_field='user_id'):
    """要求使用者必須是資源的擁有者

    Args:
        model_class: 資料模型類別
        id_param: URL 參數名稱
        owner_field: 擁有者欄位名稱
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('請先登入', 'warning')
                return redirect(url_for('auth.login'))

            # 取得資源 ID
            resource_id = kwargs.get(id_param)
            if not resource_id:
                abort(400)

            # 查詢資源
            resource = model_class.query.get_or_404(resource_id)

            # 檢查擁有權
            owner_id = getattr(resource, owner_field, None)
            if owner_id != current_user.id:
                abort(403)

            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    """要求使用者必須是管理員（預留功能）"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('請先登入', 'warning')
            return redirect(url_for('auth.login'))

        if not getattr(current_user, 'is_admin', False):
            abort(403)

        return f(*args, **kwargs)
    return decorated_function
