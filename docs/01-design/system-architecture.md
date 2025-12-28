# StudentTrade 系統架構設計

## 一、系統架構概述

### 1.1 架構類型

**StudentTrade** 採用 **Flask Monolithic（一體式）架構**，前後端一體化設計，使用伺服器端渲染（Server-Side Rendering, SSR）。

**架構特點**:
- 單一應用程式部署
- Jinja2 模板引擎進行伺服器端渲染
- Blueprint 模組化路由設計
- SQLAlchemy ORM 資料存取層
- Session-based 認證機制

### 1.2 系統層級架構

```mermaid
graph TB
    subgraph "客戶端層 Client Layer"
        Browser[Web 瀏覽器<br/>Desktop & Mobile]
    end

    subgraph "應用層 Application Layer - Flask"
        subgraph "呈現層 Presentation"
            Templates[Jinja2 Templates<br/>+ Tailwind CSS]
        end

        subgraph "路由層 Routes - Blueprint"
            AuthRoute[認證路由<br/>auth.py]
            ProductRoute[商品路由<br/>products.py]
            TransactionRoute[交易路由<br/>transactions.py]
            MessageRoute[訊息路由<br/>messages.py]
            ReviewRoute[評價路由<br/>reviews.py]
        end

        subgraph "業務邏輯層 Business Logic"
            AuthService[認證服務<br/>auth_service.py]
            ProductService[商品服務<br/>product_service.py]
            TransService[交易服務<br/>transaction_service.py]
            MsgService[訊息服務<br/>message_service.py]
            NotifyService[通知服務<br/>notification_service.py]
        end

        subgraph "資料存取層 Data Access"
            Models[SQLAlchemy Models<br/>ORM]
        end

        subgraph "工具層 Utilities"
            Validators[表單驗證器]
            Decorators[裝飾器]
            FileUpload[檔案上傳]
        end
    end

    subgraph "資料層 Data Layer"
        DB[(PostgreSQL 16<br/>Database)]
        FileStorage[檔案儲存<br/>static/uploads/]
    end

    Browser <-->|HTTP/HTTPS| AuthRoute
    Browser <-->|HTTP/HTTPS| ProductRoute
    Browser <-->|HTTP/HTTPS| TransactionRoute
    Browser <-->|HTTP/HTTPS| MessageRoute
    Browser <-->|HTTP/HTTPS| ReviewRoute

    AuthRoute --> Templates
    ProductRoute --> Templates
    TransactionRoute --> Templates
    MessageRoute --> Templates
    ReviewRoute --> Templates

    Templates -->|HTML Response| Browser

    AuthRoute --> AuthService
    ProductRoute --> ProductService
    TransactionRoute --> TransService
    MessageRoute --> MsgService

    AuthService --> Validators
    ProductService --> FileUpload

    AuthService --> Models
    ProductService --> Models
    TransService --> Models
    MsgService --> Models
    NotifyService --> Models

    Models <-->|SQL| DB
    FileUpload -->|Save/Read| FileStorage

    style Browser fill:#e1f5ff
    style Templates fill:#fff4e1
    style DB fill:#e8f5e9
    style FileStorage fill:#e8f5e9
```

---

## 二、請求處理流程

### 2.1 標準請求流程

```mermaid
sequenceDiagram
    participant User as 使用者
    participant Browser as 瀏覽器
    participant Flask as Flask App
    participant Route as Route Handler
    participant Service as Business Service
    participant Model as SQLAlchemy Model
    participant DB as PostgreSQL
    participant Template as Jinja2 Template

    User->>Browser: 發起請求（點擊/輸入）
    Browser->>Flask: HTTP Request
    Flask->>Flask: URL 路由匹配
    Flask->>Route: 調用路由處理器

    Route->>Route: 驗證使用者認證
    Route->>Route: 解析請求參數

    Route->>Service: 調用業務邏輯
    Service->>Service: 資料驗證
    Service->>Model: ORM 操作
    Model->>DB: SQL Query
    DB-->>Model: 返回資料
    Model-->>Service: Python 對象
    Service->>Service: 業務處理
    Service-->>Route: 處理後的資料

    Route->>Template: 傳遞資料 + 選擇模板
    Template->>Template: Jinja2 渲染
    Template-->>Route: 生成 HTML

    Route-->>Flask: HTTP Response
    Flask-->>Browser: HTML + CSS + JS
    Browser-->>User: 顯示頁面
```

