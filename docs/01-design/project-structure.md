# StudentTrade 專案結構說明

## 一、專案目錄總覽

```
StudentTrade/
├── .git/                           # Git 版本控制
├── .gitignore                      # Git 忽略檔案
├── .env                            # 環境變數（不提交）
├── .env.example                    # 環境變數範例
│
├── docs/                           # 📚 實作文檔
│   ├── 01-implementation-plan.md
│   ├── 02-system-architecture.md
│   ├── 03-database-design.md
│   ├── 04-api-design.md
│   ├── 05-frontend-design.md
│   ├── 06-project-structure.md     # 本文檔
│   ├── 07-development-guide.md
│   └── 08-deployment-guide.md
│
├── app/                            # 🎯 Flask 應用主目錄
│   ├── __init__.py                 # App Factory
│   ├── config.py                   # 配置檔
│   ├── extensions.py               # Flask 擴展初始化
│   │
│   ├── models/                     # 📊 資料庫模型
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── product.py
│   │   ├── category.py
│   │   ├── transaction.py
│   │   ├── message.py
│   │   ├── notification.py
│   │   └── review.py
│   │
│   ├── routes/                     # 🛣️ 路由（Blueprint）
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── products.py
│   │   ├── transactions.py
│   │   ├── messages.py
│   │   └── reviews.py
│   │
│   ├── services/                   # 🔧 業務邏輯層
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── product_service.py
│   │   ├── transaction_service.py
│   │   ├── message_service.py
│   │   └── notification_service.py
│   │
│   ├── utils/                      # 🛠️ 工具函數
│   │   ├── __init__.py
│   │   ├── validators.py
│   │   ├── decorators.py
│   │   ├── helpers.py
│   │   └── file_upload.py
│   │
│   ├── static/                     # 📦 靜態資源
│   │   ├── css/
│   │   │   ├── tailwind.css        # Tailwind 源文件
│   │   │   └── output.css          # 編譯後的 CSS
│   │   ├── js/
│   │   │   ├── main.js
│   │   │   └── components/
│   │   ├── images/
│   │   │   ├── logo.png
│   │   │   └── placeholders/
│   │   └── uploads/                # 使用者上傳檔案
│   │       ├── products/
│   │       └── avatars/
│   │
│   └── templates/                  # 🎨 Jinja2 模板
│       ├── base.html               # 基礎模板
│       │
│       ├── components/             # 可重用組件
│       │   ├── navbar.html
│       │   ├── footer.html
│       │   ├── product_card.html
│       │   ├── pagination.html
│       │   └── flash_messages.html
│       │
│       ├── auth/                   # 認證相關
│       │   ├── login.html
│       │   ├── register.html
│       │   └── profile.html
│       │
│       ├── products/               # 商品相關
│       │   ├── index.html          # 商品列表
│       │   ├── detail.html         # 商品詳情
│       │   ├── form.html           # 商品表單
│       │   └── my_products.html    # 我的商品
│       │
│       ├── transactions/           # 交易相關
│       │   ├── index.html
│       │   └── detail.html
│       │
│       ├── messages/               # 訊息相關
│       │   ├── index.html
│       │   └── chat.html
│       │
│       ├── reviews/                # 評價相關
│       │   ├── form.html
│       │   └── list.html
│       │
│       └── errors/                 # 錯誤頁面
│           ├── 404.html
│           ├── 500.html
│           └── 403.html
│
├── migrations/                     # 🗄️ 資料庫遷移
│   ├── versions/
│   └── alembic.ini
│
├── tests/                          # 🧪 測試檔案
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_products.py
│   ├── test_transactions.py
│   └── test_models.py
│
├── scripts/                        # 📜 腳本工具
│   ├── init_db.py                  # 初始化資料庫
│   ├── seed_data.py                # 種子資料
│   └── backup_db.py                # 資料庫備份
│
├── requirements.txt                # Python 依賴
├── requirements-dev.txt            # 開發依賴
├── run.py                          # 應用入口
├── tailwind.config.js              # Tailwind 配置
├── package.json                    # Node.js 依賴
│
└── [課程作業文檔]
    ├── README.md
    ├── dfd.md
    ├── hw3.md
    ├── hw5.md
    ├── plan.md
    └── video.md
```

