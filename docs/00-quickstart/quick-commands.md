# 快速命令參考

## 🚀 啟動專案

```bash
# 啟動 Docker 容器（開發環境）
docker-compose up -d --build

# 初始化資料庫 Schema
docker compose exec web python apply_sql_schema.py

# 或使用 init_db.py（包含初始資料）
docker compose exec web python init_db.py
```

## 📊 資料庫管理

```bash
# 連接到資料庫
docker compose exec db psql -U studenttrade_user -d studenttrade

# 查看資料庫狀態
docker compose exec web flask db current

# 建立遷移檔案
docker compose exec web flask db migrate -m "描述訊息"

# 執行遷移
docker compose exec web flask db upgrade

# 回滾遷移
docker compose exec web flask db downgrade

# 備份資料庫
docker compose exec db pg_dump -U studenttrade_user studenttrade > backup_$(date +%Y%m%d).sql

# 恢復資料庫
docker compose exec -T db psql -U studenttrade_user studenttrade < backup_20241229.sql
```

## 🔍 檢查與除錯

```bash
# 查看容器日誌
docker compose logs -f web

# 查看資料庫日誌
docker compose logs -f db

# 進入 Web 容器
docker compose exec web bash

# 進入資料庫容器
docker compose exec db bash

# 檢查 Python 環境
docker compose exec web python --version

# 檢查已安裝套件
docker compose exec web pip list
```

## 🛠️ 開發工具

```bash
# 執行 Python Shell
docker compose exec web flask shell

# 執行測試
docker compose exec web pytest

# 程式碼格式化
docker compose exec web black app/

# 檢查程式碼品質
docker compose exec web flake8 app/
```

## 🧹 清理與重置

```bash
# 停止容器
docker compose down

# 停止並刪除 volumes（注意：會刪除資料庫資料）
docker compose down -v

# 重建容器
docker compose up -d --build --force-recreate

# 清理未使用的 Docker 資源
docker system prune -a
```

## 📝 資料庫查詢範例

```sql
-- 查看所有資料表
\dt

-- 查看特定資料表結構
\d users

-- 查看所有使用者
SELECT id, username, email, created_at FROM users;

-- 查看商品統計
SELECT status, COUNT(*) FROM products GROUP BY status;

-- 查看交易狀態統計
SELECT status, COUNT(*) FROM transactions GROUP BY status;

-- 查看最新的 10 個商品
SELECT id, title, price, created_at FROM products ORDER BY created_at DESC LIMIT 10;
```

## 🌐 訪問應用

- **Web 應用**: http://localhost:5000
- **PostgreSQL**: localhost:5432
  - 使用者: studenttrade_user
  - 資料庫: studenttrade

## 📚 相關文檔

- [資料庫設計](./03-database-design.md) - 完整資料庫設計文檔
- [資料庫變更日誌](./DATABASE_CHANGELOG.md) - 資料庫更新歷史
- [開發指南](./07-development-guide.md) - 開發環境設置
- [部署指南](./08-deployment-guide.md) - 生產環境部署