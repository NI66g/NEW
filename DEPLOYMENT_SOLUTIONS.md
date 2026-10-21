# 🛡️ 電腦周邊智慧退換貨與爭議風控平台 · 雲端部署與資料庫架構方案 (A/B)

> **專案環境**：Python 3.13 / Streamlit / SQLite / Google Gemini AI / Gmail SMTP  
> **適用場景**：資管系畢業專題、校園展示、線上口試評審、雲端 24 小時隨時運行

---

## 📌 核心痛點背景說明
原本專案設計為前後台分離之獨立程式：
- **前台門戶 (`buyer.py`)**：供買家提交售後退換貨申請與進度查詢。
- **後台管理 (`app.py`)**：供店長人機協同審核、老闆 BI 營運儀表板、系統參數設定。
- **本地運作**：在同一台電腦運行時，前後台共用本地 SQLite 資料庫檔案 (`disputes.db`)，運作正常。
- **雲端部署問題 (如 Streamlit Community Cloud)**：
  若在雲端建立兩個獨立的網址（如 `xxx-buyer.streamlit.app` 與 `xxx-admin.streamlit.app`），雲端會分別啟動**兩個獨立隔離的 Linux 虛擬容器 (Docker)**。本地 SQLite 檔案無法跨容器通訊，買家前台寫入的資料，後台容器無法讀取。
- **Vercel 不相容性說明**：
  Vercel 是無伺服器 (Serverless) 架構，磁碟為唯讀/臨時性 (幾秒後自動銷毀)，無法持久保存 SQLite，且不支援 Streamlit 所需的長時 WebSocket 連線。

為解決線上展示與雲端資料庫互通，制定以下 **方案 A** 與 **方案 B**。

---

## 🌟 方案 A：整合型單一雲端應用 + 管理員密碼防護鎖 (最推薦 / 零成本最穩健)

### 1. 架構原理
- 將買家前台 (`buyer.py`) 與商家管理後台 (`app.py`) 整合成**單一標準入口 (`app.py`)**。
- 部署於免費且原生支援 Python 的 **Streamlit Community Cloud** (只要有一個 GitHub 倉庫即可一鍵發布)。
- 兩者運行在同一個雲端伺服器容器中，**直接共享同一個 `disputes.db` SQLite 資料庫**。

### 2. 權限防護設計 (Role-Based Access Control)
- **訪客 / 一般買家瀏覽**：
  進入網址時，預設僅能使用「買家服務門戶」：
  - 📝 提交退換貨申請 (含品類選擇、瑕疵描述、必填佐證照片上傳)
  - 🔍 查詢申請進度 / 補充照片
  - 側邊欄隱藏所有審核判決、AI 風控細節、BI 商業營業數據與 API 金鑰設定。
- **教授 / 審查店長 / 管理者**：
  在側邊欄「🔐 管理員登入」區塊輸入密碼 (預設：`admin888`，可於系統設定中自訂修改)：
  - 驗證成功後，系統動態解鎖：
    - 🧑‍💼 店長：人機對照審核台 (HITL)
    - 📊 老闆：BI 營運成效儀表板
    - ⚙️ 系統設定 & API (Gemini 金鑰、Gmail 寄件設定、示範資料重設)
  - 提供一鍵「🚪 登出後台」按鈕，隨時鎖定回買家模式。

### 3. 優勢分析
- ✅ **資料 100% 即時互通**：買家提交後，切換或刷新後台即刻呈現最新案件。
- ✅ **免申請第三方外部資料庫**：不需要註冊雲端 PostgreSQL、不需要配置連線密碼與防火牆。
- ✅ **前後台安全隔離**：買家在不知道密碼的情況下，完全無法接觸商家後台數據。
- ✅ **展示便利**：只需給評審教授一組公開網址 + 管理者密碼即可完整展現雙邊功能。

---

## 🌐 方案 B：雙獨立網址 + 免費雲端關聯式資料庫 (Supabase / Turso)

### 1. 架構原理
- 前台 (`buyer.py`) 與後台 (`app.py`) 維持為兩個完全不同的獨立網址 (例如發布在兩個不同的 Streamlit Cloud 應用或伺服器)。
- 放棄本機 SQLite 檔案，將資料庫連線改接至外部的**公有雲資料庫 (Cloud Database)**。

### 2. 推薦免費雲端資料庫
1. **Supabase (PostgreSQL)**：
   - 提供 500MB 免費雲端 PostgreSQL 資料庫。
   - 具有網頁版視覺化資料表編輯器。
   - Python 連線方式：使用 `psycopg2-binary` 或 `SQLAlchemy`，連線字串格式為 `postgresql://user:pwd@db.supabase.co:5432/postgres`。
2. **Turso (雲端版 SQLite / LibSQL)**：
   - 本質是 SQLite 語法，但託管於全域邊緣雲端。
   - Python 使用 `libsql-experimental` 套件連線，支援同步多點讀寫。

### 3. 實施步驟
1. 註冊 Supabase 或 Turso 帳號並建立專案。
2. 建立 `return_requests` 資料表與對應欄位 (order_id, customer_email, product_category, product_name, customer_reason, image_data, status, risk_level, risk_score, ai_verdict, ai_evidence, ai_recommendation, review_comment, created_at, reviewed_at)。
3. 在 `requirements.txt` 加入 `psycopg2-binary` 或 `libsql-client`。
4. 將 `app.py` 與 `buyer.py` 中的 `sqlite3.connect(DB_FILE)` 抽換為雲端資料庫連線池。
5. 在 Streamlit Cloud 的 Secrets 設定中配置雲端連線字串與金鑰。

### 4. 優缺點評估
- ✅ 前後台網址徹底獨立分開。
- ⚠️ 需額外維護第三方雲端資料庫帳號與金鑰。
- ⚠️ 免費雲端資料庫若長時間未存取可能會有休眠喚醒延遲 (Cold Start)。

---

## 📋 方案選擇總結

| 評估維度 | 🌟 方案 A (單一雲端應用 + 密碼鎖) | 🌐 方案 B (雙網址 + 雲端資料庫) |
| :--- | :--- | :--- |
| **部屬複雜度** | ⭐ 極低 (一鍵發布) | ⭐⭐⭐ 較高 (需建雲端 DB 與換連線) |
| **資料庫架構** | 共享本地 SQLite (`disputes.db`) | 外部雲端 PostgreSQL / Turso |
| **外部依賴** | 僅需 Streamlit Cloud | 需 Streamlit Cloud + Supabase |
| **費用與維護** | 永久免費、無額外設定 | 免費但需留意資料庫休眠機制 |
| **專題展示推薦** | **強烈推薦 (評審口試最穩)** | 適合需要強調微服務分散式架構者 |
