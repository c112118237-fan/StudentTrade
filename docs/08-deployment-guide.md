# StudentTrade 部署指南

## 一、部署概述

### 1.1 部署環境

本指南涵蓋三種部署環境：

| 環境 | 用途 | 部署平台 |
|------|------|---------|
| **開發環境** | 本地開發測試 | localhost |
| **測試環境** | 整合測試、UAT | Heroku / Railway（免費方案） |
| **生產環境** | 正式上線 | Railway / PythonAnywhere / AWS |

### 1.2 部署架構

```mermaid
graph TB
    User[使用者]
    User --> Nginx[Nginx<br/>反向代理]
    Nginx --> Gunicorn[Gunicorn<br/>WSGI Server]
    Gunicorn --> Flask[Flask<br/>Application]
    Flask --> DB[(PostgreSQL<br/>Database)]
    Flask --> Files[靜態檔案<br/>Static/Uploads]

    style Nginx fill:#4CAF50,color:#fff
    style Gunicorn fill:#2196F3,color:#fff
    style Flask fill:#FF9800,color:#fff
    style DB fill:#9C27B0,color:#fff
```

---

## 二、生產環境準備

### 2.1 生產配置

**建立生產配置檔**:
```python
# app/config.py

class ProductionConfig(Config):
    """生產環境配置"""
    DEBUG = False
    TESTING = False
    SQLALCHEMY_ECHO = False

    # 使用環境變數
    SECRET_KEY = os.environ.get('SECRET_KEY')
    DATABASE_URL = os.environ.get('DATABASE_URL')

    # 安全性設定
    SESSION_COOKIE_SECURE = True  # HTTPS only
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # CSRF 保護
    WTF_CSRF_ENABLED = True
```

### 2.2 環境變數

**生產環境 .env**:
```bash
# .env.production

FLASK_ENV=production
SECRET_KEY=<use-a-strong-random-key>
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# 安全性
HTTPS_ONLY=true

# 效能
WORKERS=4
THREADS=2
```

### 2.3 依賴檔案

**requirements.txt（生產）**:
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
gunicorn==21.2.0
```

---

## 三、Railway 部署（推薦）

### 3.1 Railway 簡介

**優勢**:
- ✅ 免費額度（每月 $5 credit）
- ✅ 自動從 Git 部署
- ✅ 內建 PostgreSQL
- ✅ 簡單易用
- ✅ 支援自訂域名

### 3.2 部署步驟

**步驟 1: 建立 Railway 帳號**
1. 前往 https://railway.app/
2. 使用 GitHub 帳號登入
3. 授權 Railway 存取 GitHub

**步驟 2: 建立專案與服務**

```bash
# 安裝 Railway CLI（可選）
npm install -g @railway/cli

# 登入
railway login

# 初始化專案
railway init

# 連結到 Railway 專案
railway link
```

**步驟 3: 新增 PostgreSQL**
1. 在 Railway Dashboard 點選 "New Service"
2. 選擇 "Database" → "PostgreSQL"
3. 等待資料庫建立完成
4. 複製 `DATABASE_URL`

**步驟 4: 配置環境變數**
1. 進入專案設定
2. Variables 頁籤
3. 新增環境變數：
   ```
   SECRET_KEY=<your-secret-key>
   DATABASE_URL=${{Postgres.DATABASE_URL}}
   FLASK_ENV=production
   ```

**步驟 5: 建立必要檔案**

**Procfile**:
```
web: gunicorn run:app
release: flask db upgrade
```

**runtime.txt**:
```
python-3.11.6
```

**railway.json**:
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "gunicorn run:app",
    "healthcheckPath": "/",
    "healthcheckTimeout": 100
  }
}
```

**步驟 6: 部署**

```bash
# 提交變更
git add .
git commit -m "Prepare for Railway deployment"
git push origin main

# Railway 會自動偵測並部署
```

**步驟 7: 執行資料庫遷移**

```bash
# 使用 Railway CLI
railway run flask db upgrade

# 或在 Railway Dashboard 的 Settings → Deploy → Custom Start Command
# 設定 release 命令
```

**步驟 8: 訪問應用**
```
https://your-app-name.railway.app
```

---

## 四、Heroku 部署（替代方案）

### 4.1 Heroku 部署步驟

**步驟 1: 安裝 Heroku CLI**
```bash
# Windows
winget install Heroku.HerokuCLI

# macOS
brew tap heroku/brew && brew install heroku

# 登入
heroku login
```

**步驟 2: 建立 Heroku 應用**
```bash
# 建立應用
heroku create studenttrade-app

# 新增 PostgreSQL
heroku addons:create heroku-postgresql:mini
```

