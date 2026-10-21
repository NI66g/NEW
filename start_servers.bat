@echo off
chcp 65001 >nul
cd /d "%~dp0"
title 電腦周邊退換貨風控系統 - 服務啟動器

echo ========================================================
echo   電腦周邊智慧退換貨與爭議風控系統 (方案 A 全整合系統)
echo ========================================================
echo.
set "STREAMLIT_CMD=streamlit"
if exist "%~dp0.venv\Scripts\streamlit.exe" (
    set "STREAMLIT_CMD=%~dp0.venv\Scripts\streamlit.exe"
)

echo [啟動中] 正在啟動 方案 A 整合服務 (Port 8501)...
start "周邊風控全整合門戶 (Port 8501)" cmd /k "cd /d ""%~dp0"" && "%STREAMLIT_CMD%" run app.py --server.port 8501"

echo.
echo --------------------------------------------------------
echo ✅ 系統已成功啟動！
echo.
echo 🌐 網站入口：http://localhost:8501
echo.
echo 💡 使用說明：
echo   1. 預設進入【買家門戶】（提交退貨申請、查詢進度與補件）。
echo   2. 側邊欄點選【商家 / 店長後台登入】，輸入密碼即可解鎖管理功能。
echo      ★ 系統預設管理員密碼：admin888
echo      ★ 可隨時至「系統設定」修改密碼。
echo   3. 買家申訴與店長審核台即時共用同一 SQLite 資料庫，零延遲呈現！
echo --------------------------------------------------------
echo 提示：請保持伺服器命令視窗開啟，關閉命令視窗即停止服務。
pause
