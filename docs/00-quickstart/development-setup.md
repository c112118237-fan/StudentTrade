# StudentTrade 開發指南

## 一、開發環境建置

### 1.1 必要軟體安裝

| 軟體 | 版本要求 | 下載連結 |
|------|---------|---------|
| **Python** | 3.11+ | https://www.python.org/downloads/ |
| **PostgreSQL** | 16 | https://www.postgresql.org/download/ |
| **Node.js** | 18+ | https://nodejs.org/ |
| **Git** | 最新版 | https://git-scm.com/ |

**推薦 IDE**:
- Visual Studio Code
- PyCharm Professional

---

### 1.2 環境建置步驟

```mermaid
flowchart LR
    A[1. 安裝 Python] --> B[2. 安裝 PostgreSQL]
    B --> C[3. 安裝 Node.js]
    C --> D[4. Clone 專案]
    D --> E[5. 建立虛擬環境]
    E --> F[6. 安裝依賴]
    F --> G[7. 配置環境變數]
    G --> H[8. 初始化資料庫]
    H --> I[9. 啟動應用]

    style A fill:#E3F2FD
    style E fill:#FFF9C4
    style H fill:#C8E6C9
    style I fill:#4CAF50,color:#fff
```

---

## 二、詳細建置步驟

### 步驟 1: Clone 專案

```bash
# Clone 專案倉庫
git clone https://github.com/your-repo/StudentTrade.git
cd StudentTrade
```

---

### 步驟 2: 建立 Python 虛擬環境

**Windows**:
```bash
# 建立虛擬環境
python -m venv venv

# 啟動虛擬環境
venv\Scripts\activate
```

**macOS/Linux**:
```bash
# 建立虛擬環境
python3 -m venv venv

# 啟動虛擬環境
source venv/bin/activate
```

**確認虛擬環境已啟動**:
```bash
# 應該會看到 (venv) 前綴
(venv) PS F:\StudentTrade>
```

---

### 步驟 3: 安裝 Python 依賴

```bash
# 升級 pip
pip install --upgrade pip

# 安裝生產依賴
pip install -r requirements.txt

# 安裝開發依賴（可選）
pip install -r requirements-dev.txt
```

**requirements.txt 內容**:
```
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-Login==0.6.3
Flask-Migrate==4.0.5
Flask-WTF==1.2.1
psycopg2-binary==2.9.9
python-dotenv==1.0.0
Werkzeug==3.0.1
Pillow==10.1.0
email-validator==2.1.0
```

**requirements-dev.txt 內容**:
```
pytest==7.4.3
pytest-flask==1.3.0
pytest-cov==4.1.0
black==23.12.0
flake8==6.1.0
```

---

### 步驟 4: 安裝 Node.js 依賴（Tailwind CSS）

```bash
# 初始化 npm（如果 package.json 不存在）
npm init -y

# 安裝 Tailwind CSS
npm install -D tailwindcss@4.1
npm install -D @tailwindcss/cli

# 初始化 Tailwind 配置
npx tailwindcss init
```

**package.json 內容**:
```json
{
  "name": "studenttrade",
  "version": "1.0.0",
  "scripts": {
    "dev": "tailwindcss -i ./app/static/css/tailwind.css -o ./app/static/css/output.css --watch",
    "build": "tailwindcss -i ./app/static/css/tailwind.css -o ./app/static/css/output.css --minify"
  },
  "devDependencies": {
    "tailwindcss": "^4.1.0"
  }
}
```

**tailwind.config.js 內容**:
```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/templates/**/*.html",
    "./app/static/js/**/*.js"
  ],
  theme: {
    extend: {
      colors: {
        primary: '#2563eb',
        secondary: '#64748b',
      }
    },
  },
  plugins: [],
}
```

**app/static/css/tailwind.css 內容**:
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

/* 自訂樣式 */
@layer components {
  .btn {
    @apply px-4 py-2 rounded-lg font-medium transition-colors;
  }

  .btn-primary {
    @apply bg-blue-600 text-white hover:bg-blue-700;
  }

  .btn-secondary {
    @apply bg-gray-200 text-gray-700 hover:bg-gray-300;
  }
}
```

**編譯 Tailwind CSS**:
```bash
# 開發模式（監聽變更）
npm run dev