**步驟 3: 配置環境變數**
```bash
heroku config:set SECRET_KEY=your-secret-key
heroku config:set FLASK_ENV=production
```

**步驟 4: 部署**
```bash
git push heroku main
```

**步驟 5: 執行資料庫遷移**
```bash
heroku run flask db upgrade
```

**步驟 6: 開啟應用**
```bash
heroku open
```

---

## 五、使用 Gunicorn（WSGI Server）

### 5.1 Gunicorn 配置

**gunicorn.conf.py**:
```python
# gunicorn.conf.py

import multiprocessing

# Server Socket
bind = '0.0.0.0:8000'
backlog = 2048

# Worker Processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync'
worker_connections = 1000
timeout = 30
keepalive = 2

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'

# Process Naming
proc_name = 'studenttrade'

# Server Mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (如果使用)
# keyfile = '/path/to/keyfile'
# certfile = '/path/to/certfile'
```

### 5.2 啟動 Gunicorn

```bash
# 基本啟動
gunicorn run:app

# 使用配置檔
gunicorn -c gunicorn.conf.py run:app

# 指定 workers 和 threads
gunicorn --workers 4 --threads 2 --bind 0.0.0.0:8000 run:app
```

---

## 六、使用 Nginx（反向代理）

### 6.1 安裝 Nginx

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install nginx

# CentOS/RHEL
sudo yum install nginx

# macOS
brew install nginx
```

### 6.2 Nginx 配置

**/etc/nginx/sites-available/studenttrade**:
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # 靜態檔案
    location /static {
        alias /path/to/StudentTrade/app/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /uploads {
        alias /path/to/StudentTrade/app/static/uploads;
        expires 30d;
    }

    # 代理到 Gunicorn
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support (if needed)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # 檔案上傳大小限制
    client_max_body_size 5M;
}
```

### 6.3 啟用站點

```bash
# 建立符號連結
sudo ln -s /etc/nginx/sites-available/studenttrade /etc/nginx/sites-enabled/

# 測試配置
sudo nginx -t

# 重新載入 Nginx
sudo systemctl reload nginx
```

### 6.4 SSL/HTTPS（Let's Encrypt）

```bash
# 安裝 Certbot
sudo apt install certbot python3-certbot-nginx

# 取得憑證
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# 自動更新（cron job）
sudo certbot renew --dry-run
```

**Nginx 配置會自動更新為 HTTPS**:
```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # ... 其他配置
}

# HTTP 轉 HTTPS
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

---

## 七、使用 Systemd（服務管理）

### 7.1 建立 Systemd Service

**/etc/systemd/system/studenttrade.service**:
```ini
[Unit]
Description=StudentTrade Flask Application
After=network.target postgresql.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/StudentTrade
Environment="PATH=/path/to/StudentTrade/venv/bin"
ExecStart=/path/to/StudentTrade/venv/bin/gunicorn -c gunicorn.conf.py run:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 7.2 管理服務

```bash
# 重新載入 systemd
sudo systemctl daemon-reload

# 啟動服務
sudo systemctl start studenttrade

# 開機自動啟動
sudo systemctl enable studenttrade

# 查看狀態
sudo systemctl status studenttrade

# 查看日誌
sudo journalctl -u studenttrade -f
```

---

## 八、資料庫遷移與備份

### 8.1 生產環境資料庫遷移

```bash
# 在生產伺服器上
source venv/bin/activate

# 執行遷移
flask db upgrade

# 如果需要回滾
flask db downgrade
```

### 8.2 資料庫備份

**自動備份腳本**:
```bash
#!/bin/bash
# scripts/backup_db.sh

BACKUP_DIR="/path/to/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="studenttrade"

# 建立備份
pg_dump -U postgres $DB_NAME > "$BACKUP_DIR/backup_$DATE.sql"

# 壓縮
gzip "$BACKUP_DIR/backup_$DATE.sql"

# 刪除 30 天前的備份
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +30 -delete

echo "Backup completed: backup_$DATE.sql.gz"
```

**設定 Cron Job**:
```bash
# 每天凌晨 2 點備份
0 2 * * * /path/to/scripts/backup_db.sh
```

### 8.3 資料庫恢復

```bash
# 從備份恢復
gunzip backup_20241129_020000.sql.gz
psql -U postgres studenttrade < backup_20241129_020000.sql
```

---

## 九、效能優化

### 9.1 靜態檔案 CDN（可選）

使用 Cloudflare 或 AWS CloudFront 加速靜態資源。

### 9.2 快取策略

