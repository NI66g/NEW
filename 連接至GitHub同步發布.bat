@echo off
chcp 65001 >nul
cd /d "%~dp0"
title 連接至 GitHub 同步發布工具

echo ========================================================
echo   🐙 電腦周邊售後風控平台 · 連接至 GitHub 雲端版本庫
echo ========================================================
echo.
echo 【專題加分指南】：
echo   將專案推送到 GitHub 是大學專題的重要加分項！
echo   評審教授與口試委員可清楚看見完整的開發軌跡、Commit 紀錄、
echo   分支演進與 Release 發布標籤，展現極高之軟體工程規範水準。
echo.
echo --------------------------------------------------------
echo 步驟一：請先在 GitHub 建立一個空白儲存庫 (Repository)
echo   1. 前往 https://github.com/new 登入帳號。
echo   2. Repository name 填寫專案名稱 (如: peripheral-return-risk-copilot)。
echo   3. 選擇 Public (公開) 或 Private (私人)。
echo   4. ★切記：不要勾選「Add a README file」與「Add .gitignore」！
echo   5. 點擊「Create repository」。
echo --------------------------------------------------------
echo.
set /p "repo_url=步驟二：請貼上您的 GitHub 儲存庫 HTTPS 網址: "

if "%repo_url%"=="" (
    echo.
    echo 尚未輸入網址，已取消同步。
    echo 提示：日後隨時可再次點擊此腳本進行連接！
    echo.
    pause
    exit /b
)

echo.
echo [1/3] 設定遠端連線目標 origin...
"%~dp0git.bat" remote remove origin 2>nul
"%~dp0git.bat" remote add origin %repo_url%

echo [2/3] 設定預設分支為 main...
"%~dp0git.bat" branch -M main

echo [3/3] 正在推送到 GitHub (包含所有存檔與 v1.0.0 標籤)...
echo (若彈出 GitHub 登入視窗，請點選「Sign in with your browser」授權完成)
"%~dp0git.bat" push -u origin main --tags

echo.
echo ========================================================
echo ✅ 操作完成！若推送成功，請開啟您的 GitHub 頁面檢視專題成果！
echo ========================================================
echo.
pause
