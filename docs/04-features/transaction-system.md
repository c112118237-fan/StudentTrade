# 交易系統完整說明

> StudentTrade 平台完整交易流程、狀態管理與功能說明

**最後更新**: 2025-12-29
**版本**: v2.0

---

## 📋 目錄

- [功能概述](#功能概述)
- [交易狀態說明](#交易狀態說明)
- [完整交易流程](#完整交易流程)
- [買家操作指南](#買家操作指南)
- [賣家操作指南](#賣家操作指南)
- [爭議處理機制](#爭議處理機制)
- [評價系統](#評價系統)
- [技術實作細節](#技術實作細節)

---

## 功能概述

StudentTrade 平台已完整實作從「商品瀏覽」到「交易完成」的完整流程：

### ✅ 核心功能

1. **商品詳情頁發起交易** - 一鍵發起交易請求
2. **交易狀態管理** - 7 種狀態完整覆蓋
3. **買賣雙方互動** - 接受、拒絕、開始、完成
4. **爭議處理機制** - 保障雙方權益
5. **自動通知系統** - 即時推送交易動態
6. **評價系統整合** - 交易完成後互相評價

### 📊 交易類型

| 類型 | 代碼 | 說明 | 金額 |
|------|------|------|------|
| 🛒 購買 | `sale` | 以金錢購買商品 | 顯示價格（可議價） |
| 🔄 交換 | `exchange` | 以物易物交易 | 預設為 0（可填寫） |
| 🎁 免費索取 | `free` | 賣家免費贈送 | 固定為 0 |

---

## 交易狀態說明

### 狀態總覽

| # | 狀態 | 代碼 | 說明 | 顏色 | 類型 |
|---|------|------|------|------|------|
| 1 | 待回應 | `pending` | 買家發起交易，等待賣家回應 | 🟡 黃色 | 進行中 |
| 2 | 已接受 | `accepted` | 賣家接受交易，可開始進行 | 🔵 藍色 | 進行中 |
| 3 | **進行中** | `in_progress` | 雙方正在進行交易（面交/配送） | 🟣 紫色 | 進行中 |
| 4 | 已完成 | `completed` | 交易成功完成，可互相評價 | 🟢 綠色 | 終態 |
| 5 | 已取消 | `cancelled` | 交易被取消 | ⚫ 灰色 | 終態 |
| 6 | 已拒絕 | `rejected` | 賣家拒絕交易請求 | 🔴 紅色 | 終態 |
| 7 | **爭議中** | `disputed` | 交易有爭議，等待處理 | 🟠 橘色 | 進行中 |

### 狀態轉換流程圖

```
[買家發起] → pending (待回應)
                ↓
        ┌───────┴───────┐
        ↓               ↓
    accepted        rejected ⚫
   (已接受)         (已拒絕)
        ↓
   in_progress
   (進行中) ←─────────┐
        ↓             │
    ┌───┴───┐    cancelled ⚫
    ↓       ↓    (已取消)
completed disputed
(已完成)🟢 (爭議中)🟠
                ↓
        ┌───────┴───────┐
        ↓               ↓
    completed ⚫    cancelled ⚫
```

### 詳細狀態說明

#### 1. pending（待回應）
- **說明**: 買家發起交易請求，等待賣家回應
- **可執行操作**:
  - 👤 **買家**: 取消交易
  - 🏪 **賣家**: 接受交易、拒絕交易

#### 2. accepted（已接受）
- **說明**: 賣家接受交易請求，雙方可開始進行
- **可執行操作**:
  - 👤👥 **雙方**: 開始交易、取消交易、提出爭議

#### 3. in_progress（進行中）⭐ 新增
- **說明**: 交易正在進行中（約定面交、配送中等）
- **可執行操作**:
  - 👤👥 **雙方**: 確認完成、取消交易、提出爭議

#### 4. completed（已完成）
- **說明**: 交易成功完成，雙方可互相評價
- **可執行操作**:
  - 👤 **買家**: 評價賣家
  - 🏪 **賣家**: 評價買家
- **終止狀態**: 交易結束

#### 5. cancelled（已取消）
- **說明**: 交易被取消，商品恢復可販售狀態
- **終止狀態**: 不可再操作

#### 6. rejected（已拒絕）
- **說明**: 賣家拒絕買家的交易請求
- **終止狀態**: 不可再操作

#### 7. disputed（爭議中）⭐ 新增
- **說明**: 交易出現爭議，等待管理員介入處理
- **可執行操作**:
  - 👨‍💼 **管理員**: 解決爭議（完成或取消）

---

## 完整交易流程

### 買家操作指南

#### 步驟 1：瀏覽商品並發起交易

1. **進入商品詳情頁**
   ```
   商品列表 → 點擊商品 → 商品詳情頁
   ```

2. **點擊「發起交易」按鈕**
   - 位置：商品詳情頁右側，價格下方
   - 圖示：💰 帶有金錢圖示
   - **前提條件**:
     - ✅ 必須已登入
     - ✅ 不能是商品擁有者
     - ✅ 商品狀態為 `active`（販售中）

3. **填寫交易表單**

   | 欄位 | 必填 | 說明 |
   |------|------|------|
   | 交易類型 | ✅ | 購買/交換/免費索取 |
   | 交易金額 | 依類型 | 購買：顯示並可議價<br/>交換：預設 0<br/>免費：自動 0 |
   | 備註 | ❌ | 面交地點、時間等 |

   **範例備註**:
   ```
   希望在校門口面交，週三下午可以
   ```

4. **送出交易請求**
   - 點擊「送出請求」
   - 系統自動：
     - 建立交易記錄（狀態 = `pending`）
     - 發送通知給賣家

#### 步驟 2：等待賣家回應

**在「我的交易」頁面查看狀態**：
```
導航欄 → 交易 → 我的購買
```

**可能的結果**：
- ✅ **賣家接受** → 狀態變為 `accepted`
- ❌ **賣家拒絕** → 狀態變為 `rejected`（查看拒絕原因）
- ⏰ **等待中** → 持續為 `pending`

**可執行操作**：
- 取消交易

#### 步驟 3：開始進行交易（賣家接受後）

1. **點擊「開始交易」**
   - 狀態變更：`accepted` → `in_progress`

2. **進行實際交易**
   - 約定面交時間地點
   - 或使用其他交易方式

3. **雙方確認交易狀況**
   - 私訊溝通進度
   - 確認商品狀況

#### 步驟 4：確認完成交易

1. **買家點擊「確認完成」**
   - 確認已收到商品且無問題
   - 狀態變更：`in_progress` → `completed`

2. **評價賣家（可選）**
   - 評分：1-5 星
   - 評論：文字評價

### 賣家操作指南

#### 步驟 1：接收交易通知

**通知方式**：
- 🔔 系統通知（導航欄紅點）
- 📧 郵件通知（若開啟）

**查看交易請求**：
```
導航欄 → 交易 → 我的販售
```

#### 步驟 2：處理交易請求

**查看交易詳情**：
- 買家資訊
- 交易類型和金額
- 買家備註

**可執行操作**：

1. **接受交易** ✅
   - 點擊「接受交易」
   - 狀態：`pending` → `accepted`
   - 通知買家

2. **拒絕交易** ❌
   - 點擊「拒絕交易」
   - 填寫拒絕原因（必填）
   - 狀態：`pending` → `rejected`
   - 通知買家

**範例拒絕原因**：
```
抱歉，商品已在其他平台售出
```

#### 步驟 3：進行交易

1. **開始交易**
   - 與買家協調面交或配送
   - 狀態：`accepted` → `in_progress`

2. **交易中溝通**
   - 使用私訊功能
   - 確認交易細節

#### 步驟 4：完成交易

1. **確認完成**
   - 確認買家已收到商品
   - 點擊「確認完成」
   - 狀態：`in_progress` → `completed`

2. **評價買家（可選）**
   - 評分：1-5 星
   - 評論：買家交易體驗

---

## 爭議處理機制

### 何時使用爭議功能

**適用情況**：
- 商品與描述不符
- 交易過程中出現糾紛
- 一方不履行交易承諾
- 其他需要第三方介入的情況

### 提出爭議流程

1. **點擊「提出爭議」按鈕**
   - 可用狀態：`accepted`, `in_progress`

2. **填寫爭議原因**
   - 詳細描述問題
   - 提供相關證據

3. **提交爭議**
   - 狀態變更：當前狀態 → `disputed`
   - 通知對方和管理員

### 爭議處理結果

**管理員介入後**：
- ✅ **爭議解決，完成交易** → `completed`
- ❌ **爭議解決，取消交易** → `cancelled`

---

## 評價系統

### 評價時機

- **觸發條件**: 交易狀態為 `completed`
- **評價對象**:
  - 👤 買家評價賣家
  - 🏪 賣家評價買家

### 評價內容

| 項目 | 類型 | 必填 | 說明 |
|------|------|------|------|
| 評分 | 1-5 星 | ✅ | 整體滿意度 |
| 評論 | 文字 | ❌ | 詳細評價內容 |

### 評價規則

- ✅ 每筆交易只能評價一次
- ✅ 評價後不可修改（請謹慎評價）
- ✅ 評價會影響使用者信譽分數
- ✅ 評價可被其他使用者查看

---

## 技術實作細節

### 資料庫設計

**Transactions 表結構**：

```sql
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products(id),
    buyer_id INTEGER NOT NULL REFERENCES users(id),
    seller_id INTEGER NOT NULL REFERENCES users(id),
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    amount NUMERIC(10, 2) NOT NULL,
    transaction_type VARCHAR(20) NOT NULL,
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP,
    CONSTRAINT chk_status CHECK (status IN (
        'pending', 'accepted', 'in_progress',
        'completed', 'cancelled', 'rejected', 'disputed'
    )),
    CONSTRAINT chk_type CHECK (transaction_type IN (
        'sale', 'exchange', 'free'
    ))
);
```

### 狀態轉換規則（程式碼）

**Transaction Model** (`app/models/transaction.py`):

```python
class Transaction(db.Model):
    # 狀態常數
    STATUS_PENDING = 'pending'
    STATUS_ACCEPTED = 'accepted'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELLED = 'cancelled'
    STATUS_REJECTED = 'rejected'
    STATUS_DISPUTED = 'disputed'

    # 狀態檢查方法
    def can_accept(self):
        return self.status == self.STATUS_PENDING

    def can_reject(self):
        return self.status == self.STATUS_PENDING

    def can_start_progress(self):
        return self.status == self.STATUS_ACCEPTED

    def can_complete(self):
        return self.status == self.STATUS_IN_PROGRESS

    def can_cancel(self):
        return self.status not in [
            self.STATUS_COMPLETED,
            self.STATUS_CANCELLED,
            self.STATUS_REJECTED
        ]

    def can_dispute(self):
        return self.status in [
            self.STATUS_ACCEPTED,
            self.STATUS_IN_PROGRESS
        ]
```

### API 端點

| 方法 | 端點 | 說明 |
|------|------|------|
| POST | `/transactions/create/<product_id>` | 發起交易 |
| POST | `/transactions/<id>/accept` | 接受交易 |
| POST | `/transactions/<id>/reject` | 拒絕交易 |
| POST | `/transactions/<id>/start` | 開始交易 |
| POST | `/transactions/<id>/complete` | 完成交易 |
| POST | `/transactions/<id>/cancel` | 取消交易 |
| POST | `/transactions/<id>/dispute` | 提出爭議 |

### 自動通知

**觸發通知的事件**：

| 事件 | 接收者 | 通知類型 |
|------|--------|---------|
| 發起交易 | 賣家 | `transaction_request` |
| 接受交易 | 買家 | `transaction_accepted` |
| 拒絕交易 | 買家 | `transaction_rejected` |
| 開始交易 | 對方 | `transaction_started` |
| 完成交易 | 雙方 | `transaction_completed` |
| 取消交易 | 對方 | `transaction_cancelled` |
| 提出爭議 | 對方+管理員 | `transaction_disputed` |

---

## 更新歷史

### v2.0 (2025-12-29)
- 📝 重新整理文檔結構
- 📚 合併交易相關文檔
- 🎨 優化排版和導航

### v1.2 (2024-12-22)
- ✨ 新增 `in_progress` 狀態
- ✨ 新增 `disputed` 爭議處理狀態
- 🔧 完善狀態轉換邏輯
- 📱 優化交易詳情頁面

### v1.0 (2024-11)
- 🎉 初始版本發布
- ✅ 基礎交易功能實作

---

## 相關文檔

- [資料庫設計](../02-database/database-design.md) - Transactions 表詳細設計
- [API 規範](../03-api/api-specification.md) - 交易相關 API
- [系統架構](../01-design/system-architecture.md) - 整體架構說明

---

**維護團隊**: StudentTrade 開發組
**問題回報**: [GitHub Issues](https://github.com/...)