# 生產模式（壓縮）
npm run build
```

---

### 步驟 5: 配置 PostgreSQL 資料庫

**建立資料庫**:
```bash
# 使用 psql 進入 PostgreSQL
psql -U postgres

# 建立資料庫
CREATE DATABASE studenttrade;

# 建立使用者（可選）
CREATE USER studenttrade_user WITH PASSWORD 'your_password';

# 授予權限
GRANT ALL PRIVILEGES ON DATABASE studenttrade TO studenttrade_user;

# 退出
\q
```

---

### 步驟 6: 配置環境變數

**建立 .env 檔案**:
```bash
# 複製範例檔案
cp .env.example .env
```

**編輯 .env**:
```bash
# Flask
SECRET_KEY=your-very-secret-key-here-change-me
FLASK_ENV=development

# PostgreSQL
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/studenttrade

# 檔案上傳
UPLOAD_FOLDER=app/static/uploads
MAX_CONTENT_LENGTH=5242880
```

**生成密鑰**:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

### 步驟 7: 初始化資料庫

```bash
# 初始化 Flask-Migrate
flask db init

# 建立遷移檔案
flask db migrate -m "Initial migration"

# 執行遷移
flask db upgrade

# 建立種子資料（可選）
python scripts/seed_data.py
```

**seed_data.py 範例**:
```python
# scripts/seed_data.py

from app import create_app
from app.extensions import db
from app.models.category import Category

app = create_app()

with app.app_context():
    # 建立分類
    categories = [
        {'name': '書籍', 'description': '教科書、參考書、小說等'},
        {'name': '文具', 'description': '筆記本、筆、文具用品'},
        {'name': '電子產品', 'description': '3C 產品、電腦周邊'},
        {'name': '生活用品', 'description': '日常生活用品'},
        {'name': '運動用品', 'description': '運動器材、服裝'},
        {'name': '其他', 'description': '其他類別商品'},
    ]

    for cat_data in categories:
        cat = Category.query.filter_by(name=cat_data['name']).first()
        if not cat:
            cat = Category(**cat_data)
            db.session.add(cat)

    db.session.commit()
    print("種子資料建立完成！")
```

---

### 步驟 8: 啟動應用

**開發模式**:
```bash
# 方法 1: 使用 run.py
python run.py

# 方法 2: 使用 Flask CLI
flask run

# 方法 3: 指定 host 和 port
flask run --host=0.0.0.0 --port=5000
```

**同時運行 Tailwind 監聽**:
```bash
# 終端機 1: 運行 Flask
python run.py

# 終端機 2: 監聽 Tailwind
npm run dev
```

**訪問應用**:
```
http://localhost:5000
```

---

## 三、開發流程

### 3.1 開發週期圖

```mermaid
flowchart TD
    Start([開始開發]) --> Branch[建立功能分支]
    Branch --> Code[撰寫程式碼]
    Code --> Test[執行測試]

    Test --> TestPass{測試通過?}
    TestPass -->|否| Debug[除錯]
    Debug --> Code

    TestPass -->|是| Format[格式化程式碼]
    Format --> Commit[提交變更]
    Commit --> Push[推送到遠端]

    Push --> PR[建立 Pull Request]
    PR --> Review[Code Review]

    Review --> ReviewOK{通過審核?}
    ReviewOK -->|否| Fix[修正問題]
    Fix --> Code

    ReviewOK -->|是| Merge[合併到 main]
    Merge --> Deploy[部署]
    Deploy --> End([完成])

    style Start fill:#4CAF50,color:#fff
    style End fill:#4CAF50,color:#fff
    style TestPass fill:#FFF9C4
    style ReviewOK fill:#FFF9C4
```

---

### 3.2 Git 工作流程

**建立功能分支**:
```bash
# 更新 main 分支
git checkout main
git pull origin main

# 建立新分支
git checkout -b feature/user-authentication
```

**提交變更**:
```bash
# 查看狀態
git status

# 加入檔案
git add app/routes/auth.py app/services/auth_service.py

# 提交（使用有意義的訊息）
git commit -m "Add user registration and login functionality"

