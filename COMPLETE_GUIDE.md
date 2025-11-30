# StudentTrade 完整使用指南

## ✅ 已完成的功能

### 🎨 前後端整合完成
- ✅ Toast 通知系統（Tailwind CSS 4.1 + Alpine.js 3.x）
- ✅ 表單欄位修正（登入/註冊完全對接後端）
- ✅ 首頁無需登入即可瀏覽
- ✅ 商品詳情需登入才能查看
- ✅ 買家/賣家雙角色功能完整
- ✅ 使用者頭貼顯示（登入後顯示使用者名稱首字母圓形頭貼）
- ✅ 下拉選單功能（購物車、賣場、編輯個人資料、登出）

### 📝 表單欄位已修正
1. **登入頁面** (`/auth/login`)
   - ✅ 修正：`identifier` → `email`
   - ✅ 添加 CSRF Token
   - ✅ 添加 POST 方法和 action

2. **註冊頁面** (`/auth/register`)
   - ✅ 修正：`password_confirm` → `confirm_password`
   - ✅ 添加 CSRF Token
   - ✅ 添加 POST 方法和 action
   - ✅ 添加學校信箱說明

### 🔐 權限控制
- ✅ 首頁（商品列表）：**無需登入**即可瀏覽
- ✅ 商品詳情：**需要登入**才能查看
- ✅ 刊登商品：需要登入
- ✅ 發起交易：需要登入
- ✅ 私訊功能：需要登入
- ✅ 評價功能：需要登入

## 🚀 快速啟動

### 1. 啟動服務

```bash
# 啟動 Docker Compose（自動連接 PostgreSQL）
docker-compose up -d

# 查看容器狀態
docker-compose ps
```

### 2. 初始化資料庫

```bash
# 進入 web 容器並初始化資料庫
docker exec -it studenttrade_web python init_db.py

# 輸入 'yes' 確認初始化
```

### 3. 訪問應用

打開瀏覽器訪問：**http://localhost:5000**

## 📋 測試流程

### 測試 1：首頁瀏覽（無需登入）

1. 訪問 http://localhost:5000
2. ✅ 應該看到商品列表頁面
3. ✅ 可以瀏覽但無商品（尚未建立）
4. ✅ 導航欄顯示「登入」和「註冊」按鈕

### 測試 2：註冊新帳號

1. 點擊「註冊」或訪問 http://localhost:5000/auth/register
2. 填寫表單：
   - **使用者名稱**：王小明（2-20字元，中文英文數字底線）
   - **學校信箱**：student@example.edu 或 student@school.edu.tw
   - **密碼**：password123（至少8字元，含英文和數字）
   - **確認密碼**：password123
3. 點擊「註冊」
4. ✅ 應該看到 Toast 通知：「註冊成功！請重新登入」
5. ✅ 自動跳轉到登入頁面

### 測試 3：登入

1. 在登入頁面填寫：
   - **電子郵件**：student@example.edu
   - **密碼**：password123
   - （可選）勾選「記住我」
2. 點擊「登入」
3. ✅ 應該看到 Toast 通知：「歡迎回來，王小明！」
4. ✅ 跳轉到首頁
5. ✅ 導航欄顯示使用者頭貼（圓形，顯示名稱首字母）和使用者名稱
6. ✅ 點擊使用者名稱顯示下拉選單：
   - 購物車
   - 賣場
   - 編輯個人資料
   - 登出

### 測試 4：商品詳情需登入

1. **未登入狀態**：
   - 在首頁點擊任一商品
   - ✅ 應該看到 Toast 警告：「請先登入以查看商品詳情」
   - ✅ 自動跳轉到登入頁面
   - ✅ 登入後自動返回原商品頁面

2. **已登入狀態**：
   - 可以正常查看商品詳情
   - 可以發起交易
   - 可以聯絡賣家

### 測試 5：刊登商品（賣家功能）

1. 登入後點擊「刊登商品」
2. 填寫商品資訊：
   - 商品標題
   - 商品描述
   - 價格
   - 商品分類
   - 商品狀況（全新/近全新/良好/普通/需修理）
   - 上傳圖片（最多5張）
3. 提交後：
   - ✅ Toast 通知：「商品已成功刊登！」
   - ✅ 跳轉到商品詳情頁
   - ✅ 您現在是該商品的**賣家**

### 測試 6：購買商品（買家功能）

1. 使用另一個帳號登入（或註冊新帳號）
2. 瀏覽首頁商品
3. 點擊商品進入詳情頁
4. 點擊「發起交易」
5. 填寫交易資訊並提交
6. ✅ Toast 通知：「交易請求已送出！」
7. ✅ 您現在是該商品的**買家**

### 測試 7：賣家接受交易

1. 登入賣家帳號
2. 訪問「交易」頁面
3. 查看待處理的交易請求
4. 點擊「接受」
5. ✅ Toast 通知：「交易已接受」
6. ✅ 交易狀態更新為「已接受」

