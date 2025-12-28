@echo off
REM 完整整理和推送腳本：分離前端和 Bot，然後推送到 GitHub

setlocal enabledelayedexpansion

echo ==========================================
echo 整理項目：分離前端和 Bot 代碼
echo ==========================================
echo.

set "BASE_DIR=%~dp0"
set "BOT_DIR=%BASE_DIR%wushizhifu-bot"
set "FRONTEND_DIR=%BASE_DIR%wushizhifu-frontend"

echo 📁 基礎目錄: %BASE_DIR%
echo 🤖 Bot 目錄: %BOT_DIR%
echo 🌐 前端目錄: %FRONTEND_DIR%
echo.

REM ==========================================
REM 步驟 1: 創建目錄
REM ==========================================
echo [步驟 1] 創建目錄結構...
if not exist "%BOT_DIR%" mkdir "%BOT_DIR%"
if not exist "%FRONTEND_DIR%" mkdir "%FRONTEND_DIR%"
echo ✅ 目錄創建完成
echo.

REM ==========================================
REM 步驟 2: 複製 Bot 文件
REM ==========================================
echo [步驟 2] 複製 Bot 代碼文件...

REM Bot 核心文件
for %%f in (bot.py config.py requirements.txt) do (
    if exist "%%f" (
        copy /Y "%%f" "%BOT_DIR%\" >nul 2>&1
        echo   ✅ %%f
    )
)

REM Bot 目錄結構
for %%d in (database handlers keyboards middleware services utils deploy) do (
    if exist "%%d" (
        xcopy /E /I /Y /Q "%%d" "%BOT_DIR%\%%d\" >nul 2>&1
        echo   ✅ %%d\
    )
)

REM Bot 相關文檔（排除前端相關的）
for %%f in (README_BOT.md ARCHITECTURE.md FUNCTIONAL_DESIGN.md IMPLEMENTATION_SUMMARY.md IMPROVEMENTS.md USER_FLOW_DIAGRAM.md DEPLOYMENT.md SEPARATE_REPOS.md PUSH_TO_GITHUB.md PUSH_TO_EXISTING_REPO.md QUICK_PUSH.md GITHUB_SETUP.md ORGANIZE_PROJECT.md) do (
    if exist "%%f" (
        copy /Y "%%f" "%BOT_DIR%\" >nul 2>&1
        echo   ✅ %%f
    )
)

REM Git 配置文件
if exist ".gitignore" copy /Y ".gitignore" "%BOT_DIR%\" >nul 2>&1
if exist ".gitattributes" copy /Y ".gitattributes" "%BOT_DIR%\" >nul 2>&1

REM 使用 README_BOT.md 作為 README（如果存在）
if exist "README_BOT.md" (
    copy /Y "README_BOT.md" "%BOT_DIR%\README.md" >nul 2>&1
    echo   ✅ README.md (從 README_BOT.md)
)

echo ✅ Bot 文件複製完成
echo.

REM ==========================================
REM 步驟 3: 複製前端文件
REM ==========================================
echo [步驟 3] 複製前端代碼文件...

if exist "wushizhifu-full" (
    echo   從 wushizhifu-full 目錄複製前端文件...
    
    REM 複製所有文件，但排除 bot 目錄
    xcopy /E /I /Y /H "wushizhifu-full\*" "%FRONTEND_DIR%\" >nul 2>&1
    
    REM 刪除 bot 目錄（如果存在）
    if exist "%FRONTEND_DIR%\bot" (
        rmdir /S /Q "%FRONTEND_DIR%\bot" >nul 2>&1
        echo   ❌ 已排除 bot\ 目錄
    )
    
    echo ✅ 前端文件複製完成
    echo   提示：前端代碼主要從 GitHub 倉庫獲取，此處僅作為備份
) else (
    echo   ⚠️  未找到 wushizhifu-full 目錄
    echo   前端代碼將直接從 GitHub 倉庫克隆
)

echo.

REM ==========================================
REM 步驟 4: 清理不需要的文件
REM ==========================================
echo [步驟 4] 清理不需要的文件...

REM 清理 Bot 目錄
cd /d "%BOT_DIR%"
if exist "wushipay.db" del /Q "wushipay.db" >nul 2>&1
if exist "__pycache__" rmdir /S /Q "__pycache__" >nul 2>&1
for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /S /Q "%%d" >nul 2>&1

REM 清理前端目錄（如果有）
cd /d "%FRONTEND_DIR%"
if exist "node_modules" rmdir /S /Q "node_modules" >nul 2>&1
if exist "dist" rmdir /S /Q "dist" >nul 2>&1

cd /d "%BASE_DIR%"
echo ✅ 清理完成
echo.

REM ==========================================
REM 完成
REM ==========================================
echo ==========================================
echo ✅ 整理完成！
echo ==========================================
echo.
echo 📁 目錄結構：
echo.
echo %BASE_DIR%
echo ├── wushizhifu-bot\       (Bot 代碼)
echo └── wushizhifu-frontend\  (前端代碼)
echo.
echo 下一步：
echo 1. 檢查 wushizhifu-bot 目錄
echo 2. 檢查 wushizhifu-frontend 目錄
echo 3. 分別推送到 GitHub
echo.
echo 推送命令：
echo   cd wushizhifu-bot
echo   git init
echo   git add .
echo   git commit -m "Initial commit"
echo   git remote add origin https://github.com/victor2025PH/wushizhifu_bot.git
echo   git push -u origin main
echo.
echo   cd ..\wushizhifu-frontend
echo   git init
echo   git add .
echo   git commit -m "Initial commit"
echo   git remote add origin https://github.com/victor2025PH/wushizhifu.git
echo   git push -u origin main
echo.
pause

