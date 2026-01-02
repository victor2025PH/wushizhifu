#!/bin/bash
# 安装 qrcode 库到 bot 的虚拟环境

echo "=========================================="
echo "🔧 安装 QR Code 生成库"
echo "=========================================="

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "📁 项目目录: $PROJECT_DIR"

# 方法1: 检查是否有虚拟环境
if [ -d "$PROJECT_DIR/venv" ]; then
    echo "✅ 找到虚拟环境: $PROJECT_DIR/venv"
    VENV_PYTHON="$PROJECT_DIR/venv/bin/python"
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
        else
            echo "❌ 虚拟环境安装失败"
        fi
    fi
fi

# 方法2: 检查 botB 目录下的虚拟环境
if [ -d "$SCRIPT_DIR/venv" ]; then
    echo "✅ 找到虚拟环境: $SCRIPT_DIR/venv"
    VENV_PYTHON="$SCRIPT_DIR/venv/bin/python"
    VENV_PIP="$SCRIPT_DIR/venv/bin/pip"
    
    if [ -f "$VENV_PIP" ]; then
        echo "📦 在虚拟环境中安装 qrcode[pil]..."
        "$VENV_PIP" install qrcode[pil]
        if [ $? -eq 0 ]; then
            echo "✅ 安装成功！"
            echo ""
            echo "🔄 请重启 bot 服务："
            echo "   sudo systemctl restart otc-bot.service"
            exit 0
        else
            echo "❌ 虚拟环境安装失败"
        fi
    fi
fi

# 方法3: 检查 systemd 服务配置，找到实际使用的 Python
if [ -f "/etc/systemd/system/otc-bot.service" ]; then
    echo "📋 检查 systemd 服务配置..."
    EXEC_START=$(grep "^ExecStart=" /etc/systemd/system/otc-bot.service | cut -d'=' -f2- | awk '{print $1}')
    WORK_DIR=$(grep "^WorkingDirectory=" /etc/systemd/system/otc-bot.service | cut -d'=' -f2-)
    
    if [ -n "$EXEC_START" ]; then
        echo "🔍 服务使用的 Python: $EXEC_START"
        PYTHON_DIR=$(dirname "$EXEC_START")
        PIP_PATH="$PYTHON_DIR/pip"
        
        if [ -f "$PIP_PATH" ]; then
            echo "📦 使用服务配置的 pip 安装 qrcode[pil]..."
            "$PIP_PATH" install qrcode[pil]
            if [ $? -eq 0 ]; then
                echo "✅ 安装成功！"
                echo ""
                echo "🔄 请重启 bot 服务："
                echo "   sudo systemctl restart otc-bot.service"
                exit 0
            else
                echo "❌ 安装失败"
            fi
        fi
    fi
    
    if [ -n "$WORK_DIR" ]; then
        echo "📁 工作目录: $WORK_DIR"
        if [ -d "$WORK_DIR/venv" ]; then
            VENV_PIP="$WORK_DIR/venv/bin/pip"
            if [ -f "$VENV_PIP" ]; then
                echo "📦 在工作目录的虚拟环境中安装 qrcode[pil]..."
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
    fi
fi

# 方法4: 尝试使用当前 Python 环境
echo "📦 尝试使用当前 Python 环境安装..."
python3 -m pip install --user qrcode[pil] 2>/dev/null || pip3 install --user qrcode[pil] 2>/dev/null

if python3 -c "import qrcode" 2>/dev/null; then
    echo "✅ 安装成功（用户级）！"
    echo ""
    echo "⚠️  注意：如果 bot 运行在虚拟环境中，可能仍无法使用"
    echo "🔄 请重启 bot 服务："
    echo "   sudo systemctl restart otc-bot.service"
    exit 0
fi

# 如果都失败了
echo ""
echo "❌ 所有安装方法都失败了"
echo ""
echo "请手动执行以下步骤："
echo ""
echo "1. 找到 bot 实际使用的 Python 路径："
echo "   sudo systemctl status otc-bot.service | grep 'Main PID'"
echo "   ps aux | grep bot.py"
echo ""
echo "2. 使用该 Python 的 pip 安装："
echo "   /path/to/python -m pip install qrcode[pil]"
echo ""
echo "3. 或者找到虚拟环境并激活："
echo "   source /path/to/venv/bin/activate"
echo "   pip install qrcode[pil]"
echo ""
echo "4. 重启服务："
echo "   sudo systemctl restart otc-bot.service"

exit 1
