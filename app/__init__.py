from flask import Flask, render_template
from app.config import config
from app.extensions import db, login_manager, migrate, csrf, socketio
from datetime import datetime

def create_app(config_name='default'):
    """應用程式工廠函數"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # 初始化擴展
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")

    # 註冊 Blueprints
    from app.routes import auth, products, transactions, messages, reviews, notifications
    app.register_blueprint(auth.bp)
    app.register_blueprint(products.bp)
    app.register_blueprint(transactions.bp)
    app.register_blueprint(messages.bp)
    app.register_blueprint(reviews.bp)
    app.register_blueprint(notifications.bp)

    # 為前端模板兼容性添加endpoint別名
    # navbar.html 使用 url_for('index')，但實際路由在 products.index
    # 我們只需確保模板能正確生成 URL
    with app.app_context():
        # 為 'index' endpoint 創建別名指向 products.index
        if 'index' not in app.url_map._rules_by_endpoint:
            from flask import redirect, url_for as flask_url_for
            def index_redirect():
                return redirect(flask_url_for('products.index'))
            app.add_url_rule('/home', 'index', view_func=index_redirect)

    # 註冊錯誤處理器
    register_error_handlers(app)

    # 註冊 Jinja2 filters
    register_template_filters(app)

    # 註冊 context processors
    register_context_processors(app)

    # 註冊 SocketIO 事件
    from app.events import messages as message_events

    return app

def register_error_handlers(app):
    """註冊錯誤處理器"""

    @app.errorhandler(404)
    def not_found(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(403)
    def forbidden(error):
        return render_template('errors/403.html'), 403

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500

def register_template_filters(app):
    """註冊模板過濾器"""

    @app.template_filter('timeago')
    def timeago_filter(date):
        """時間前顯示（如：3 天前）"""
        if not date:
            return ''

        now = datetime.utcnow()
        diff = now - date

        seconds = diff.total_seconds()

        if seconds < 60:
            return '剛剛'
        elif seconds < 3600:
            return f'{int(seconds // 60)} 分鐘前'
        elif seconds < 86400:
            return f'{int(seconds // 3600)} 小時前'
        elif seconds < 2592000:
            return f'{int(seconds // 86400)} 天前'
        elif seconds < 31536000:
            return f'{int(seconds // 2592000)} 個月前'
        else:
            return f'{int(seconds // 31536000)} 年前'

    @app.template_filter('number_format')
    def number_format_filter(value):
        """數字格式化（如：25,000）"""
        if value is None:
            return '0'
        return '{:,}'.format(int(value))

def register_context_processors(app):
    """註冊 context processors（讓模板可以存取這些資料）"""

    @app.context_processor
    def inject_global_data():
        """注入全域資料到所有模板"""
        from flask_login import current_user
        from app.services.notification_service import NotificationService
        from app.services.message_service import MessageService
        from app.utils.helpers import (
            get_product_condition_label,
            get_product_status_label,
            get_transaction_status_label,
            get_transaction_type_label,
            format_price
        )

        # 如果使用者已登入，取得未讀訊息和通知數量
        unread_messages = 0
        unread_notifications = 0

        if current_user.is_authenticated:
            unread_messages = MessageService.get_unread_count(current_user.id)
            unread_notifications = NotificationService.get_unread_count(current_user.id)

        # 提供一個 globals 函數給模板使用（為了兼容前端模板）
        def template_globals():
            """模板可用的 globals 檢查"""
            return {
                'index': True,
                'products': True,
                'messages': True,
                'transactions': True,
                'reviews': True,
                'notifications': True,
                'auth': True
            }

        return {
            'unread_messages': unread_messages,
            'unread_notifications': unread_notifications,
            'get_product_condition_label': get_product_condition_label,
            'get_product_status_label': get_product_status_label,
            'get_transaction_status_label': get_transaction_status_label,
            'get_transaction_type_label': get_transaction_type_label,
            'format_price': format_price,
            'globals': template_globals
        }
