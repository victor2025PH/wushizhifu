#!/bin/bash
# 安装 qrcode 库到 bot 的虚拟环境

echo "=========================================="
echo "🔧 安装 QR Code 生成库"
echo "=========================================="

# 方法1: 从 systemd 服务配置获取虚拟环境路径（最准确）
if [ -f "/etc/systemd/system/otc-bot.service" ]; then
    echo "📋 检查 systemd 服务配置..."
    EXEC_START=$(grep "^ExecStart=" /etc/systemd/system/otc-bot.service | cut -d'=' -f2- | awk '{print $1}')
    WORK_DIR=$(grep "^WorkingDirectory=" /etc/systemd/system/otc-bot.service | cut -d'=' -f2-)
    
    if [ -n "$EXEC_START" ] && [ -f "$EXEC_START" ]; then
        echo "🔍 服务使用的 Python: $EXEC_START"
        PYTHON_DIR=$(dirname "$EXEC_START")
        PIP_PATH="$PYTHON_DIR/pip"
        
        if [ -f "$PIP_PATH" ]; then
            echo "📦 使用服务配置的 pip 安装 qrcode[pil]..."
            "$PIP_PATH" install qrcode[pil]
            if [ $? -eq 0 ]; then
                echo "✅ 安装成功！"
                echo ""
                echo "🔄 正在重启 bot 服务..."
                sudo systemctl restart otc-bot.service
                sleep 2
                echo "✅ 服务已重启"
                echo ""
                echo "📋 验证安装（查看日志）："
                echo "   sudo journalctl -u otc-bot.service -n 20 | grep -i qrcode"
                exit 0
            else
                echo "❌ 安装失败，尝试其他方法..."
            fi
        fi
    fi
    
    if [ -n "$WORK_DIR" ] && [ -d "$WORK_DIR/venv" ]; then
        echo "📁 工作目录: $WORK_DIR"
        VENV_PIP="$WORK_DIR/venv/bin/pip"
        if [ -f "$VENV_PIP" ]; then
            echo "📦 在工作目录的虚拟环境中安装 qrcode[pil]..."
            "$VENV_PIP" install qrcode[pil]
            if [ $? -eq 0 ]; then
                echo "✅ 安装成功！"
                echo ""
                echo "🔄 正在重启 bot 服务..."
                sudo systemctl restart otc-bot.service
                sleep 2
                echo "✅ 服务已重启"
                exit 0
            fi
        fi
    fi
fi

# 方法2: 检查常见的项目路径
COMMON_PATHS=(
    "/home/ubuntu/wushizhifu/botB"
    "/home/ubuntu/wushizhifu/otc-bot"
    "$HOME/wushizhifu/botB"
    "$HOME/wushizhifu/otc-bot"
)

for PROJECT_DIR in "${COMMON_PATHS[@]}"; do
    if [ -d "$PROJECT_DIR/venv" ]; then
        echo "✅ 找到虚拟环境: $PROJECT_DIR/venv"
        VENV_PIP="$PROJECT_DIR/venv/bin/pip"
        
        if [ -f "$VENV_PIP" ]; then
            echo "📦 在虚拟环境中安装 qrcode[pil]..."
            "$VENV_PIP" install qrcode[pil]
            if [ $? -eq 0 ]; then
                echo "✅ 安装成功！"
                echo ""
                echo "🔄 请重启 bot 服务："
                echo "   sudo systemctl restart otc-bot.service"
                exit 0
            fi
        fi
    fi
done

# 方法3: 检查当前目录
if [ -d "./venv" ]; then
    echo "✅ 找到当前目录的虚拟环境: ./venv"
    if [ -f "./venv/bin/pip" ]; then
        echo "📦 在虚拟环境中安装 qrcode[pil]..."
        ./venv/bin/pip install qrcode[pil]
        if [ $? -eq 0 ]; then
            echo "✅ 安装成功！"
            echo ""
            echo "🔄 请重启 bot 服务："
            echo "   sudo systemctl restart otc-bot.service"
            exit 0
        fi
    fi
fi

# 如果都失败了，提供手动安装指南
echo ""
echo "❌ 自动检测失败，请手动安装"
echo ""
echo "请按照以下步骤操作："
echo ""
echo "1. 找到 bot 的虚拟环境路径："
echo "   sudo cat /etc/systemd/system/otc-bot.service | grep ExecStart"
echo ""
echo "2. 使用该路径的 pip 安装（例如）："
echo "   /home/ubuntu/wushizhifu/botB/venv/bin/pip install qrcode[pil]"
echo ""
echo "3. 或者进入项目目录并激活虚拟环境："
echo "   cd /home/ubuntu/wushizhifu/botB"
echo "   source venv/bin/activate"
echo "   pip install qrcode[pil]"
echo "   deactivate"
echo ""
echo "4. 重启服务："
echo "   sudo systemctl restart otc-bot.service"
echo ""
echo "5. 验证安装："
echo "   sudo journalctl -u otc-bot.service -n 20 | grep -i qrcode"

exit 1
