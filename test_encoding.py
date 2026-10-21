# -*- coding: utf-8 -*-
import subprocess

# 1. 連接至GitHub同步發布.bat
github_bat = """@echo off
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

if "%repo_url%"=="" (
    echo.
    echo [提示] 尚未輸入網址，已取消操作。
    echo 隨時可再次點擊此工具重新輸入！
    echo.
    pause
    exit /b
)

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
"""

# 2. 一鍵建立版本存檔.bat
save_bat = """@echo off
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
call "%~dp0git.bat" log -n 5 --pretty=format:"  * [%%h] %%s (%%cr) %%d"
echo.
echo.
pause
"""

# 3. 一鍵回溯歷史版本.bat
rollback_bat = """@echo off
chcp 65001 >nul
cd /d "%~dp0"
title 系統版本回溯工具 (Git Rollback)

echo ========================================================
echo   電腦周邊售後風控平台 - 一鍵版本回溯工具 (Git)
echo ========================================================
echo.
echo 當網站遭遇重大 BUG 或改壞時，可透過此工具「時光倒流」回到先前的正常存檔點！
echo.
echo --------------------------------------------------------
echo [歷史存檔清單] (最上方為最新版本)：
echo --------------------------------------------------------
call "%~dp0git.bat" log -n 10 --pretty=format:"  [%%h] %%s (%%cr) %%d"
echo.
echo --------------------------------------------------------
echo.
echo 常用快捷回溯選項：
echo   [1] 放棄未存檔的修改 (重置所有檔案回到最後一次存檔點)
echo   [2] 回溯到上一個版本 (HEAD~1，退回前一次存檔)
echo   [3] 輸入指定的 Commit 雜湊碼 (例如: 45633a3 或 v1.0.0)
echo   [Q] 取消離開
echo.
set /p "choice=請選擇回溯方式 [1/2/3/Q]: "

if /i "%choice%"=="1" (
    echo.
    echo 正在重置所有修改回到最新存檔點...
    call "%~dp0git.bat" restore .
    call "%~dp0git.bat" clean -fd
    echo [完成] 已成功清除未存檔的修改，檔案已恢復如初！
    goto end
)

if /i "%choice%"=="2" (
    echo.
    echo 正在回溯到上一個穩定版本 (HEAD~1)...
    call "%~dp0git.bat" reset --hard HEAD~1
    echo [完成] 已成功回溯至上一個版本！
    goto end
)

if /i "%choice%"=="3" (
    echo.
    set /p "target_hash=請輸入欲回溯的 Commit 雜湊碼 (前 7 碼) 或標籤 (如 v1.0.0): "
    if not "%target_hash%"=="" (
        echo 正在回溯至 %target_hash% ...
        call "%~dp0git.bat" reset --hard %target_hash%
        echo [完成] 已成功回溯至指定的版本 [%target_hash%]！
    )
    goto end
)

echo 取消回溯操作。

:end
echo.
echo 當前專案最新版本狀態：
call "%~dp0git.bat" log -n 1 --oneline --decorate
echo.
pause
"""

files = {
    'D:/10777/10777/連接至GitHub同步發布.bat': github_bat,
    'D:/10777/10777/一鍵建立版本存檔.bat': save_bat,
    'D:/10777/10777/一鍵回溯歷史版本.bat': rollback_bat
}

for path, content in files.items():
    with open(path, 'w', encoding='utf-8', newline='\r\n') as f:
        f.write(content)
    print(f"Written {path}")

# Test running github_bat with empty input (should print prompt and pause cleanly)
p = subprocess.run(['cmd.exe', '/c', 'D:\\10777\\10777\\連接至GitHub同步發布.bat'], input='\n\n', capture_output=True, text=True, encoding='utf-8', errors='ignore')
print('Exit code:', p.returncode)
print('STDOUT:\n', p.stdout)
print('STDERR:\n', p.stderr)