### 2.2 認證流程

```mermaid
sequenceDiagram
    participant User as 使用者
    participant Browser as 瀏覽器
    participant AuthRoute as 認證路由
    participant AuthService as 認證服務
    participant UserModel as User Model
    participant DB as PostgreSQL
    participant Session as Flask Session

    User->>Browser: 輸入帳號密碼
    Browser->>AuthRoute: POST /auth/login

    AuthRoute->>AuthService: login(email, password)
    AuthService->>UserModel: 查詢使用者
    UserModel->>DB: SELECT * FROM users WHERE email=?
    DB-->>UserModel: User 資料

    AuthService->>AuthService: 驗證密碼 (bcrypt)

    alt 驗證成功
        AuthService->>Session: 儲存 user_id
        Session-->>AuthService: Session ID
        AuthService-->>AuthRoute: 成功
        AuthRoute-->>Browser: Redirect 到首頁 + Set-Cookie
        Browser-->>User: 顯示首頁（已登入）
    else 驗證失敗
        AuthService-->>AuthRoute: 失敗（錯誤訊息）
        AuthRoute-->>Browser: 返回登入頁 + 錯誤提示
        Browser-->>User: 顯示錯誤訊息
    end
```

### 2.3 商品刊登流程

```mermaid
sequenceDiagram
    participant User as 賣家
    participant Browser as 瀏覽器
    participant ProductRoute as 商品路由
    participant ProductService as 商品服務
    participant FileUpload as 檔案上傳工具
    participant ProductModel as Product Model
    participant ImageModel as ProductImage Model
    participant DB as PostgreSQL
    participant Storage as 檔案儲存

    User->>Browser: 填寫商品表單 + 上傳圖片
    Browser->>ProductRoute: POST /products/new

    ProductRoute->>ProductRoute: 檢查認證
    ProductRoute->>ProductService: create_product(data, files)

    ProductService->>ProductService: 驗證表單資料

    ProductService->>FileUpload: 處理圖片上傳
    FileUpload->>FileUpload: 驗證格式與大小
    FileUpload->>FileUpload: 生成唯一檔名
    FileUpload->>Storage: 儲存圖片檔案
    Storage-->>FileUpload: 檔案路徑

    ProductService->>ProductModel: 創建商品記錄
    ProductModel->>DB: INSERT INTO products
    DB-->>ProductModel: product_id

    ProductService->>ImageModel: 創建圖片記錄
    ImageModel->>DB: INSERT INTO product_images

    ProductService-->>ProductRoute: 成功 (product_id)
    ProductRoute-->>Browser: Redirect 到商品詳情頁
    Browser-->>User: 顯示商品詳情
```

---

## 三、系統核心組件

### 3.1 Flask 應用程式初始化

**應用程式工廠模式（App Factory Pattern）**:

```python
# app/__init__.py

from flask import Flask
from app.extensions import db, login_manager, migrate
from app.config import Config

def create_app(config_class=Config):
    """Flask 應用程式工廠函數"""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 初始化擴展
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # 註冊 Blueprints
    from app.routes import auth, products, transactions, messages, reviews
    app.register_blueprint(auth.bp)
    app.register_blueprint(products.bp)
    app.register_blueprint(transactions.bp)
    app.register_blueprint(messages.bp)
    app.register_blueprint(reviews.bp)

    # 錯誤處理器
    register_error_handlers(app)

    return app
```

**組件說明**:
- `Config` - 配置類別（資料庫連接、密鑰等）
- `db` - SQLAlchemy 資料庫實例
- `login_manager` - Flask-Login 認證管理
- `migrate` - Flask-Migrate 資料庫遷移
- `Blueprints` - 模組化路由

### 3.2 Blueprint 模組化設計

