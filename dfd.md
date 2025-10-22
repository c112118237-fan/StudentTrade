## DFD 與系統環境圖 (Context Diagram)

此文件包含 StudentTrade 系統的系統環境圖（DFD Context）與 DFD 圖0（Level 0）。
---


---

## 系統環境圖（Context Diagram - DFD Level: Context）

下圖描述 StudentTrade 與外部實體之間的主要資料流：

```mermaid
flowchart LR
  subgraph External[外部實體]
    User[使用者]
    Admin[管理者]
    Payment[第三方支付]
  end

  subgraph System[StudentTrade 系統]
    ST[StudentTrade]
  end

  ## DFD 與系統環境圖 (Context Diagram)

  此文件包含 StudentTrade 系統的系統環境圖（DFD Context）與 DFD 圖0（Level 0）。
  ---


  ## 系統環境圖（Context Diagram - DFD Level: Context）

  下圖描述 StudentTrade 與外部實體之間的主要資料流：

  ```mermaid
  flowchart LR
    subgraph External[外部實體]
      User[使用者]
      Admin[管理者]
      Payment[第三方支付]
    end

    subgraph System[StudentTrade 系統]
      ST[StudentTrade]
    end

    User -->|登入／註冊、刊登商品、查詢商品、交換請求| ST
    ST -->|商品列表、回覆交易、通知| User
    Admin -->|管理命令、審核請求| ST
    ST -->|稽核日誌、通知| Admin
    ST -->|付款請求／確認| Payment
    Payment -->|付款回傳、退款| ST
  ```

  說明：
  - 外部實體：使用者（買/賣）、系統管理者、第三方支付平台。
  - 主要資料流包含：使用者與系統之間的帳號、商品、交換請求、通知與交易資訊。



  ---

  ## DFD 圖0（Level 0）

  下圖為 Level 0（圖0）示意圖，至少包含三個以上的處理程序（Process）：

  ```mermaid
  flowchart TB
    %% External entities
    User[使用者]
    Payment[第三方支付]
    Admin[管理者]

    %% Processes
    P1[(P1) 使用者管理]
    P2[(P2) 商品管理]
    P3[(P3) 交易與交換處理]
    P4[(P4) 通知與日誌]

    %% Data stores
    DS1[(D1) 使用者資料庫]
    DS2[(D2) 商品資料庫]
    DS3[(D3) 交易記錄]

    %% Flows
    User -->|註冊/登入/更新資料| P1
    P1 -->|讀取/寫入| DS1

    User -->|刊登/查詢/下架商品| P2
    P2 -->|讀取/寫入| DS2

    User -->|提出交換/購買請求| P3
    P3 -->|建立/更新| DS3
    P3 -->|付款請求| Payment
    Payment -->|付款結果| P3

    P3 -->|交易結果、通知| P4
    P2 -->|商品變動通知| P4
    P1 -->|帳號異動通知| P4
    P4 -->|訊息/Email/系統日誌| Admin

    Admin -->|管理/審核| P2
    Admin -->|稽核| P3

  ```

  說明：
  - P1 使用者管理：處理註冊、登入、帳號更新與驗證。
  - P2 商品管理：處理刊登、修改、下架、查詢商品。
  - P3 交易與交換處理：處理交換請求、付款請求、交易完成與交易記錄。
  - P4 通知與日誌：負責發送系統通知、Email、以及記錄系統日誌。

  資料庫（Data Stores）至少包含使用者、商品與交易記錄三個資料庫。