```python
# 使用 Flask-Caching
from flask_caching import Cache

cache = Cache(config={'CACHE_TYPE': 'simple'})

@cache.cached(timeout=300)
def get_popular_products():
    return Product.query.order_by(Product.view_count.desc()).limit(10).all()
```

### 9.3 資料庫索引

確保已建立適當的索引（參考 03-database-design.md）。

### 9.4 Gunicorn Worker 調整

```bash
# CPU 密集：workers = (CPU * 2) + 1
gunicorn --workers 5 --threads 2 run:app

# I/O 密集：使用 async workers
gunicorn --workers 4 --worker-class gevent run:app
```

---

## 十、監控與日誌

### 10.1 應用日誌

```python
# app/__init__.py

import logging
from logging.handlers import RotatingFileHandler

def setup_logging(app):
    if not app.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')

        file_handler = RotatingFileHandler(
            'logs/studenttrade.log',
            maxBytes=10240000,  # 10MB
            backupCount=10
        )

        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))

        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('StudentTrade startup')
```

### 10.2 錯誤追蹤（Sentry）

```bash
pip install sentry-sdk[flask]
```

```python
# app/__init__.py

import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[FlaskIntegration()],
    traces_sample_rate=1.0
)
```

---

## 十一、安全性檢查清單

### 11.1 部署前檢查

- [ ] DEBUG = False
- [ ] SECRET_KEY 使用強隨機值
- [ ] 資料庫密碼強度足夠
- [ ] HTTPS 啟用（SSL 憑證）
- [ ] CSRF 保護啟用
- [ ] Session Cookie 設定安全
- [ ] SQL 注入防護（使用 ORM）
- [ ] XSS 防護（Jinja2 自動跳脫）
- [ ] 檔案上傳驗證
- [ ] 敏感資料不出現在日誌
- [ ] .env 檔案不提交到 Git
- [ ] 定期更新依賴套件

### 11.2 安全標頭

```python
# app/__init__.py

@app.after_request
def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response
```

---

## 十二、部署流程圖

```mermaid
flowchart TD
    Start([開始部署]) --> PrepCode[準備程式碼]
    PrepCode --> CreateEnv[建立生產環境變數]
    CreateEnv --> SetupDB[設置 PostgreSQL]
    SetupDB --> RunMigration[執行資料庫遷移]
    RunMigration --> CollectStatic[編譯靜態資源]

    CollectStatic --> DeployMethod{部署方式?}

    DeployMethod -->|PaaS| Railway[Railway/Heroku]
    DeployMethod -->|VPS| VPS[VPS 部署]

    Railway --> PushGit[推送到 Git]
    PushGit --> AutoDeploy[自動部署]

    VPS --> SetupServer[設置伺服器]
    SetupServer --> InstallDeps[安裝依賴]
    InstallDeps --> ConfigNginx[配置 Nginx]
    ConfigNginx --> StartGunicorn[啟動 Gunicorn]
    StartGunicorn --> SetupSSL[設置 SSL]

    AutoDeploy --> Test[測試應用]
    SetupSSL --> Test

    Test --> TestOK{測試通過?}
    TestOK -->|否| Debug[除錯]
    Debug --> PrepCode

    TestOK -->|是| Monitor[設置監控]
    Monitor --> Done([部署完成])

    style Start fill:#4CAF50,color:#fff
    style Done fill:#4CAF50,color:#fff
    style TestOK fill:#FFF9C4
```

---

## 十三、總結

### 13.1 推薦部署方式

**適合學生專題**:
1. **Railway**（推薦）- 免費、簡單、功能完整
2. **Heroku** - 知名、文檔豐富
3. **PythonAnywhere** - 適合 Python 應用

**適合正式產品**:
1. **VPS (Digital Ocean, Linode)** - 完全控制
2. **AWS / GCP** - 企業級

### 13.2 部署檢查清單

- [ ] 程式碼推送到 GitHub
- [ ] 環境變數配置完成
- [ ] 資料庫建立並遷移
- [ ] 靜態資源編譯
- [ ] Gunicorn 正常運行
- [ ] Nginx 配置（如使用）
- [ ] HTTPS 啟用
- [ ] 日誌系統設置
- [ ] 備份機制建立
- [ ] 監控告警設置
- [ ] 效能測試通過
- [ ] 安全性檢查通過

### 13.3 參考資源

- [Railway Documentation](https://docs.railway.app/)
- [Flask Deployment](https://flask.palletsprojects.com/en/3.0.x/deploying/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Let's Encrypt](https://letsencrypt.org/)

---

**恭喜！您已完成 StudentTrade 的完整部署流程。**