```mermaid
graph TD
    FlaskApp[Flask Application]

    FlaskApp --> AuthBP[auth Blueprint<br/>/auth/*]
    FlaskApp --> ProductBP[products Blueprint<br/>/products/* 和 /]
    FlaskApp --> TransBP[transactions Blueprint<br/>/transactions/*]
    FlaskApp --> MsgBP[messages Blueprint<br/>/messages/*]
    FlaskApp --> ReviewBP[reviews Blueprint<br/>/reviews/*]

    AuthBP --> AuthRoutes["/register<br/>/login<br/>/logout<br/>/profile"]
    ProductBP --> ProductRoutes["/products<br/>/products/new<br/>/products/:id<br/>/my-products"]
    TransBP --> TransRoutes["/transactions<br/>/transactions/:id<br/>/transactions/create"]
    MsgBP --> MsgRoutes["/messages<br/>/messages/:user_id<br/>/messages/send"]
    ReviewBP --> ReviewRoutes["/reviews/new<br/>/users/:id/reviews"]

    style FlaskApp fill:#4CAF50,color:#fff
    style AuthBP fill:#2196F3,color:#fff
    style ProductBP fill:#FF9800,color:#fff
    style TransBP fill:#9C27B0,color:#fff
    style MsgBP fill:#F44336,color:#fff
    style ReviewBP fill:#009688,color:#fff
```

**Blueprint 優勢**:
- 模組化開發，職責分離
- 易於維護與擴展
- 支援團隊並行開發
- 可重用性高

### 3.3 資料庫連接架構

```mermaid
graph LR
    FlaskApp[Flask Application]
    SQLAlchemy[SQLAlchemy ORM]
    Psycopg2[psycopg2 Driver]
    PostgreSQL[(PostgreSQL 16)]

    FlaskApp -->|使用| SQLAlchemy
    SQLAlchemy -->|透過| Psycopg2
    Psycopg2 -->|連接| PostgreSQL

    SQLAlchemy -.->|Models| UserModel[User Model]
    SQLAlchemy -.->|Models| ProductModel[Product Model]
    SQLAlchemy -.->|Models| TransactionModel[Transaction Model]

    style PostgreSQL fill:#336791,color:#fff
    style SQLAlchemy fill:#D71F00,color:#fff
```

**連接配置**:
```python
# app/config.py

import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'

    # PostgreSQL 資料庫連接
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://username:password@localhost:5432/studenttrade'

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True  # 開發模式顯示 SQL
```

---

## 四、認證與授權機制

### 4.1 認證架構

```mermaid
graph TD
    User[使用者請求]

    User --> CheckAuth{是否已認證?}

    CheckAuth -->|是| CheckSession{Session 有效?}
    CheckAuth -->|否| LoginPage[導向登入頁]

    CheckSession -->|有效| LoadUser[載入使用者資料]
    CheckSession -->|無效| LoginPage

    LoadUser --> CheckPermission{是否有權限?}

    CheckPermission -->|有| AllowAccess[允許存取]
    CheckPermission -->|無| Error403[403 Forbidden]

    LoginPage --> LoginForm[登入表單]
    LoginForm --> ValidateCredentials{驗證帳密}

    ValidateCredentials -->|成功| CreateSession[建立 Session]
    ValidateCredentials -->|失敗| LoginError[顯示錯誤]

    CreateSession --> AllowAccess
    LoginError --> LoginForm

    style AllowAccess fill:#4CAF50,color:#fff
    style Error403 fill:#F44336,color:#fff
    style LoginPage fill:#FF9800,color:#fff
```

### 4.2 Flask-Login 實作

**使用者模型**:
```python
# app/models/user.py

from flask_login import UserMixin
from app.extensions import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(80), nullable=False)

    def check_password(self, password):
        """驗證密碼"""
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)
```

**登入管理**:
```python
# app/extensions.py

from flask_login import LoginManager

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = '請先登入'

@login_manager.user_loader
def load_user(user_id):
    from app.models.user import User
    return User.query.get(int(user_id))
```

