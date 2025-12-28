# StudentTrade API 設計文檔

## 一、API 概述

### 1.1 API 設計原則

- **RESTful 架構** - 使用標準 HTTP 方法（GET, POST, PUT, DELETE）
- **語義化 URL** - URL 清晰表達資源關係
- **統一回應格式** - 成功與錯誤回應保持一致
- **狀態碼規範** - 正確使用 HTTP 狀態碼
- **CSRF 保護** - 所有 POST/PUT/DELETE 請求需包含 CSRF Token

### 1.2 技術規格

- **協議**: HTTP/HTTPS
- **格式**: HTML (SSR) + JSON (部分 AJAX)
- **認證**: Session-based (Flask-Login)
- **編碼**: UTF-8

---

## 二、API 路由總覽

### 2.1 路由樹狀圖

```mermaid
graph TD
    Root[/ Flask App]

    Root --> Home[GET / 首頁]
    Root --> Auth[/auth 認證模組]
    Root --> Products[/products 商品模組]
    Root --> Trans[/transactions 交易模組]
    Root --> Msg[/messages 訊息模組]
    Root --> Review[/reviews 評價模組]

    Auth --> AuthRegister[GET/POST /register<br/>註冊]
    Auth --> AuthLogin[GET/POST /login<br/>登入]
    Auth --> AuthLogout[GET /logout<br/>登出]
    Auth --> AuthProfile[GET/POST /profile<br/>個人資料]

    Products --> ProdList[GET /products<br/>商品列表]
    Products --> ProdDetail[GET /products/:id<br/>商品詳情]
    Products --> ProdNew[GET/POST /products/new<br/>刊登商品]
    Products --> ProdEdit[GET/POST /products/:id/edit<br/>編輯商品]
    Products --> ProdDelete[POST /products/:id/delete<br/>刪除商品]
    Products --> MyProds[GET /my-products<br/>我的商品]

    Trans --> TransList[GET /transactions<br/>交易列表]
    Trans --> TransDetail[GET /transactions/:id<br/>交易詳情]
    Trans --> TransCreate[POST /transactions/create<br/>發起交易]
    Trans --> TransAccept[POST /transactions/:id/accept<br/>接受交易]
    Trans --> TransReject[POST /transactions/:id/reject<br/>拒絕交易]
    Trans --> TransComplete[POST /transactions/:id/complete<br/>完成交易]
    Trans --> TransCancel[POST /transactions/:id/cancel<br/>取消交易]

    Msg --> MsgList[GET /messages<br/>訊息列表]
    Msg --> MsgChat[GET /messages/:user_id<br/>對話]
    Msg --> MsgSend[POST /messages/send<br/>發送訊息]
    Msg --> MsgRead[POST /messages/:id/read<br/>標記已讀]

    Review --> ReviewNew[GET/POST /reviews/new/:trans_id<br/>評價]
    Review --> UserReviews[GET /users/:id/reviews<br/>查看評價]

    style Root fill:#4CAF50,color:#fff
    style Auth fill:#2196F3,color:#fff
    style Products fill:#FF9800,color:#fff
    style Trans fill:#9C27B0,color:#fff
    style Msg fill:#F44336,color:#fff
    style Review fill:#009688,color:#fff
```

---

## 三、認證 API（/auth）

### 3.1 使用者註冊

**端點**: `GET/POST /auth/register`
**認證**: 不需要
**用途**: 新使用者註冊

**GET Request - 顯示註冊頁面**:
```
GET /auth/register
```

**Response** (HTML):
- 返回註冊表單頁面 `auth/register.html`

**POST Request - 提交註冊**:
```
POST /auth/register
Content-Type: application/x-www-form-urlencoded

email=test@example.com
username=測試使用者
password=password123
password_confirm=password123
student_id=A12345678
phone=0912345678
```

**Success Response**:
- **Status**: 302 Redirect
- **Location**: `/auth/login`
- **Flash Message**: "註冊成功，請登入"

**Error Response**:
- **Status**: 200 OK
- **Body**: 返回註冊頁面並顯示錯誤訊息
- **錯誤情況**:
  - Email 已被註冊
  - 學號已被註冊
  - 密碼不符合要求
  - 兩次密碼不一致

---

### 3.2 使用者登入

**端點**: `GET/POST /auth/login`
**認證**: 不需要
**用途**: 使用者登入系統

**GET Request**:
```
GET /auth/login
```

**POST Request**:
```
POST /auth/login
Content-Type: application/x-www-form-urlencoded

email=test@example.com
password=password123
remember_me=on
```

**Success Response**:
- **Status**: 302 Redirect
- **Location**: `/` (首頁) 或 `next` 參數指定的頁面
- **Set-Cookie**: `session=...`

