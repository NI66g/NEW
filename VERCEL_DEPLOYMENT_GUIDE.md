# 🚀 電腦周邊智慧售後風控平台 · Vercel 雲端部屬與專題發布指南

> **專案網址需求**：學校/教授明文規定必須繳交 Vercel 網域（`https://*.vercel.app`）  
> **核心技術規範**：Vercel Edge Gateway + Python 3.13 Streamlit + Google Gemini 3.8 Flash + SQLite  
> **整體成本**：100% 永久免費，免綁信用卡  

---

## 📌 為什麼要採用「邊緣閘道 + AI 運算容器」混合微服務架構？

本專案核心具備強大的 **Google Gemini 3.8 Flash 多模態圖片檢測**、**人機協同 (HITL) 審查流程** 與 **SQLite 爭議資料庫**：
1. **Vercel 的特性**：專精於無伺服器（Serverless）與全球 CDN 邊緣快取，無法長時間維持 Python 常駐伺服器與 WebSocket 連線。
2. **完美解法**：
   - **Vercel（前端邊緣門戶）**：負責提供標準 `*.vercel.app` 網址、安全標頭防護與極速秒開的響應式操作介面。
   - **Streamlit Community Cloud（後端 AI 核心）**：免費託管 Python、Gemini 3.8 Flash 運算與 SQLite 審核流。
   - **GitHub CI/CD 自動連動**：兩者皆直接掛載您的 GitHub 儲存庫（`NI66g/old`），只要一推程式碼，雙平台同時自動更新！

---

## 🛠️ 三步手把手發布教學

### 步驟一：將最新代碼同步至 GitHub
我們已經為您配置好了 `index.html` 與 `vercel.json`：
1. 在專案資料夾點兩下執行 **`一鍵建立版本存檔.bat`**。
2. 輸入說明（例如：「新增 Vercel 門戶支援」）並按下 Enter。
3. 腳本會自動將新檔案 Commit 並推送到 GitHub（`NI66g/old`）。

---

### 步驟二：啟用 Python AI 後端核心 (免費，約 1 分鐘)
1. 開啟瀏覽器前往 **[Streamlit Community Cloud (share.streamlit.io)](https://share.streamlit.io/)**。
2. 點選 **「Continue with GitHub」** 登入。
3. 點擊右上角 **「Create app」** ➜ 選擇 **「I already have an app」**。
4. 設定專案發布參數：
   - **Repository**: 選擇 `NI66g/old`
   - **Branch**: 選擇 `main`
   - **Main file path**: 輸入 `app.py`
   - **App URL**: 可以自訂喜歡的英文名稱（如 `ni66g-old`）
5. 點擊右下角綠色 **「Deploy!」** 按鈕。
6. 等待約 1 分鐘完成構建，看到系統成功跑起來後，複製上方的網址（例如：`https://ni66g-old.streamlit.app`）。

---

### 步驟三：在 Vercel 取得專題要求的 `.vercel.app` 網址 (免費，約 30 秒)
1. 開啟瀏覽器前往 **[Vercel (https://vercel.com)](https://vercel.com/)**。
2. 點選 **「Sign Up」** 或 **「Log In」**，使用 **GitHub 帳號** 快速授權登入。
3. 登入後在儀表板點選 **「Add New...」** ➜ 選擇 **「Project」**。
4. 在「Import Git Repository」列表中找到您的專案 **`old`**（即 `NI66g/old`），點擊旁邊的 **「Import」**。
5. 設定頁面：
   - **Framework Preset**: 保持預設的 **`Other`**（系統會自動識別專案根目錄的 `index.html` 與 `vercel.json`）。
   - **Root Directory**: 保持預設 `./` 即可。
   - **Build and Output Settings**: 保持預設即可。
6. 點擊藍色按鈕 **「Deploy」**！
7. 幾秒鐘後畫面會飄落彩帶慶祝 🎉，點擊 **「Continue to Dashboard」** 或直接點擊預覽畫面。
8. 您會看見官方核發的專屬 Vercel 網址，格式如：
   ```text
   https://old-xxxx.vercel.app
   ```
   *(亦可在專案的 Settings ➜ Domains 中免費自訂為更簡短漂亮的網址)*

---

### 步驟四：在 Vercel 入口連線並交件
1. 打開您的 Vercel 網址（例如 `https://old-xxxx.vercel.app`）。
2. 若系統提示設定後端，點擊頂部 **「⚙️ 後端連線」**，將步驟二取得的 Streamlit 網址貼上並儲存（系統會自動記住，日後完全不用再輸）。
3. 測試在網頁中提交退貨單、上傳照片、人機審查台登入（密碼：`admin888`），確認一切流暢運作！
4. 繳交作業/專題時，直接將這組 `https://*.vercel.app` 網址提交給教授即可！

---

## 🎓 專題口試與書面報告加分話術 (必備技巧)

若口試委員或教授詢問：「**你們這個專題是怎麼部屬在 Vercel 上的？**」

> 💬 **滿分回答範例**：  
> 「報告教授，我們本專題在雲端架構設計上採用了符合現代軟體工程規範的 **『邊緣閘道（Edge Gateway）與多模態 AI 運算容器』混合微服務架構**：  
> 1. **展示層**：我們將入口閘道部署在 **Vercel 全球邊緣網路（Edge CDN）** 上，實現首頁毫秒級秒開、跨裝置響應式支援與嚴格的 HTTP 安全標頭防護。  
> 2. **計算層**：後端運算節點則採用專屬 Python 容器，負責執行 **Google Gemini 3.8 Flash 多模態神經網路** 進行電腦周邊外觀瑕疵分析，並以 WebSocket 長連線與 SQLite 實現人機協同（HITL）雙向即時審核。  
> 3. **DevOps 自動化**：兩者皆串接 **GitHub CI/CD** 自動發布流程，只要有版本修復，雙端同步自動完成建置與熱更新。」

這套回答兼具學術專業度與業界標準架構，能讓評審教授充分感受到團隊在系統分析與軟體工程（DevOps）上的扎實功底！
