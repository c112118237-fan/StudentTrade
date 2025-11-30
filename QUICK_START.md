# StudentTrade 快速啟動指南

## ✅ 系統狀態

您的 StudentTrade 應用程式已經成功部署！

- 🐳 **Docker容器**: 正常運行
- 🗄️ **PostgreSQL資料庫**: 8 個資料表已創建
- 🌐 **Flask應用**: 運行於 http://localhost:5000
- 📊 **API端點**: 28 個 RESTful API 已就緒

## 🚀 訪問應用

打開瀏覽器訪問：
```
http://localhost:5000
```

## 📋 已實作功能

### 1. 認證系統 ✅
- 使用者註冊（學校信箱驗證）
- 使用者登入/登出
- 個人資料管理
- 密碼變更

### 2. 商品管理 ✅
- 商品刊登（支援最多 5 張圖片）
- 商品搜尋與篩選
- 商品編輯/刪除
- 瀏覽次數統計

### 3. 交易系統 ✅
- 發起交易請求
- 接受/拒絕交易
- 完成/取消交易
- 交易狀態追蹤

### 4. 訊息系統 ✅
- 私人訊息
- 對話列表
- 未讀訊息計數
- 訊息標記已讀

### 5. 評價系統 ✅
- 交易後互評（1-5星）
- 評價統計
- 評價列表

### 6. 通知系統 ✅
- 自動通知（交易、訊息、評價）
- 未讀通知計數
- 通知管理

## 🛠️ 常用命令

### 查看容器狀態
```bash
docker-compose ps
```

### 查看應用日誌
```bash
docker-compose logs -f web
```

### 停止應用
```bash
docker-compose down
```

### 重新啟動應用
```bash
docker-compose up -d
```

### 進入 PostgreSQL
```bash
docker-compose exec db psql -U studenttrade -d studenttrade
```

### 初始化資料庫（清空資料並重建）
```bash
docker-compose exec web python init_db.py
```

## 📊 資料庫結構

已創建的 8 個資料表：
1. **users** - 使用者資料
2. **categories** - 商品分類
3. **products** - 商品資訊
4. **product_images** - 商品圖片（最多5張）
5. **transactions** - 交易記錄
6. **messages** - 私人訊息
7. **notifications** - 系統通知
8. **reviews** - 使用者評價

## 🔑 預設配置

### 資料庫連接
- **主機**: localhost
- **埠口**: 5432
- **資料庫**: studenttrade
- **使用者**: studenttrade
- **密碼**: studenttrade123

### Flask 應用
- **主機**: localhost
- **埠口**: 5000
- **模式**: Development (Debug=True)

## 📝 使用流程

1. **註冊帳號**
   - 訪問 http://localhost:5000/auth/register
   - 使用學校信箱註冊（需要 .edu 或 .edu.tw 結尾）
   - 密碼至少 8 字元，包含數字和字母

2. **刊登商品**
   - 登入後點擊「刊登商品」
   - 填寫商品資訊並上傳圖片（最多 5 張）
   - 選擇分類和商品狀況

3. **瀏覽商品**
   - 首頁顯示所有上架商品
   - 可使用搜尋和篩選功能
   - 點擊商品查看詳情

4. **發起交易**
   - 在商品詳情頁點擊「發起交易」
   - 填寫交易資訊
   - 等待賣家回應

5. **私訊溝通**
   - 點擊訊息圖示
   - 選擇對話對象
   - 即時私訊交流

6. **完成交易並評價**
   - 交易完成後可互相評價
   - 評分 1-5 星並可留言
   - 評價會顯示在使用者個人頁面

## 🐛 故障排除

### 應用無法啟動
```bash
# 檢查日誌
docker-compose logs web

# 重新構建並啟動
docker-compose up -d --build
```

### 資料庫連接失敗
```bash
# 檢查資料庫狀態
docker-compose logs db

# 重啟資料庫
docker-compose restart db
```

### 圖片上傳失敗
```bash
# 確保上傳目錄存在
docker-compose exec web mkdir -p /app/app/static/uploads/products
docker-compose exec web mkdir -p /app/app/static/uploads/avatars
```

## 📚 技術文件

詳細的技術文件請參閱：
- [BACKEND_README.md](BACKEND_README.md) - 完整後端技術文件
- [docs/](docs/) - 專案規劃文件（9 個 Markdown 文件）

## 🎯 下一步

1. **測試功能**: 註冊多個帳號測試完整流程
2. **自訂配置**: 修改 .env 檔案調整配置
3. **部署生產**: 參考 BACKEND_README.md 的部署章節

## ⚠️ 注意事項

- 這是開發環境，Debug 模式已啟用
- 部署到生產環境前請變更 SECRET_KEY
- 建議使用 HTTPS 保護使用者資料
- 定期備份 PostgreSQL 資料庫

---

如有問題，請參閱 [BACKEND_README.md](BACKEND_README.md) 或檢查應用日誌。
