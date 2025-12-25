@echo off
REM 推送 Bot 代碼到現有的 GitHub 倉庫
REM 倉庫: https://github.com/victor2025PH/wushizhifu

echo ==========================================
echo 推送 Bot 代碼到 GitHub 倉庫
echo 倉庫: https://github.com/victor2025PH/wushizhifu
echo ==========================================
echo.

REM 檢查是否已初始化 Git
if not exist ".git" (
    echo 初始化 Git 倉庫...
    git init
    git branch -M main
    echo ✅ Git 倉庫已初始化
    echo.
) else (
    echo ✅ Git 倉庫已存在
    echo.
)

REM 檢查遠程倉庫
git remote show origin >nul 2>&1
if %errorlevel% neq 0 (
    echo 添加遠程倉庫...
    git remote add origin https://github.com/victor2025PH/wushizhifu.git
    echo ✅ 遠程倉庫已添加
    echo.
) else (
    echo 當前遠程倉庫:
    git remote -v
    echo.
    set /p change="是否要更改遠程倉庫？(Y/N): "
    if /i "%change%"=="Y" (
        git remote set-url origin https://github.com/victor2025PH/wushizhifu.git
        echo ✅ 遠程倉庫已更新
        echo.
    )
)

REM 添加所有文件
echo 添加文件到 Git...
git add .

REM 顯示狀態
echo.
echo 📋 準備提交的文件：
git status
echo.

REM 提示用戶確認
set /p confirm="確認提交這些文件？(Y/N): "
if /i not "%confirm%"=="Y" (
    echo 已取消
    pause
    exit /b
)

REM 提交
echo.
echo 提交更改...
git commit -m "Add: WuShiPay Telegram Bot - Complete bot implementation with database, handlers, and deployment scripts"
echo ✅ 已提交
echo.

REM 提示推送
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
        echo 訪問倉庫: https://github.com/victor2025PH/wushizhifu
    ) else (
        echo.
        echo ⚠️  推送失敗，可能需要：
        echo   1. 確認倉庫存在且有寫入權限
        echo   2. 如果遠程有內容，可能需要先拉取：git pull origin main --allow-unrelated-histories
        echo   3. 然後再推送：git push -u origin main
    )
) else (
    echo 已跳過推送
    echo.
    echo 手動推送命令：
    echo   git push -u origin main
)

echo.
echo ✅ 完成！
pause

