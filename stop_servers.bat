@echo off
chcp 65001 >nul
echo 正在停止所有退換貨風控系統服務 (Port 8501 與 8502)...
taskkill /F /IM streamlit.exe >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8501 :8502"') do (
    taskkill /F /PID %%a >nul 2>&1
)
echo ✅ 已成功停止所有退換貨風控伺服器服務！
pause
