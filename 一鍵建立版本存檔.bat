@echo off
chcp 65001 >nul
cd /d "%~dp0"
title 系統版本存檔工具 (Git Checkpoint)

echo ========================================================
echo   電腦周邊售後風控平台 - 一鍵版本存檔工具 (Git)
echo ========================================================
echo.
echo 目前專案變更狀態：
call "%~dp0git.bat" status -s
echo.
echo --------------------------------------------------------
set /p "commit_msg=請輸入本次修改的說明 (例如: 修改了按鈕顏色 / 直接按 Enter 使用預設): "
if "%commit_msg%"=="" (
    set "commit_msg=更新系統功能與穩定性優化 [%date% %time:~0,5%]"
)

echo.
echo [1/2] 正在收錄所有變更檔案...
call "%~dp0git.bat" add .

echo [2/2] 正在建立歷史存檔點...
call "%~dp0git.bat" commit -m "%commit_msg%"

echo.
echo ========================================================
echo [完成] 版本存檔成功！近期存檔紀錄如下：
echo ========================================================
call "%~dp0git.bat" log -n 5 --oneline
echo.
pause