# 推送到遠端
git push -u origin feature/user-authentication
```

**提交訊息規範**:
```
<type>: <subject>

<body>

<footer>
```

**Type 類型**:
- `feat`: 新功能
- `fix`: 修復 Bug
- `docs`: 文檔變更
- `style`: 格式調整（不影響程式碼）
- `refactor`: 重構
- `test`: 測試相關
- `chore`: 建置工具或輔助工具

**範例**:
```
feat: Add user authentication system

- Implement user registration with email verification
- Add login/logout functionality
- Create profile management page

Closes #123
```

---

## 四、階段性開發指南

### 階段 1: 環境建置 ✅

**目標**: 開發環境完全就緒

**檢查清單**:
- [ ] Python 3.11+ 安裝完成
- [ ] PostgreSQL 16 安裝完成
- [ ] Node.js 18+ 安裝完成
- [ ] 虛擬環境建立並啟動
- [ ] Python 依賴全部安裝
- [ ] Tailwind CSS 編譯成功
- [ ] 資料庫連接測試通過
- [ ] Flask 應用可正常啟動
- [ ] 訪問 http://localhost:5000 有回應

---

### 階段 2: 資料庫實作（3-5 天）

**目標**: 完成所有資料庫模型並測試

**步驟 2.1: 建立所有 Models**
```bash
# 建立檔案
app/models/user.py
app/models/category.py
app/models/product.py
app/models/product_image.py
app/models/transaction.py
app/models/message.py
app/models/notification.py
app/models/review.py
```

**步驟 2.2: 在 models/__init__.py 匯入**
```python
# app/models/__init__.py

from app.models.user import User
from app.models.category import Category
from app.models.product import Product
from app.models.product_image import ProductImage
from app.models.transaction import Transaction
from app.models.message import Message
from app.models.notification import Notification
from app.models.review import Review
```

**步驟 2.3: 建立資料庫遷移**
```bash
flask db migrate -m "Add all models"
flask db upgrade
```

**步驟 2.4: 測試資料庫**
```python
# 在 Flask shell 測試
flask shell

>>> from app.models.user import User
>>> from app.extensions import db
>>> user = User(email='test@test.com', username='測試')
>>> user.set_password('password')
>>> db.session.add(user)
>>> db.session.commit()
>>> User.query.all()
```

**檢查清單**:
- [ ] 8 個 Models 全部建立
- [ ] 資料庫遷移成功
- [ ] 所有資料表建立成功
- [ ] 外鍵關聯正確
- [ ] 可以成功建立測試資料

---

### 階段 3: 後端核心功能（2-3 週）

#### 3.1 使用者認證系統（5-7 天）

**實作順序**:
1. 建立 AuthService (`app/services/auth_service.py`)
2. 建立 auth Blueprint (`app/routes/auth.py`)
3. 建立認證模板 (`app/templates/auth/`)
4. 測試註冊、登入、登出功能

**檢查清單**:
- [ ] 使用者可以註冊
- [ ] Email 唯一性驗證
- [ ] 密碼加密（bcrypt）
- [ ] 使用者可以登入
- [ ] Session 管理正常
- [ ] 使用者可以登出
- [ ] 個人資料編輯功能
- [ ] 頭像上傳功能

#### 3.2 商品管理系統（7-10 天）

**實作順序**:
1. 建立 ProductService
2. 建立 products Blueprint
3. 實作商品 CRUD
4. 實作圖片上傳
5. 實作搜尋與篩選
6. 建立商品模板

**檢查清單**:
- [ ] 商品刊登功能
- [ ] 商品列表顯示
- [ ] 商品詳情頁
- [ ] 商品編輯功能
- [ ] 商品刪除功能（軟刪除）
- [ ] 圖片上傳與壓縮
- [ ] 關鍵字搜尋
- [ ] 分類篩選
- [ ] 價格範圍篩選
- [ ] 分頁功能

#### 3.3 交易系統（5-8 天）

**實作順序**:
1. 建立 TransactionService
2. 建立 transactions Blueprint
3. 實作交易流程
4. 建立交易模板

**檢查清單**:
- [ ] 發起交易請求
- [ ] 賣家接受/拒絕交易
- [ ] 交易狀態管理
- [ ] 完成交易
- [ ] 取消交易
- [ ] 交易記錄查詢

---

### 階段 4: 前端開發（2-3 週）

#### 4.1 基礎框架（3-5 天）

**實作順序**:
1. 建立 base.html 模板
2. 建立 navbar 組件
3. 建立 footer 組件
4. 配置 Tailwind CSS
5. 建立可重用組件

**檢查清單**:
- [ ] base.html 完成
- [ ] 導航列（響應式）
- [ ] 頁尾
- [ ] Flash Messages 組件
- [ ] 商品卡片組件
- [ ] 分頁組件
- [ ] Tailwind CSS 正常運作

#### 4.2 頁面實作（10-15 天）

**每個頁面的實作步驟**:
1. 建立 HTML 模板
2. 套用 Tailwind 樣式
3. 加入互動 JavaScript
4. 測試響應式設計
5. 跨瀏覽器測試

**檢查清單**:
- [ ] 首頁（商品列表）
- [ ] 商品詳情頁
- [ ] 商品表單頁
- [ ] 登入頁
- [ ] 註冊頁
- [ ] 個人資料頁
- [ ] 交易列表頁
- [ ] 交易詳情頁
- [ ] 訊息頁
- [ ] 所有頁面響應式設計測試通過

---

### 階段 5: 測試與優化（1-2 週）

#### 5.1 單元測試

```bash
# 執行所有測試
pytest

