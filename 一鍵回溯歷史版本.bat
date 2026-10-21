@echo off
chcp 65001 >nul
cd /d "%~dp0"
title 系統版本回溯工具 (Git Rollback)

echo ========================================================
echo   🚨 電腦周邊售後風控平台 · 一鍵版本回溯工具 (Git)
echo ========================================================
echo.
echo 當網站遭遇重大 BUG 或程式碼改壞時，可透過此工具「時光倒流」回到先前的正常存檔點！
echo.
echo --------------------------------------------------------
echo 📜 近期版本存檔清單 (最上方為最新版本)：
echo --------------------------------------------------------
"%~dp0git.bat" log -n 10 --pretty=format:"  [%%h] %%s (%%cr) %%d"
echo.
echo --------------------------------------------------------
echo.
echo 常用快捷回溯選項：
echo   [1] 放棄未存檔的修改（重置目前所有檔案回到最後一次存檔點）
echo   [2] 回溯到上一個版本（退回前一次存檔）
echo   [3] 輸入指定的 Commit 雜湊碼 (例如: c272a80 或 v1.0.0)
echo   [Q] 取消離開
echo.
set /p "choice=請選擇回溯方式 [1/2/3/Q]: "

if /i "%choice%"=="1" (
    echo.
    echo 正在重置所有修改回到最新存檔點...
    "%~dp0git.bat" restore .
    "%~dp0git.bat" clean -fd
    echo ✅ 已成功清除未存檔的修改，檔案已恢復如初！
    goto end
)

if /i "%choice%"=="2" (
    echo.
    echo 正在回溯到上一個穩定版本 (HEAD~1)...
    "%~dp0git.bat" reset --hard HEAD~1
    echo ✅ 已成功回溯至上一個版本！
    goto end
)

if /i "%choice%"=="3" (
    echo.
    set /p "target_hash=請輸入欲回溯的 Commit 雜湊碼 (前 7 碼) 或標籤 (如 v1.0.0): "
    if not "%target_hash%"=="" (
        echo 正在回溯至 %target_hash% ...
        "%~dp0git.bat" reset --hard %target_hash%
        echo ✅ 已成功回溯至指定的版本 [%target_hash%]！
    )
    goto end
)

echo 取消回溯操作。

:end
echo.
echo 當前專案最新版本狀態：
"%~dp0git.bat" log -n 1 --oneline --decorate
echo.
pause
