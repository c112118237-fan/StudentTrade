# StudentTrade 後端實作說明

## 專案概述

StudentTrade 是一個校園二手交易平台，使用 Flask 3.0 + PostgreSQL 16 構建，採用 Docker 容器化部署。

## 技術架構

### 後端技術棧
- **框架**: Flask 3.0.0
- **資料庫**: PostgreSQL 16
- **ORM**: SQLAlchemy 3.1.1
- **認證**: Flask-Login 0.6.3
- **遷移**: Flask-Migrate 4.0.5
- **圖片處理**: Pillow 10.1.0
- **容器化**: Docker + Docker Compose

### 專案結構
```
StudentTrade/
├── app/
│   ├── __init__.py              # App Factory
│   ├── config.py                # 配置類別
│   ├── extensions.py            # Flask 擴展
│   ├── models/                  # 資料庫模型（8 個）
│   │   ├── user.py              # 使用者模型
│   │   ├── category.py          # 分類模型
│   │   ├── product.py           # 商品模型
│   │   ├── product_image.py     # 商品圖片模型
│   │   ├── transaction.py       # 交易模型
│   │   ├── message.py           # 訊息模型
│   │   ├── notification.py      # 通知模型
│   │   └── review.py            # 評價模型
│   ├── routes/                  # 路由藍圖（6 個）
│   │   ├── auth.py              # 認證路由
│   │   ├── products.py          # 商品路由
│   │   ├── transactions.py      # 交易路由
│   │   ├── messages.py          # 訊息路由
│   │   ├── reviews.py           # 評價路由
│   │   └── notifications.py     # 通知路由
│   ├── services/                # 業務邏輯層
│   │   ├── auth_service.py      # 認證服務
│   │   ├── product_service.py   # 商品服務
│   │   ├── transaction_service.py  # 交易服務
│   │   ├── message_service.py   # 訊息服務
│   │   └── notification_service.py # 通知/評價服務
│   ├── utils/                   # 工具函數
│   │   ├── validators.py        # 驗證器
│   │   ├── decorators.py        # 裝飾器
│   │   ├── helpers.py           # 輔助函數
│   │   └── file_upload.py       # 檔案上傳服務
│   ├── static/                  # 靜態檔案
│   │   └── uploads/             # 上傳檔案目錄
│   │       ├── products/        # 商品圖片
│   │       └── avatars/         # 使用者頭像
│   └── templates/               # Jinja2 模板（24 個）
├── Dockerfile                   # Docker 映像檔
├── docker-compose.yml           # Docker Compose 配置
├── requirements.txt             # Python 依賴
├── run.py                       # 應用入口
├── init_db.py                   # 資料庫初始化腳本
└── .env.example                 # 環境變數範例
```

## 快速開始

### 1. 使用 Docker 部署（推薦）

```bash
# 1. 複製環境變數範例
cp .env.example .env

# 2. 啟動 Docker 容器
docker-compose up -d

# 3. 初始化資料庫
docker-compose exec web python init_db.py

# 4. 訪問應用
# http://localhost:5000
```

### 2. 本地開發環境

```bash
# 1. 建立虛擬環境（Python 3.10）
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 2. 安裝依賴
pip install -r requirements.txt

# 3. 確保 PostgreSQL 16 正在運行
# 並在 .env 中設定 DATABASE_URL

# 4. 初始化資料庫
python init_db.py

# 5. 啟動應用
python run.py
```

## API 端點總覽

### 認證系統（4 個端點）
- `GET/POST /auth/register` - 使用者註冊
- `GET/POST /auth/login` - 使用者登入
- `GET /auth/logout` - 使用者登出
- `GET/POST /auth/profile` - 個人資料管理

### 商品管理（7 個端點）
- `GET /` 或 `/products` - 商品列表（首頁）
- `GET /products/<id>` - 商品詳情
- `GET/POST /products/new` - 刊登商品
- `GET/POST /products/<id>/edit` - 編輯商品
- `POST /products/<id>/delete` - 刪除商品
- `GET /my-products` - 我的商品列表

### 交易系統（7 個端點）
- `GET /transactions` - 交易列表
- `GET /transactions/<id>` - 交易詳情
- `POST /transactions/create` - 發起交易
- `POST /transactions/<id>/accept` - 接受交易
- `POST /transactions/<id>/reject` - 拒絕交易
- `POST /transactions/<id>/complete` - 完成交易
- `POST /transactions/<id>/cancel` - 取消交易

### 訊息系統（4 個端點）
- `GET /messages` - 訊息列表
- `GET /messages/<user_id>` - 對話詳情
- `POST /messages/send` - 發送訊息
- `POST /messages/<id>/read` - 標記已讀

### 評價系統（2 個端點）
- `GET/POST /reviews/new/<transaction_id>` - 提交評價
- `GET /reviews/users/<user_id>` - 查看使用者評價

### 通知系統（4 個端點）
- `GET /notifications` - 通知列表
- `POST /notifications/<id>/read` - 標記已讀
- `POST /notifications/read-all` - 全部標記已讀
- `POST /notifications/<id>/delete` - 刪除通知