# 執行特定測試
pytest tests/test_auth.py

# 查看測試覆蓋率
pytest --cov=app --cov-report=html
```

**tests/test_auth.py 範例**:
```python
import pytest
from app import create_app
from app.extensions import db
from app.models.user import User

@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_register(client):
    """測試註冊功能"""
    response = client.post('/auth/register', data={
        'email': 'test@test.com',
        'username': '測試使用者',
        'password': 'password123',
        'password_confirm': 'password123'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert User.query.filter_by(email='test@test.com').first() is not None

def test_login(client):
    """測試登入功能"""
    # 先建立使用者
    user = User(email='test@test.com', username='測試')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()

    # 測試登入
    response = client.post('/auth/login', data={
        'email': 'test@test.com',
        'password': 'password123'
    }, follow_redirects=True)

    assert response.status_code == 200
```

#### 5.2 程式碼品質

**使用 Black 格式化**:
```bash
black app/
```

**使用 Flake8 檢查**:
```bash
flake8 app/ --max-line-length=120
```

---

## 五、除錯技巧

### 5.1 Flask Debug Mode

```python
# run.py
app.run(debug=True)  # 啟用 debug 模式
```

**功能**:
- 程式碼變更自動重載
- 詳細的錯誤訊息
- 互動式除錯器

### 5.2 PostgreSQL 查詢日誌

```python
# app/config.py
SQLALCHEMY_ECHO = True  # 顯示所有 SQL 查詢
```

### 5.3 使用 Flask Shell

```bash
flask shell

>>> from app.models.user import User
>>> User.query.all()
>>> User.query.filter_by(email='test@test.com').first()
```

---

## 六、常見問題解決

### Q1: 資料庫連接失敗

```bash
# 檢查 PostgreSQL 服務是否運行
# Windows
net start postgresql-x64-16

# 檢查連接字串
echo $DATABASE_URL
```

### Q2: Tailwind CSS 未生效

```bash
# 確認編譯成功
npm run build

# 檢查模板引用路徑
{{ url_for('static', filename='css/output.css') }}
```

### Q3: 虛擬環境問題

```bash
# 刪除舊環境
rm -rf venv

# 重新建立
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

---

## 七、總結

### 完整開發時程（預估）

| 階段 | 天數 | 累計 |
|------|-----|------|
| 環境建置 | 1-2 天 | 2 天 |
| 資料庫實作 | 3-5 天 | 7 天 |
| 後端核心 | 17-25 天 | 32 天 |
| 前端開發 | 13-20 天 | 52 天 |
| 測試優化 | 7-14 天 | 66 天 |

**總計**: 約 2-3 個月

### 下一步

請閱讀：
- [08-deployment-guide.md](./08-deployment-guide.md) - 部署指南
