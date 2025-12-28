@echo off
REM 推送 Bot 代碼到 GitHub 倉庫 wushizhifu_bot

echo ==========================================
echo 推送 Bot 代碼到 GitHub
echo 倉庫: https://github.com/victor2025PH/wushizhifu_bot
echo ==========================================
echo.

cd /d "%~dp0wushizhifu-bot"

if not exist "bot.py" (
    echo ❌ 錯誤：未找到 Bot 代碼，請先運行 organize_and_push.bat 整理項目
    pause
    exit /b 1
)

echo 當前目錄: %CD%
echo.

REM 初始化 Git
if not exist ".git" (
    echo 初始化 Git 倉庫...
    git init
    git branch -M main
    echo ✅ Git 倉庫已初始化
    echo.
)

REM 檢查遠程倉庫
git remote show origin >nul 2>&1
if errorlevel 1 (
    echo 添加遠程倉庫...
    git remote add origin https://github.com/victor2025PH/wushizhifu_bot.git
    echo ✅ 遠程倉庫已添加
) else (
    echo 當前遠程倉庫:
    git remote -v
    echo.
    set /p change="是否要更新遠程倉庫？(Y/N): "
    if /i "!change!"=="Y" (
        git remote set-url origin https://github.com/victor2025PH/wushizhifu_bot.git
        echo ✅ 遠程倉庫已更新
    )
)

echo.
echo 添加文件到 Git...
git add .

echo.
echo 📋 準備提交的文件：
git status
echo.

set /p confirm="確認提交這些文件？(Y/N): "
if /i not "%confirm%"=="Y" (
    echo 已取消
    pause
    exit /b
)

echo.
echo 提交更改...
git commit -m "Initial commit: WuShiPay Telegram Bot - Complete implementation with database, handlers, admin system, and deployment scripts"
echo ✅ 已提交
echo.

set /p push="是否要推送到 GitHub？(Y/N): "
if /i "%push%"=="Y" (
    echo.
    echo 推送到 GitHub...
    git push -u origin main
    if %errorlevel% equ 0 (
        echo.
        echo ✅ 推送成功！
        echo.
        echo 訪問倉庫: https://github.com/victor2025PH/wushizhifu_bot
    ) else (
        echo.
        echo ⚠️  推送失敗
        echo 可能的原因：
        echo   1. 倉庫不存在或無權限
        echo   2. 需要身份驗證（使用 Personal Access Token）
        echo   3. 遠程倉庫已有內容，需要先拉取
    )
) else (
    echo 已跳過推送
    echo.
    echo 手動推送命令：
    echo   git push -u origin main
)

echo.
pause