**認證裝飾器**:
```python
# app/utils/decorators.py

from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user

def login_required(f):
    """要求使用者登入"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('請先登入', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def seller_required(f):
    """要求使用者是商品擁有者"""
    @wraps(f)
    def decorated_function(product_id, *args, **kwargs):
        from app.models.product import Product
        product = Product.query.get_or_404(product_id)
        if product.user_id != current_user.id:
            flash('無權限執行此操作', 'danger')
            return redirect(url_for('products.index'))
        return f(product_id, *args, **kwargs)
    return decorated_function
```

---

## 五、資料流向

### 5.1 讀取資料流程（查詢商品）

```mermaid
flowchart LR
    A[使用者訪問<br/>商品列表頁] --> B[products.index<br/>路由]
    B --> C[ProductService<br/>get_products]
    C --> D[Product Model<br/>Query]
    D --> E[PostgreSQL<br/>SELECT]
    E --> F[返回商品列表]
    F --> G[Jinja2 模板<br/>渲染]
    G --> H[HTML 頁面<br/>返回瀏覽器]

    style A fill:#e3f2fd
    style E fill:#c8e6c9
    style H fill:#fff9c4
```

### 5.2 寫入資料流程（刊登商品）

```mermaid
flowchart LR
    A[使用者提交<br/>商品表單] --> B[products.create<br/>路由]
    B --> C{表單驗證}

    C -->|失敗| D[返回表單<br/>顯示錯誤]
    C -->|成功| E[ProductService<br/>create_product]

    E --> F[處理圖片上傳]
    F --> G[儲存至<br/>static/uploads/]

    E --> H[Product Model<br/>Create]
    H --> I[PostgreSQL<br/>INSERT]

    I --> J[返回 product_id]
    J --> K[Redirect 到<br/>商品詳情頁]

    style A fill:#e3f2fd
    style D fill:#ffcdd2
    style G fill:#c8e6c9
    style I fill:#c8e6c9
    style K fill:#fff9c4
```

### 5.3 交易流程

```mermaid
stateDiagram-v2
    [*] --> 商品刊登
    商品刊登 --> 等待買家

    等待買家 --> 買家發起交易請求

    買家發起交易請求 --> 等待賣家回應

    等待賣家回應 --> 賣家接受: accept
    等待賣家回應 --> 交易取消: reject

    賣家接受 --> 交易進行中

    交易進行中 --> 買家確認完成: complete
    交易進行中 --> 交易取消: cancel

    買家確認完成 --> 評價階段
    評價階段 --> 交易完成

    交易取消 --> 商品重新上架
    商品重新上架 --> 等待買家

    交易完成 --> [*]
```

---

## 六、安全性設計

### 6.1 安全措施

| 安全威脅 | 防護措施 | 實作方式 |
|---------|---------|---------|
| **SQL 注入** | 使用 ORM | SQLAlchemy 參數化查詢 |
| **XSS 攻擊** | 自動跳脫 | Jinja2 自動 HTML escape |
| **CSRF 攻擊** | CSRF Token | Flask-WTF CSRF 保護 |
| **密碼洩漏** | 密碼加密 | Bcrypt 雜湊加密 |
| **Session 劫持** | Secure Cookie | HTTPS + HttpOnly + SameSite |
| **檔案上傳漏洞** | 檔案驗證 | 限制檔案類型與大小 |
| **暴力破解** | 登入限制 | 失敗次數限制（可選） |

### 6.2 密碼安全流程

```mermaid
sequenceDiagram
    participant User as 使用者
    participant Form as 註冊表單
    participant Service as AuthService
    participant Bcrypt as Bcrypt
    participant DB as PostgreSQL

    User->>Form: 輸入密碼
    Form->>Service: register(email, password)

    Service->>Bcrypt: generate_password_hash(password)
    Bcrypt->>Bcrypt: 加鹽 + 雜湊
    Bcrypt-->>Service: password_hash

    Service->>DB: 儲存 email + password_hash
    DB-->>Service: 成功

    Note over Bcrypt: 原始密碼永不儲存
    Note over DB: 只儲存雜湊值
```

### 6.3 CSRF 保護

