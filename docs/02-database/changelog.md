# 資料庫變更日誌 (Database Changelog)

本文件記錄 StudentTrade 資料庫架構的所有重要變更。

---

## 版本 v1.2 (2025-12-29)

### 🆕 新增欄位

#### USERS 表
- `department` (VARCHAR(120)) - 系所資訊
- `bio` (TEXT) - 個人簡介
- `is_verified` (BOOLEAN, DEFAULT FALSE) - 郵件驗證狀態
- `is_deleted` (BOOLEAN, DEFAULT FALSE) - 軟刪除標記
- `last_login` (TIMESTAMP) - 最後登入時間

#### PRODUCTS 表
- `location` (VARCHAR(200)) - 交易地點
- `transaction_method` (VARCHAR(200)) - 交易方式（面交/郵寄/其他）

### 🔄 修改內容

#### TRANSACTIONS 表

**新增狀態值**：
- `in_progress` - 交易進行中（在 accepted 和 completed 之間）
- `disputed` - 爭議中（處理交易糾紛）

**交易類型變更**：
- `purchase` → `sale`（語義更清晰）
- 新增 `free` 類型（免費贈送）

**完整狀態清單**：
```
pending → accepted → in_progress → completed
             ↓           ↓
          rejected    disputed
             ↓
          cancelled
```

**完整類型清單**：
- `sale` - 買賣交易
- `exchange` - 物品交換
- `free` - 免費贈送

### 📊 資料庫統計

| 資料表 | 欄位數 | 主要變更 |
|--------|--------|---------|
| users | 15 | +5 欄位（從 10 → 15） |
| products | 14 | +2 欄位（從 12 → 14） |
| transactions | 10 | +2 狀態值，交易類型重命名 |
| categories | 6 | 無變更 |
| product_images | 6 | 無變更 |
| messages | 7 | 無變更 |
| notifications | 7 | 無變更 |
| reviews | 7 | 無變更 |

### 🔧 遷移指令

如需從舊版本升級，執行以下命令：

```bash
# 更新交易類型（如果有舊資料）
psql -U studenttrade_user -d studenttrade -c "UPDATE transactions SET transaction_type = 'sale' WHERE transaction_type = 'purchase';"

# 使用 Flask-Migrate 進行資料庫遷移
flask db migrate -m "v1.2: Add user profile fields and product location"
flask db upgrade
```

### 📝 受影響的文件

- [app/models/user.py](../app/models/user.py) - User 模型更新
- [app/models/product.py](../app/models/product.py) - Product 模型更新
- [app/models/transaction.py](../app/models/transaction.py) - Transaction 狀態和類型更新
- [sql/web_schema.sql](../sql/web_schema.sql) - 完整 Schema 檔案
- [docs/03-database-design.md](./03-database-design.md) - 資料庫設計文檔

---

## 版本 v1.1 (2024-12)

### 功能完善

#### 交易功能強化
- 完整的交易狀態管理
- 交易歷史記錄
- 評價系統整合

#### 通知系統
- 即時通知推送
- 未讀通知計數
- 多種通知類型支援

#### 訊息系統
- WebSocket 實時訊息
- 訊息已讀標記
- 對話記錄管理

---

## 版本 v1.0 (2024-11)

### 初始版本

建立 8 張核心資料表：

1. **users** - 使用者資料
2. **categories** - 商品分類
3. **products** - 商品資料
4. **product_images** - 商品圖片
5. **transactions** - 交易記錄
6. **messages** - 私訊系統
7. **notifications** - 通知系統
8. **reviews** - 評價系統

### 基礎功能

- 使用者註冊與登入
- 商品上架與瀏覽
- 交易請求與管理
- 私訊功能
- 評價機制

### 技術規格

- **資料庫**: PostgreSQL 16
- **ORM**: Flask-SQLAlchemy
- **遷移工具**: Flask-Migrate
- **編碼**: UTF-8
- **時區**: Asia/Taipei (UTC+8)

---

## 資料庫設計原則

### 命名規範
- 資料表名稱：小寫複數（users, products）
- 欄位名稱：小寫 + 底線分隔（created_at, user_id）
- 外鍵欄位：關聯表名 + _id（user_id, product_id）

### 約束規範
- 所有主鍵使用 SERIAL 自動遞增
- 所有資料表包含 created_at 時間戳記
- 重要資料表包含 updated_at 並自動更新
- 使用外鍵確保資料完整性
- 適當的 CHECK 約束驗證資料有效性

### 索引策略
- 主鍵自動建立索引
- 外鍵欄位建立索引
- 常用查詢欄位建立索引（status, created_at 等）
- 未讀訊息/通知使用部分索引（WHERE is_read = FALSE）

---

## 查看詳細資訊

- 完整資料庫設計：[docs/03-database-design.md](./03-database-design.md)
- 實際 Schema 檔案：[sql/web_schema.sql](../sql/web_schema.sql)
- 資料庫模型：[app/models/](../app/models/)

---

**最後更新**: 2025-12-29
**目前版本**: v1.2
**維護者**: StudentTrade 開發團隊