**Error Response**:
- **Status**: 200 OK
- **Body**: 登入頁面 + 錯誤訊息
- **錯誤訊息**: "帳號或密碼錯誤"

---

### 3.3 使用者登出

**端點**: `GET /auth/logout`
**認證**: 需要
**用途**: 登出系統

**Request**:
```
GET /auth/logout
```

**Response**:
- **Status**: 302 Redirect
- **Location**: `/`
- **Flash Message**: "已成功登出"

---

### 3.4 個人資料管理

**端點**: `GET/POST /auth/profile`
**認證**: 需要
**用途**: 查看/編輯個人資料

**GET Request**:
```
GET /auth/profile
```

**Response**:
- **Status**: 200 OK
- **Body**: 個人資料頁面 `auth/profile.html`

**POST Request**:
```
POST /auth/profile
Content-Type: multipart/form-data

username=新名稱
phone=0987654321
avatar=<file>
```

**Success Response**:
- **Status**: 302 Redirect
- **Location**: `/auth/profile`
- **Flash Message**: "資料更新成功"

---

## 四、商品 API（/products）

### 4.1 首頁與商品列表

**端點**: `GET /` 或 `GET /products`
**認證**: 不需要
**用途**: 顯示商品列表、支援搜尋與篩選

**Request Parameters**:
```
GET /products?q=電腦&category=3&min_price=100&max_price=5000&condition=良好&page=2
```

| 參數 | 類型 | 必填 | 說明 |
|------|------|-----|------|
| `q` | string | 否 | 搜尋關鍵字 |
| `category` | int | 否 | 分類 ID |
| `min_price` | decimal | 否 | 最低價格 |
| `max_price` | decimal | 否 | 最高價格 |
| `condition` | string | 否 | 商品狀況 |
| `sort` | string | 否 | 排序方式（latest/price_asc/price_desc/popular） |
| `page` | int | 否 | 頁碼（預設 1） |

**Response** (HTML):
- **Status**: 200 OK
- **Body**: 商品列表頁面 `products/index.html`
- **資料**:
  - 商品列表（分頁）
  - 分類列表
  - 篩選條件
  - 分頁資訊

---

### 4.2 商品詳情

**端點**: `GET /products/<id>`
**認證**: 不需要
**用途**: 查看商品詳細資訊

**Request**:
```
GET /products/123
```

**Response** (HTML):
- **Status**: 200 OK
- **Body**: 商品詳情頁面 `products/detail.html`
- **資料**:
  - 商品完整資訊
  - 商品圖片列表
  - 賣家資訊
  - 相關商品推薦

**Error Response**:
- **Status**: 404 Not Found
- **Body**: 錯誤頁面 `errors/404.html`

---

### 4.3 刊登商品

**端點**: `GET/POST /products/new`
**認證**: 需要
**用途**: 刊登新商品

**GET Request**:
```
GET /products/new
```

**Response**:
- **Status**: 200 OK
- **Body**: 商品表單頁面 `products/form.html`

**POST Request**:
```
POST /products/new
Content-Type: multipart/form-data

title=二手 MacBook Pro
description=2020 年購買，狀況良好
price=25000
category_id=3
condition=良好
exchange_preference=可交換 iPad
images[]=<file1>
images[]=<file2>
```

**Success Response**:
- **Status**: 302 Redirect
- **Location**: `/products/<new_product_id>`
- **Flash Message**: "商品刊登成功"

**Error Response**:
- **Status**: 200 OK
- **Body**: 表單頁面 + 錯誤訊息
- **錯誤情況**:
  - 必填欄位未填
  - 價格不合法
  - 圖片格式不支援
  - 圖片檔案過大

---

### 4.4 編輯商品

**端點**: `GET/POST /products/<id>/edit`
**認證**: 需要（且須為商品擁有者）
**用途**: 編輯已刊登商品

**GET Request**:
```
GET /products/123/edit
```

**Response**:
- **Status**: 200 OK
- **Body**: 商品表單頁面（預填資料）

**POST Request**:
```
POST /products/123/edit
Content-Type: multipart/form-data

title=更新的標題
price=20000
...
```

**Success Response**:
- **Status**: 302 Redirect
- **Location**: `/products/123`
- **Flash Message**: "商品更新成功"

**Authorization Error**:
- **Status**: 403 Forbidden
- **Body**: 錯誤頁面
- **Message**: "無權限執行此操作"

---

### 4.5 刪除商品

**端點**: `POST /products/<id>/delete`
**認證**: 需要（且須為商品擁有者）
**用途**: 刪除商品（軟刪除，設定 status='deleted'）

**Request**:
```
POST /products/123/delete
```