---

## 二、目錄樹狀圖（Mermaid）

```mermaid
graph TD
    Root[StudentTrade/]

    Root --> Docs[📚 docs/]
    Root --> App[🎯 app/]
    Root --> Migrations[🗄️ migrations/]
    Root --> Tests[🧪 tests/]
    Root --> Scripts[📜 scripts/]
    Root --> Config[⚙️ 配置檔]

    App --> Models[models/<br/>資料庫模型]
    App --> Routes[routes/<br/>路由 Blueprint]
    App --> Services[services/<br/>業務邏輯]
    App --> Utils[utils/<br/>工具函數]
    App --> Static[static/<br/>靜態資源]
    App --> Templates[templates/<br/>Jinja2 模板]

    Models --> UserModel[user.py]
    Models --> ProductModel[product.py]
    Models --> TransModel[transaction.py]

    Routes --> AuthRoute[auth.py]
    Routes --> ProductRoute[products.py]
    Routes --> TransRoute[transactions.py]

    Static --> CSS[css/]
    Static --> JS[js/]
    Static --> Images[images/]
    Static --> Uploads[uploads/]

    Templates --> BaseTemplate[base.html]
    Templates --> AuthTemplates[auth/]
    Templates --> ProductTemplates[products/]
    Templates --> Components[components/]

    Config --> EnvFile[.env]
    Config --> Requirements[requirements.txt]
    Config --> RunFile[run.py]
    Config --> TailwindConfig[tailwind.config.js]

    style Root fill:#4CAF50,color:#fff
    style App fill:#2196F3,color:#fff
    style Models fill:#FF9800,color:#fff
    style Routes fill:#9C27B0,color:#fff
    style Templates fill:#F44336,color:#fff
```

---

## 三、核心檔案說明

### 3.1 應用入口（run.py）

**用途**: Flask 應用程式的啟動入口

```python
# run.py

from app import create_app
from app.extensions import db

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # 創建資料表（開發用）
    app.run(debug=True, host='0.0.0.0', port=5000)
```

---

### 3.2 應用工廠（app/__init__.py）

**用途**: 創建 Flask 應用實例

```python
# app/__init__.py

from flask import Flask
from app.config import Config
from app.extensions import db, login_manager, migrate, csrf

def create_app(config_class=Config):
    """應用程式工廠函數"""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 初始化擴展
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    # 註冊 Blueprints
    from app.routes import auth, products, transactions, messages, reviews
    app.register_blueprint(auth.bp)
    app.register_blueprint(products.bp)
    app.register_blueprint(transactions.bp)
    app.register_blueprint(messages.bp)
    app.register_blueprint(reviews.bp)

    # 註冊錯誤處理器
    register_error_handlers(app)

    # 註冊 Jinja2 filters
    register_template_filters(app)

    return app

def register_error_handlers(app):
    """註冊錯誤處理器"""
    from flask import render_template

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
    from datetime import datetime

    @app.template_filter('timeago')
    def timeago_filter(date):
        """時間前顯示（如：3 天前）"""
        # 實作...
        pass

    @app.template_filter('number_format')
    def number_format_filter(value):
        """數字格式化（如：25,000）"""
        return '{:,}'.format(value)
```

---

### 3.3 配置檔（app/config.py）

**用途**: 應用程式配置

```python
# app/config.py

import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '..', '.env'))

class Config:
    """基礎配置"""
    # 密鑰
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # 資料庫
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://studenttrade:password@localhost:5432/studenttrade'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False  # 開發時設為 True 可查看 SQL

    # 檔案上傳
    UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

    # Flask-Login
    LOGIN_VIEW = 'auth.login'
    LOGIN_MESSAGE = '請先登入'

    # 分頁
    PRODUCTS_PER_PAGE = 20
    TRANSACTIONS_PER_PAGE = 10
    MESSAGES_PER_PAGE = 50

class DevelopmentConfig(Config):
    """開發環境配置"""
    DEBUG = True
    SQLALCHEMY_ECHO = True

class ProductionConfig(Config):
    """生產環境配置"""
    DEBUG = False
    SQLALCHEMY_ECHO = False

class TestingConfig(Config):
    """測試環境配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
```