### 測試 8：完成交易並評價

1. 雙方確認交易完成
2. 點擊「完成交易」
3. ✅ Toast 通知：「交易已完成」
4. 前往評價頁面
5. 互相評價（1-5星 + 評論）
6. ✅ Toast 通知：「評價已提交！」

## 🎯 Toast 通知類型

### 成功通知（綠色）
- 註冊成功
- 登入成功
- 商品刊登成功
- 交易操作成功
- 評價提交成功

### 錯誤通知（紅色）
- 表單驗證失敗
- 登入失敗
- 權限不足
- 操作失敗

### 警告通知（黃色）
- 需要登入
- 確認操作
- 狀態不符

### 資訊通知（藍色）
- 一般提示
- 系統訊息

## 📊 資料庫檢查

### 查看資料表

```bash
docker exec -it studenttrade_db psql -U studenttrade -d studenttrade -c "\dt"
```

### 查看使用者

```bash
docker exec -it studenttrade_db psql -U studenttrade -d studenttrade -c "SELECT id, email, username, created_at FROM users;"
```

### 查看商品

```bash
docker exec -it studenttrade_db psql -U studenttrade -d studenttrade -c "SELECT id, title, price, status, user_id FROM products;"
```

### 查看交易

```bash
docker exec -it studenttrade_db psql -U studenttrade -d studenttrade -c "SELECT id, product_id, buyer_id, seller_id, status FROM transactions;"
```

## 🔧 開發工具

### 查看容器日誌

```bash
# Web 容器日誌
docker-compose logs -f web

# 資料庫日誌
docker-compose logs -f db
```

### 重啟服務

```bash
# 重啟 web 容器
docker-compose restart web

# 重啟所有容器
docker-compose restart
```

### 停止服務

```bash
docker-compose down
```

### 重新構建

```bash
docker-compose up -d --build
```

## 🎨 Toast 使用範例

### 在 JavaScript 中使用

```javascript
// 成功通知
Toast.success('操作成功！');

// 錯誤通知
Toast.error('發生錯誤，請重試');

// 警告通知
Toast.warning('請注意：這個操作無法復原');

// 資訊通知
Toast.info('系統維護中，請稍後再試');

// 自訂顯示時間（毫秒）
Toast.success('訊息內容', 5000);  // 顯示 5 秒
```

### Flask Flash 訊息自動轉換

後端 Python 程式碼：
```python
flash('註冊成功！', 'success')    # → 綠色 Toast
flash('操作失敗', 'error')        # → 紅色 Toast
flash('請先登入', 'warning')       # → 黃色 Toast
flash('系統訊息', 'info')          # → 藍色 Toast
```

前端會自動顯示對應的 Toast 通知！

## 📝 密碼規則

**已放寬為**：
- ✅ 至少 8 個字元
- ✅ 包含英文字母（大小寫皆可）
- ✅ 包含數字

**範例**：
- ✅ `password123`
- ✅ `mypass99`
- ✅ `student2024`
- ❌ `12345678`（只有數字）
- ❌ `password`（沒有數字）
- ❌ `pass123`（少於8字元）

## 🏫 學校信箱規則

必須使用以下結尾的信箱：
- ✅ `.edu`（如：student@school.edu）
- ✅ `.edu.tw`（如：s123456@mail.ncku.edu.tw）

**不接受**：
- ❌ `@gmail.com`
- ❌ `@yahoo.com`
- ❌ 其他非學校信箱

## 🎭 買家/賣家雙角色

### 您可以同時是：

1. **賣家**
   - 刊登商品
   - 接受/拒絕交易請求
   - 收取款項
   - 被買家評價

2. **買家**
   - 瀏覽商品
   - 發起交易
   - 付款購買
   - 評價賣家

### 範例場景

**王小明**：
- 賣出二手課本 → 是賣家
- 購買二手腳踏車 → 是買家

**李大華**：
- 賣出舊電腦 → 是賣家
- 買了王小明的課本 → 是買家

## 🐛 常見問題

### Q: 登入後還是無法查看商品詳情？
A: 檢查瀏覽器 Cookie，清除快取後重新登入。

### Q: Toast 通知沒有顯示？
A: 檢查瀏覽器控制台是否有 JavaScript 錯誤。

### Q: 無法上傳圖片？
A: 確保圖片格式為 PNG, JPG, JPEG, GIF，且大小不超過 5MB。

### Q: 密碼驗證失敗？
A: 確保密碼至少 8 字元，包含英文和數字。

### Q: 學校信箱驗證失敗？
A: 確保信箱結尾是 `.edu` 或 `.edu.tw`。

## 📞 聯絡資訊

如有問題，請參閱：
- [BACKEND_README.md](BACKEND_README.md) - 技術文件
- [QUICK_START.md](QUICK_START.md) - 快速啟動指南

---

**祝您使用愉快！** 🎉