**Success Response**:
- **Status**: 302 Redirect
- **Location**: `/my-products`
- **Flash Message**: "商品已刪除"

---

### 4.6 我的商品

**端點**: `GET /my-products`
**認證**: 需要
**用途**: 查看自己刊登的所有商品

**Request**:
```
GET /my-products?status=active&page=1
```

**Response**:
- **Status**: 200 OK
- **Body**: 我的商品頁面 `products/my_products.html`
- **資料**:
  - 我的商品列表（分頁）
  - 商品狀態統計

---

## 五、交易 API（/transactions）

### 5.1 交易列表

**端點**: `GET /transactions`
**認證**: 需要
**用途**: 查看我的交易記錄（作為買家或賣家）

**Request**:
```
GET /transactions?role=buyer&status=pending&page=1
```

| 參數 | 類型 | 說明 |
|------|------|------|
| `role` | string | buyer（我是買家）/ seller（我是賣家）/ all |
| `status` | string | pending/accepted/completed/cancelled |
| `page` | int | 頁碼 |

**Response**:
- **Status**: 200 OK
- **Body**: 交易列表頁面 `transactions/index.html`

---

### 5.2 交易詳情

**端點**: `GET /transactions/<id>`
**認證**: 需要（且須為交易參與者）
**用途**: 查看交易詳細資訊

**Request**:
```
GET /transactions/456
```

**Response**:
- **Status**: 200 OK
- **Body**: 交易詳情頁面 `transactions/detail.html`
- **資料**:
  - 交易完整資訊
  - 商品資訊
  - 買賣雙方資訊
  - 交易狀態歷史

---

### 5.3 發起交易

**端點**: `POST /transactions/create`
**認證**: 需要
**用途**: 對商品發起交易請求

**Request**:
```
POST /transactions/create
Content-Type: application/x-www-form-urlencoded

product_id=123
transaction_type=purchase
amount=25000
notes=可以面交嗎？
```

**Success Response** (JSON):
```json
{
    "status": "success",
    "message": "交易請求已發送",
    "transaction_id": 456,
    "redirect": "/transactions/456"
}
```

**Error Response** (JSON):
```json
{
    "status": "error",
    "message": "無法對自己的商品發起交易"
}
```

---

### 5.4 接受交易

**端點**: `POST /transactions/<id>/accept`
**認證**: 需要（且須為賣家）
**用途**: 賣家接受交易請求

**Request**:
```
POST /transactions/456/accept
```

**Success Response**:
- **Status**: 302 Redirect
- **Location**: `/transactions/456`
- **Flash Message**: "已接受交易請求"

---

### 5.5 拒絕交易

**端點**: `POST /transactions/<id>/reject`
**認證**: 需要（且須為賣家）
**用途**: 賣家拒絕交易請求

**Request**:
```
POST /transactions/456/reject
```

**Success Response**:
- **Status**: 302 Redirect
- **Location**: `/transactions`
- **Flash Message**: "已拒絕交易請求"

---

### 5.6 完成交易

**端點**: `POST /transactions/<id>/complete`
**認證**: 需要（買家或賣家）
**用途**: 標記交易已完成

**Request**:
```
POST /transactions/456/complete
```

**Success Response**:
- **Status**: 302 Redirect
- **Location**: `/reviews/new/456`
- **Flash Message**: "交易已完成，請評價對方"

---

### 5.7 取消交易

**端點**: `POST /transactions/<id>/cancel`
**認證**: 需要（買家或賣家）
**用途**: 取消交易

**Request**:
```
POST /transactions/456/cancel
```

**Success Response**:
- **Status**: 302 Redirect
- **Location**: `/transactions`
- **Flash Message**: "交易已取消"

---

## 六、訊息 API（/messages）

### 6.1 訊息列表

**端點**: `GET /messages`
**認證**: 需要
**用途**: 查看所有對話列表

**Request**:
```
GET /messages
```

**Response**:
- **Status**: 200 OK
- **Body**: 訊息列表頁面 `messages/index.html`
- **資料**:
  - 對話列表（顯示最後一則訊息）
  - 未讀訊息數量

---

### 6.2 對話詳情

**端點**: `GET /messages/<user_id>`
**認證**: 需要
**用途**: 與特定使用者的對話

**Request**:
```
GET /messages/789?product_id=123
```

**Response**:
- **Status**: 200 OK
- **Body**: 聊天介面 `messages/chat.html`
- **資料**:
  - 與該使用者的所有訊息
  - 相關商品資訊（如有）

---

### 6.3 發送訊息

**端點**: `POST /messages/send`
**認證**: 需要
**用途**: 發送訊息給其他使用者

**Request** (JSON):
```json
POST /messages/send
Content-Type: application/json

{
    "receiver_id": 789,
    "product_id": 123,
    "content": "這個商品還在嗎？"
}
```