---

### 3.4 擴展初始化（app/extensions.py）

**用途**: 初始化 Flask 擴展

```python
# app/extensions.py

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()

# Flask-Login 配置
login_manager.login_view = 'auth.login'
login_manager.login_message = '請先登入'

@login_manager.user_loader
def load_user(user_id):
    from app.models.user import User
    return User.query.get(int(user_id))
```

---

## 四、Models 層（資料庫模型）

### 4.1 User Model（app/models/user.py）

```python
# app/models/user.py

from app.extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(80), nullable=False)
    phone = db.Column(db.String(20))
    student_id = db.Column(db.String(20), unique=True)
    avatar_url = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 關聯
    products = db.relationship('Product', backref='seller', lazy='dynamic')
    transactions_as_buyer = db.relationship('Transaction', foreign_keys='Transaction.buyer_id', backref='buyer', lazy='dynamic')
    transactions_as_seller = db.relationship('Transaction', foreign_keys='Transaction.seller_id', backref='seller', lazy='dynamic')

    def set_password(self, password):
        """設定密碼"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """驗證密碼"""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'
```

### 4.2 Product Model（app/models/product.py）

```python
# app/models/product.py

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
    view_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 關聯
    images = db.relationship('ProductImage', backref='product', lazy='dynamic', cascade='all, delete-orphan')
    transactions = db.relationship('Transaction', backref='product', lazy='dynamic')

    @property
    def primary_image(self):
        """取得主要圖片"""
        img = self.images.filter_by(is_primary=True).first()
        return img.image_url if img else '/static/images/placeholder.png'

    def increment_view_count(self):
        """增加瀏覽次數"""
        self.view_count += 1
        db.session.commit()

    def __repr__(self):
        return f'<Product {self.title}>'
```

---

## 五、Routes 層（路由 Blueprint）

### 5.1 Auth Blueprint（app/routes/auth.py）

```python
# app/routes/auth.py

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db
from app.models.user import User
from app.services.auth_service import AuthService

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """註冊"""
    if current_user.is_authenticated:
        return redirect(url_for('products.index'))

    if request.method == 'POST':
        result = AuthService.register(request.form)
        if result['success']:
            flash('註冊成功，請登入', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash(result['message'], 'error')

    return render_template('auth/register.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """登入"""
    if current_user.is_authenticated:
        return redirect(url_for('products.index'))

    if request.method == 'POST':
        user = AuthService.login(request.form.get('email'), request.form.get('password'))
        if user:
            login_user(user, remember=request.form.get('remember_me'))
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('products.index'))
        else:
            flash('帳號或密碼錯誤', 'error')

    return render_template('auth/login.html')

@bp.route('/logout')
@login_required
def logout():
    """登出"""
    logout_user()
    flash('已成功登出', 'success')
    return redirect(url_for('products.index'))

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """個人資料"""
    if request.method == 'POST':
        result = AuthService.update_profile(current_user, request.form, request.files)
        if result['success']:
            flash('資料更新成功', 'success')
            return redirect(url_for('auth.profile'))
        else:
            flash(result['message'], 'error')

    return render_template('auth/profile.html')
```

---

## 六、Services 層（業務邏輯）

### 6.1 Auth Service（app/services/auth_service.py）

