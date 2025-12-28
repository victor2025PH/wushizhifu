@echo off
REM 重命名目录脚本 - 将 wushizhifu-bot 和 wushizhifu-otc-bot 重命名为 botA 和 botB

echo ==========================================
echo 重命名 Bot 目录
echo ==========================================
echo.

set "CURRENT_DIR=%~dp0"

echo 当前目录: %CURRENT_DIR%
echo.

REM 检查并重命名 botA (原 wushizhifu-bot)
if exist "%CURRENT_DIR%wushizhifu-bot" (
    if not exist "%CURRENT_DIR%botA" (
        echo 重命名 wushizhifu-bot -^> botA
        ren "%CURRENT_DIR%wushizhifu-bot" "botA"
        echo ✅ Bot A 目录已重命名
    ) else (
        echo ⚠️  botA 目录已存在，跳过
    )
) else (
    echo ℹ️  wushizhifu-bot 目录不存在
)

echo.

REM 检查并重命名 botB (原 wushizhifu-otc-bot)
if exist "%CURRENT_DIR%wushizhifu-otc-bot" (
    if not exist "%CURRENT_DIR%botB" (
        echo 重命名 wushizhifu-otc-bot -^> botB
        ren "%CURRENT_DIR%wushizhifu-otc-bot" "botB"
        echo ✅ Bot B 目录已重命名
    ) else (
        echo ⚠️  botB 目录已存在，跳过
    )
) else (
    echo ℹ️  wushizhifu-otc-bot 目录不存在
)

echo.
echo ==========================================
echo 重命名完成！
echo ==========================================
echo.
echo 请确认:
echo   1. botA/ 目录存在
echo   2. botB/ 目录存在
echo   3. .env 文件在根目录
echo.
pause