**Success Response** (JSON):
```json
{
    "status": "success",
    "message_id": 1001,
    "created_at": "2024-11-29 12:34:56"
}
```

---

### 6.4 標記已讀

**端點**: `POST /messages/<id>/read`
**認證**: 需要
**用途**: 標記訊息為已讀

**Request**:
```
POST /messages/1001/read
```

**Success Response** (JSON):
```json
{
    "status": "success"
}
```

---

## 七、評價 API（/reviews）

### 7.1 提交評價

**端點**: `GET/POST /reviews/new/<transaction_id>`
**認證**: 需要
**用途**: 對交易完成後的對方進行評價

**GET Request**:
```
GET /reviews/new/456
```

**Response**:
- **Status**: 200 OK
- **Body**: 評價表單頁面 `reviews/form.html`

**POST Request**:
```
POST /reviews/new/456
Content-Type: application/x-www-form-urlencoded

rating=5
comment=交易順利，賣家很好！
```

**Success Response**:
- **Status**: 302 Redirect
- **Location**: `/transactions/456`
- **Flash Message**: "評價已提交"

---

### 7.2 查看使用者評價

**端點**: `GET /users/<id>/reviews`
**認證**: 不需要
**用途**: 查看某位使用者收到的所有評價

**Request**:
```
GET /users/789/reviews?page=1
```

**Response**:
- **Status**: 200 OK
- **Body**: 評價列表頁面 `reviews/list.html`
- **資料**:
  - 使用者資訊
  - 平均評分
  - 評價列表（分頁）

---

## 八、HTTP 狀態碼規範

| 狀態碼 | 說明 | 使用情境 |
|--------|------|---------|
| 200 OK | 成功 | GET 請求成功返回頁面 |
| 302 Found | 重定向 | POST 成功後重定向 |
| 400 Bad Request | 錯誤請求 | 表單驗證失敗 |
| 401 Unauthorized | 未認證 | 需要登入但未登入 |
| 403 Forbidden | 無權限 | 認證但無權限執行操作 |
| 404 Not Found | 找不到 | 資源不存在 |
| 500 Internal Server Error | 伺服器錯誤 | 系統內部錯誤 |

---

## 九、錯誤處理格式

### 9.1 HTML 回應（一般頁面）

**錯誤顯示方式**:
- 使用 Flask Flash Messages
- 在頁面頂部顯示錯誤/成功訊息
- 使用不同顏色區分（紅色=錯誤、綠色=成功、黃色=警告）

**範例**:
```html
<!-- 成功訊息 -->
<div class="alert alert-success">商品刊登成功</div>

<!-- 錯誤訊息 -->
<div class="alert alert-error">Email 已被註冊</div>

<!-- 警告訊息 -->
<div class="alert alert-warning">請先登入</div>
```

### 9.2 JSON 回應（AJAX 請求）

**成功回應**:
```json
{
    "status": "success",
    "message": "操作成功",
    "data": { ... }
}
```

**錯誤回應**:
```json
{
    "status": "error",
    "message": "錯誤訊息",
    "errors": {
        "field_name": ["錯誤說明"]
    }
}
```

---

## 十、安全性考量

### 10.1 CSRF 保護

所有 POST/PUT/DELETE 請求都必須包含 CSRF Token：

```html
<form method="POST">
    {{ form.csrf_token }}
    <!-- 其他欄位 -->
</form>
```

### 10.2 認證檢查

使用裝飾器進行認證：

```python
from flask_login import login_required

@bp.route('/products/new', methods=['GET', 'POST'])
@login_required
def create_product():
    ...
```

### 10.3 權限檢查

檢查使用者是否有權限執行操作：

```python
@bp.route('/products/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_product(id):
    product = Product.query.get_or_404(id)
    if product.user_id != current_user.id:
        abort(403)  # 無權限
    ...
```

---

## 十一、總結

### 11.1 API 端點總計

| 模組 | 端點數量 | 說明 |
|------|---------|------|
| 認證 | 4 | 註冊、登入、登出、個人資料 |
| 商品 | 6 | 列表、詳情、刊登、編輯、刪除、我的商品 |
| 交易 | 7 | 列表、詳情、發起、接受、拒絕、完成、取消 |
| 訊息 | 4 | 列表、對話、發送、標記已讀 |
| 評價 | 2 | 提交評價、查看評價 |
| **總計** | **23** | |

### 11.2 下一步

請繼續閱讀：
- [05-frontend-design.md](./05-frontend-design.md) - 前端設計
- [06-project-structure.md](./06-project-structure.md) - 專案結構
- [07-development-guide.md](./07-development-guide.md) - 開發指南
