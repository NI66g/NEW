@echo off
cd /d "%~dp0"
title 連接至 GitHub 同步發布工具

echo ========================================================
echo   電腦周邊售後風控平台 - 連接至 GitHub 雲端版本庫
echo ========================================================
echo.
echo 正在檢查 Git 狀態...
call "%~dp0git.bat" status
echo.
echo 測試成功！請按任意鍵結束。
pause
