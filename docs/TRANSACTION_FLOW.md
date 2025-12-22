# 交易流程說明

## 📋 目錄
- [交易狀態說明](#交易狀態說明)
- [完整交易流程](#完整交易流程)
- [狀態轉換規則](#狀態轉換規則)
- [爭議處理流程](#爭議處理流程)

---

## 交易狀態說明

### 1. pending (待回應)
- **說明**: 買家發起交易請求，等待賣家回應
- **可執行操作**:
  - 買家: 取消交易
  - 賣家: 接受交易、拒絕交易

### 2. accepted (已接受)
- **說明**: 賣家接受交易請求，雙方可以開始進行交易
- **可執行操作**:
  - 買家/賣家: 開始交易、確認完成、提出爭議、取消交易

### 3. in_progress (進行中)
- **說明**: 交易正在進行中（例如：約定面交、配送中）
- **可執行操作**:
  - 買家/賣家: 確認完成、提出爭議、取消交易

### 4. completed (已完成)
- **說明**: 交易成功完成，買賣雙方可以互相評價
- **可執行操作**:
  - 買家: 評價賣家
  - 賣家: 評價買家

### 5. cancelled (已取消)
- **說明**: 交易被取消，商品恢復為可販售狀態
- **終止狀態**: 不可再進行其他操作

### 6. rejected (已拒絕)
- **說明**: 賣家拒絕買家的交易請求，商品恢復為可販售狀態
- **終止狀態**: 不可再進行其他操作

### 7. disputed (爭議中)
- **說明**: 交易出現爭議，等待管理員介入處理
- **可執行操作**:
  - 管理員: 解決爭議（取消交易或強制完成）

---

## 完整交易流程

### 正常交易流程

```
1. 買家發起交易
   ↓
2. [pending] 待賣家回應
   ↓
3. 賣家接受 → [accepted] 已接受
   ↓
4. 雙方開始交易 → [in_progress] 進行中
   ↓
5. 確認完成 → [completed] 已完成
   ↓
6. 雙方互相評價
```

### 快速完成流程

```
1. 買家發起交易
   ↓
2. [pending] 待賣家回應
   ↓
3. 賣家接受 → [accepted] 已接受
   ↓
4. 雙方直接確認完成 → [completed] 已完成
   ↓
5. 雙方互相評價
```

### 取消流程

```
場景 1: 買家在待回應時取消
[pending] → 買家取消 → [cancelled]

場景 2: 賣家拒絕交易
[pending] → 賣家拒絕 → [rejected]

場景 3: 進行中取消
[accepted/in_progress] → 任一方取消 → [cancelled]
```

### 爭議處理流程

```
[accepted/in_progress]
   ↓
買家/賣家提出爭議
   ↓
[disputed] 爭議中
   ↓
管理員處理
   ├─ 取消交易 → [cancelled]
   └─ 強制完成 → [completed]
```

---

## 狀態轉換規則

### 狀態轉換矩陣

| 當前狀態 | 可轉換至 | 操作者 | 說明 |
|---------|---------|--------|------|
| pending | accepted | 賣家 | 接受交易 |
| pending | rejected | 賣家 | 拒絕交易 |
| pending | cancelled | 買家 | 取消交易 |
| accepted | in_progress | 買家/賣家 | 開始進行交易 |
| accepted | completed | 買家/賣家 | 直接完成 |
| accepted | disputed | 買家/賣家 | 提出爭議 |
| accepted | cancelled | 買家/賣家 | 取消交易 |
| in_progress | completed | 買家/賣家 | 確認完成 |
| in_progress | disputed | 買家/賣家 | 提出爭議 |
| in_progress | cancelled | 買家/賣家 | 取消交易 |
| disputed | cancelled | 管理員 | 解決爭議-取消 |
| disputed | completed | 管理員 | 解決爭議-完成 |

### 商品狀態聯動

| 交易狀態變化 | 商品狀態變化 |
|------------|------------|
| 交易建立 (pending) | active → pending |
| 交易完成 (completed) | pending → sold |
| 交易取消/拒絕 (cancelled/rejected) | pending → active |

---

## 爭議處理流程

### 何時可以提出爭議？

- 交易狀態為 `accepted` 或 `in_progress`
- 買家或賣家任一方皆可提出

### 爭議原因範例

**買家可能提出的爭議：**
- 商品與描述不符
- 賣家未依約定交貨
- 商品有瑕疵未事先告知
- 賣家失聯

**賣家可能提出的爭議：**
- 買家未依約付款
- 買家失聯
- 買家惡意退貨

### 管理員處理

1. **審核爭議原因**
   - 查看雙方提供的證據
   - 聯繫雙方了解情況

2. **做出裁決**
   - **取消交易**: 退款給買家，商品恢復販售
   - **強制完成**: 確認交易完成，商品標記為已售出

3. **通知雙方**
   - 系統自動發送通知給買賣雙方
   - 說明處理結果

---

## API 端點說明

### 交易操作端點

| 端點 | 方法 | 說明 | 權限 |
|-----|------|------|------|
| `/transactions/<id>` | GET | 查看交易詳情 | 買家/賣家 |
| `/transactions/create` | POST | 發起交易 | 買家 |
| `/transactions/<id>/accept` | POST | 接受交易 | 賣家 |
| `/transactions/<id>/reject` | POST | 拒絕交易 | 賣家 |
| `/transactions/<id>/start-progress` | POST | 開始交易 | 買家/賣家 |
| `/transactions/<id>/complete` | POST | 完成交易 | 買家/賣家 |
| `/transactions/<id>/cancel` | POST | 取消交易 | 買家/賣家 |
| `/transactions/<id>/dispute` | POST | 提出爭議 | 買家/賣家 |

### Service 方法

```python
# 基本交易操作
TransactionService.create_transaction(product_id, buyer_id, transaction_type, amount, notes)
TransactionService.accept_transaction(transaction_id, seller_id)
TransactionService.reject_transaction(transaction_id, seller_id, reason)
TransactionService.complete_transaction(transaction_id, user_id)
TransactionService.cancel_transaction(transaction_id, user_id, reason)

# 進階功能
TransactionService.start_progress(transaction_id, user_id)
TransactionService.create_dispute(transaction_id, user_id, reason)
TransactionService.resolve_dispute(transaction_id, admin_id, resolution, action)

# 查詢方法
TransactionService.get_transaction_by_id(transaction_id)
TransactionService.get_user_transactions(user_id, role, status, page, per_page)
```

---

## 通知系統

### 自動通知觸發時機

| 事件 | 接收者 | 通知類型 |
|-----|--------|---------|
| 買家發起交易 | 賣家 | transaction_request |
| 賣家接受交易 | 買家 | transaction_accepted |
| 賣家拒絕交易 | 買家 | transaction_rejected |
| 開始進行交易 | 對方 | transaction_in_progress |
| 交易完成 | 對方 | transaction_completed |
| 交易取消 | 對方 | transaction_cancelled |
| 提出爭議 | 對方 | transaction_disputed |
| 爭議已處理 | 雙方 | dispute_resolved |

---

## 注意事項

### 權限控制

- ✅ 只有買家和賣家可以查看交易詳情
- ✅ 只有賣家可以接受/拒絕交易
- ✅ 買賣雙方都可以開始、完成、取消、提出爭議
- ✅ 只有管理員可以解決爭議

### 資料驗證

- ✅ 買家不能購買自己的商品
- ✅ 同一商品不能同時有多個進行中的交易
- ✅ 商品必須處於 `active` 狀態才能發起交易
- ✅ 狀態轉換必須符合規則

### 錯誤處理

- 所有 Service 方法都返回 `(success: bool, result)` 格式
- 失敗時會回傳錯誤訊息
- 資料庫操作失敗會自動 rollback

---

## 未來擴展建議

1. **自動取消機制**
   - pending 狀態超過 7 天自動取消
   - in_progress 狀態超過 30 天自動提醒

2. **交易評分系統**
   - 完成交易後雙方互評
   - 評分影響信用度

3. **交易保障金**
   - 提供第三方託管服務
   - 增加交易安全性

4. **交易聊天室**
   - 專屬的交易溝通頻道
   - 保留溝通記錄作為證據

5. **交易數據分析**
   - 統計用戶的交易成功率
   - 分析常見爭議原因
