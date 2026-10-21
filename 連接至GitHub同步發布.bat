@echo off
chcp 65001 >nul
cd /d "%~dp0"
title 連接至 GitHub 雲端版本庫工具

echo ========================================================
echo   電腦周邊售後風控平台 - 連接至 GitHub 雲端版本庫
echo ========================================================
echo.
echo 【專題加分指南】：
echo   將專案推送到 GitHub 是大學專題的重要加分項目！
echo   口試委員與教授可清楚檢視完整的開發軌跡與 Commit 紀錄。
echo.
echo --------------------------------------------------------
echo 步驟一：請先在 GitHub 建立一個「空白」儲存庫 (Repository)
echo   1. 前往 https://github.com/new 登入帳號。
echo   2. Repository name 輸入專案名稱 (如: peripheral-warranty-copilot)。
echo   3. 選擇 Public (公開) 或 Private (私人)。
echo   4. [重要] 切勿勾選 Add a README file 與 Add .gitignore！
echo   5. 點擊綠色按鈕 Create repository。
echo --------------------------------------------------------
echo.
set /p "repo_url=步驟二：請貼上您的 GitHub 儲存庫 HTTPS 網址: "

if "%repo_url%"=="" goto no_url
goto do_push

:no_url
echo.
echo [提示] 尚未輸入網址，已取消操作。
echo 隨時可再次點擊此工具重新輸入！
echo.
pause
exit /b

:do_push
echo.
echo [1/3] 正在設定遠端連線目標 origin...
call "%~dp0git.bat" remote remove origin 2>nul
call "%~dp0git.bat" remote add origin %repo_url%

echo [2/3] 正在設定主分支為 main...
call "%~dp0git.bat" branch -M main

echo [3/3] 正在推送所有程式碼與版本標籤至 GitHub...
echo (若系統彈出 GitHub 登入視窗，請點選「Sign in with your browser」完成授權)
call "%~dp0git.bat" push -u origin main --tags

echo.
echo ========================================================
echo [完成] 若上方顯示 Everything up-to-date 或進度 100%%，
echo        代表已成功同步至 GitHub！請至網頁重新整理檢視成果。
echo ========================================================
echo.
pause