```python
# app/services/auth_service.py

from app.extensions import db
from app.models.user import User
from app.utils.validators import validate_email, validate_password
from app.utils.file_upload import save_avatar

class AuthService:
    @staticmethod
    def register(form_data):
        """註冊新使用者"""
        email = form_data.get('email')
        password = form_data.get('password')
        username = form_data.get('username')

        # 驗證
        if not validate_email(email):
            return {'success': False, 'message': '無效的 Email 格式'}

        if User.query.filter_by(email=email).first():
            return {'success': False, 'message': 'Email 已被註冊'}

        if not validate_password(password):
            return {'success': False, 'message': '密碼至少需要 8 個字元'}

        # 建立使用者
        user = User(email=email, username=username)
        user.set_password(password)

        if form_data.get('student_id'):
            user.student_id = form_data.get('student_id')

        db.session.add(user)
        db.session.commit()

        return {'success': True}

    @staticmethod
    def login(email, password):
        """登入"""
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password) and user.is_active:
            return user
        return None

    @staticmethod
    def update_profile(user, form_data, files):
        """更新個人資料"""
        user.username = form_data.get('username', user.username)
        user.phone = form_data.get('phone', user.phone)

        # 處理頭像上傳
        if 'avatar' in files:
            avatar_file = files['avatar']
            if avatar_file.filename:
                avatar_url = save_avatar(avatar_file, user.id)
                if avatar_url:
                    user.avatar_url = avatar_url

        db.session.commit()
        return {'success': True}
```

---

## 七、Utils 層（工具函數）

### 7.1 檔案上傳（app/utils/file_upload.py）

```python
# app/utils/file_upload.py

import os
from werkzeug.utils import secure_filename
from flask import current_app
from PIL import Image
import uuid

def allowed_file(filename):
    """檢查檔案格式"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def save_product_image(file, product_id):
    """儲存商品圖片"""
    if not file or not allowed_file(file.filename):
        return None

    # 生成唯一檔名
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{product_id}_{uuid.uuid4().hex}.{ext}"

    # 儲存路徑
    upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'products')
    os.makedirs(upload_dir, exist_ok=True)

    filepath = os.path.join(upload_dir, filename)

    # 使用 Pillow 壓縮圖片
    img = Image.open(file)
    img.thumbnail((800, 800))  # 最大 800x800
    img.save(filepath, quality=85, optimize=True)

    return f'/static/uploads/products/{filename}'

def save_avatar(file, user_id):
    """儲存使用者頭像"""
    if not file or not allowed_file(file.filename):
        return None

    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"avatar_{user_id}.{ext}"

    upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'avatars')
    os.makedirs(upload_dir, exist_ok=True)

    filepath = os.path.join(upload_dir, filename)

    # 裁剪為正方形
    img = Image.open(file)
    img.thumbnail((200, 200))
    img.save(filepath, quality=90, optimize=True)

    return f'/static/uploads/avatars/{filename}'
```

---

## 八、Templates 層（模板）

### 8.1 基礎模板（app/templates/base.html）

```html
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}StudentTrade 校園二手平台{% endblock %}</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/output.css') }}">
    {% block extra_css %}{% endblock %}
</head>
<body class="bg-gray-50">
    <!-- 導航列 -->
    {% include 'components/navbar.html' %}

    <!-- Flash 訊息 -->
    {% include 'components/flash_messages.html' %}

    <!-- 主要內容 -->
    <main class="container mx-auto px-4 py-8">
        {% block content %}{% endblock %}
    </main>

    <!-- 頁尾 -->
    {% include 'components/footer.html' %}

    <script src="{{ url_for('static', filename='js/main.js') }}"></script>
    {% block extra_js %}{% endblock %}
</body>
</html>
```

---

## 九、環境變數範例（.env.example）

```bash
# .env.example

# Flask
SECRET_KEY=your-secret-key-here
FLASK_ENV=development

# PostgreSQL
DATABASE_URL=postgresql://username:password@localhost:5432/studenttrade

# 檔案上傳
UPLOAD_FOLDER=app/static/uploads
MAX_CONTENT_LENGTH=5242880  # 5MB

# Email (可選)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-password
```

---

## 十、總結

這個專案結構遵循 Flask 最佳實踐，採用清晰的分層架構：

- **Routes** - 處理 HTTP 請求
- **Services** - 業務邏輯
- **Models** - 資料庫模型
- **Utils** - 工具函數
- **Templates** - 前端模板

這樣的結構易於維護、測試與擴展。

下一步請閱讀：
- [07-development-guide.md](./07-development-guide.md) - 開發指南
- [08-deployment-guide.md](./08-deployment-guide.md) - 部署指南