## 核心功能實作

### 1. 認證系統
- 學校信箱驗證（必須 .edu 或 .edu.tw）
- 密碼強度驗證（至少 8 字元、包含數字和字母）
- Flask-Login 整合（Session 管理）
- 個人資料管理（頭像上傳、資料編輯）

### 2. 商品管理
- CRUD 操作（建立、讀取、更新、刪除）
- 多圖片上傳（最多 5 張，自動壓縮）
- 搜尋功能（關鍵字、分類、價格區間）
- 分頁顯示（每頁 12 個商品）
- 瀏覽次數統計

### 3. 交易系統
- 交易請求/接受/拒絕流程
- 交易狀態管理（pending, accepted, completed, cancelled）
- 商品狀態自動更新
- 交易完成後可評價

### 4. 訊息系統
- 即時私訊功能
- 對話列表（顯示最後一則訊息）
- 未讀訊息計數
- AJAX 支援（可用於即時更新）

### 5. 評價系統
- 1-5 星評分
- 評論內容
- 評價統計（平均分、總數、分布）
- 只有交易雙方可評價

### 6. 通知系統
- 自動通知（交易請求、訊息、評價等）
- 未讀通知計數
- 通知類型分類

## 資料庫設計

### 8 個資料表
1. **users** - 使用者
2. **categories** - 商品分類
3. **products** - 商品
4. **product_images** - 商品圖片
5. **transactions** - 交易
6. **messages** - 訊息
7. **notifications** - 通知
8. **reviews** - 評價

### 關聯關係
- User 1:N Products（一個使用者有多個商品）
- Product 1:N ProductImages（一個商品有多張圖片）
- Transaction N:1 Product（多個交易指向一個商品）
- Transaction 1:N Reviews（一個交易有兩個評價）
- User 1:N Messages（一個使用者發送/接收多則訊息）
- User 1:N Notifications（一個使用者有多個通知）

## 環境變數設定

```env
# .env 檔案範例
DATABASE_URL=postgresql://studenttrade:studenttrade123@db:5432/studenttrade
SECRET_KEY=your-secret-key-here
FLASK_ENV=development
```

## Docker 配置

### 服務說明
- **web**: Flask 應用（Port 5000）
- **db**: PostgreSQL 16（Port 5432）
- **postgres_data**: 持久化資料卷

### 常用命令
```bash
# 啟動服務
docker-compose up -d

# 查看日誌
docker-compose logs -f web

# 停止服務
docker-compose down

# 重新構建
docker-compose up -d --build

# 進入容器
docker-compose exec web bash
docker-compose exec db psql -U studenttrade
```

## 安全性考量

### 已實作的安全措施
1. **密碼雜湊**: 使用 werkzeug.security（bcrypt）
2. **CSRF 保護**: Flask-WTF CSRF tokens
3. **SQL 注入防護**: SQLAlchemy ORM
4. **檔案上傳驗證**: 檔案類型、大小限制
5. **權限控制**: 裝飾器驗證擁有權
6. **輸入驗證**: 完整的表單驗證

### 建議改進
1. 實作 Rate Limiting（防止暴力破解）
2. 加入 HTTPS（生產環境）
3. 實作信箱驗證流程
4. 加入 reCAPTCHA（防止機器人）
5. 檔案上傳掃毒

## 效能優化

### 已實作
1. **資料庫索引**: email, category_id 等常查詢欄位
2. **圖片壓縮**: Pillow 自動壓縮（品質 85）
3. **分頁查詢**: 避免一次載入大量資料
4. **Lazy Loading**: SQLAlchemy relationship lazy='dynamic'

### 建議改進
1. Redis 快取（熱門商品、使用者 session）
2. CDN（靜態檔案、圖片）
3. 資料庫連接池配置
4. 非同步任務（Celery）

## 測試

目前尚未實作測試（按照使用者要求）。建議未來加入：
- 單元測試（pytest）
- 整合測試
- API 測試

## 部署到生產環境

### 建議步驟
1. 設定環境變數（SECRET_KEY、DATABASE_URL）
2. 使用 Gunicorn + Nginx
3. 設定 HTTPS（Let's Encrypt）
4. 配置防火牆
5. 設定自動備份

### Gunicorn 範例
```bash
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
```

## 故障排除

### 常見問題

**問題 1**: 資料庫連接失敗
```bash
# 檢查 PostgreSQL 是否運行
docker-compose ps
# 檢查連接字串
echo $DATABASE_URL
```

**問題 2**: 圖片上傳失敗
```bash
# 確保上傳目錄存在且有寫入權限
mkdir -p app/static/uploads/products
mkdir -p app/static/uploads/avatars
chmod 755 app/static/uploads
```

**問題 3**: 模組找不到
```bash
# 重新安裝依賴
pip install -r requirements.txt
```

## 授權

本專案為學校作業專案，僅供學習使用。

## 聯絡資訊

如有問題請參考專案文件或聯絡開發團隊。