```python
# app/routes/products.py

from flask_wtf.csrf import CSRFProtect
from flask import render_template, request

csrf = CSRFProtect(app)

@bp.route('/products/new', methods=['GET', 'POST'])
@login_required
def create_product():
    if request.method == 'POST':
        # Flask-WTF 自動驗證 CSRF Token
        # 如果 token 無效會自動返回 400 錯誤
        ...
```

```html
<!-- app/templates/products/form.html -->

<form method="POST" action="{{ url_for('products.create') }}">
    <!-- CSRF Token 自動包含 -->
    {{ form.csrf_token }}

    <input type="text" name="title" required>
    <button type="submit">提交</button>
</form>
```

---

## 七、效能優化策略

### 7.1 資料庫優化

**索引設計**:
```sql
-- 商品搜尋索引
CREATE INDEX idx_products_title ON products(title);
CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_products_status ON products(status);

-- 複合索引（價格範圍查詢）
CREATE INDEX idx_products_price_status ON products(price, status);

-- 全文搜尋索引（PostgreSQL）
CREATE INDEX idx_products_search ON products
USING GIN(to_tsvector('english', title || ' ' || description));
```

**查詢優化**:
- 使用 `limit()` 限制查詢結果
- 使用 `offset()` 實現分頁
- 避免 N+1 查詢問題（使用 `joinedload()`）
- 使用 `select_related` 預載關聯資料

### 7.2 快取策略（進階）

```python
# 使用 Flask-Caching

from flask_caching import Cache

cache = Cache(config={'CACHE_TYPE': 'simple'})

@cache.cached(timeout=300)  # 快取 5 分鐘
def get_popular_products():
    """獲取熱門商品（快取）"""
    return Product.query.filter_by(status='active')\
                        .order_by(Product.view_count.desc())\
                        .limit(10).all()
```

### 7.3 靜態資源優化

**Tailwind CSS 生產版本**:
```bash
# 編譯並壓縮 CSS
npx tailwindcss -i ./app/static/css/tailwind.css \
                -o ./app/static/css/output.css \
                --minify
```

**圖片優化**:
- 限制上傳大小（< 5MB）
- 自動壓縮圖片（Pillow）
- 使用適當的圖片格式（JPEG for photos, PNG for graphics）
- 延遲載入（Lazy Loading）

---

## 八、錯誤處理

### 8.1 錯誤處理流程

```mermaid
flowchart TD
    A[請求] --> B{路由匹配}

    B -->|404| C[404 頁面<br/>找不到頁面]
    B -->|成功| D[執行處理器]

    D --> E{是否發生錯誤?}

    E -->|無錯誤| F[正常返回]
    E -->|403| G[403 頁面<br/>無權限]
    E -->|500| H[500 頁面<br/>伺服器錯誤]
    E -->|其他| I[通用錯誤頁面]

    H --> J[記錄錯誤日誌]

    style C fill:#FF5722,color:#fff
    style G fill:#FF9800,color:#fff
    style H fill:#F44336,color:#fff
    style F fill:#4CAF50,color:#fff
```

### 8.2 錯誤處理器

```python
# app/__init__.py

def register_error_handlers(app):
    """註冊錯誤處理器"""

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()  # 回滾資料庫
        app.logger.error(f'Server Error: {error}')
        return render_template('errors/500.html'), 500
```

---

## 九、總結

### 9.1 架構優勢

✅ **簡單易懂** - Monolithic 架構適合小型團隊
✅ **開發效率高** - 前後端一體，減少溝通成本
✅ **部署簡單** - 單一應用程式，部署容易
✅ **維護方便** - 模組化設計，職責清晰

### 9.2 關鍵設計決策

1. **Flask Monolithic** - 適合專案規模與團隊
2. **Blueprint 模組化** - 清晰的程式碼組織
3. **SQLAlchemy ORM** - 簡化資料庫操作
4. **Session-based 認證** - 簡單可靠的認證機制
5. **Jinja2 SSR** - 良好的 SEO 與效能

### 9.3 下一步

請繼續閱讀：
- [03-database-design.md](./03-database-design.md) - 資料庫設計
- [04-api-design.md](./04-api-design.md) - API 路由設計
- [07-development-guide.md](./07-development-guide.md) - 開發指南
