#!/bin/bash
# 诊断视频功能问题

set -e

echo "=========================================="
echo "🔍 Bot A 视频功能诊断工具"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_DIR="/home/ubuntu/wushizhifu/botA"
SERVICE_NAME="wushizhifu-bot"

echo -e "${BLUE}项目目录: ${PROJECT_DIR}${NC}"
echo ""

# 1. 检查 Bot A 服务状态
echo -e "${YELLOW}1️⃣  检查 Bot A 服务状态...${NC}"
if systemctl is-active --quiet ${SERVICE_NAME}; then
    echo -e "${GREEN}✅ Bot A 服务正在运行${NC}"
    systemctl status ${SERVICE_NAME} --no-pager -l | head -10
else
    echo -e "${RED}❌ Bot A 服务未运行${NC}"
    echo "启动服务："
    echo "  sudo systemctl start ${SERVICE_NAME}"
    exit 1
fi

# 2. 检查日志中是否有频道视频相关错误
echo ""
echo -e "${YELLOW}2️⃣  检查最近的日志...${NC}"
echo "查找频道视频相关日志："
sudo journalctl -u ${SERVICE_NAME} -n 100 --no-pager | grep -i "channel\|video\|频道\|视频" | tail -20 || echo "未找到相关日志"

# 3. 检查频道 ID 配置
echo ""
echo -e "${YELLOW}3️⃣  检查频道 ID 配置...${NC}"
if [ -f "${PROJECT_DIR}/handlers/channel_video_handler.py" ]; then
    CURRENT_ID=$(grep "VIDEO_CHANNEL_ID" "${PROJECT_DIR}/handlers/channel_video_handler.py" | grep -oE "-?[0-9]+" | head -1)
    echo -e "${BLUE}当前配置的频道 ID: ${CURRENT_ID}${NC}"
    echo ""
    echo "如果需要更新频道 ID："
    echo "1. 运行获取频道 ID 工具："
    echo "   cd ${PROJECT_DIR}"
    echo "   source venv/bin/activate"
    echo "   python3 获取频道ID.py"
    echo ""
    echo "2. 更新 botA/handlers/channel_video_handler.py 中的 VIDEO_CHANNEL_ID"
    echo "3. 重启 Bot A 服务"
else
    echo -e "${RED}❌ 找不到 channel_video_handler.py${NC}"
fi

# 4. 检查数据库中的视频配置
echo ""
echo -e "${YELLOW}4️⃣  检查数据库中的视频配置...${NC}"
cd "${PROJECT_DIR}"
if [ -d "venv" ]; then
    source venv/bin/activate
    python3 << 'PYEOF'
import sys
sys.path.insert(0, '.')
try:
    from database.video_repository import VideoRepository
    configs = VideoRepository.get_all_video_configs()
    if configs:
        print("✅ 已配置的视频：")
        for config in configs:
            print(f"  类型: {config['video_type']}")
            print(f"  频道 ID: {config['channel_id']}")
            print(f"  消息 ID: {config['message_id']}")
            print(f"  更新时间: {config.get('updated_at', 'N/A')}")
            print()
    else:
        print("⚠️  数据库中暂无视频配置")
except Exception as e:
    print(f"❌ 检查数据库失败: {e}")
PYEOF
else
    echo -e "${YELLOW}⚠️  虚拟环境不存在，跳过数据库检查${NC}"
fi

# 5. 检查管理员列表
echo ""
echo -e "${YELLOW}5️⃣  检查管理员列表...${NC}"
cd "${PROJECT_DIR}"
if [ -d "venv" ]; then
    source venv/bin/activate
    python3 << 'PYEOF'
import sys
sys.path.insert(0, '.')
try:
    from database.admin_repository import AdminRepository
    admins = AdminRepository.get_all_admins()
    if admins:
        print("✅ 管理员列表：")
        for admin in admins:
            print(f"  用户 ID: {admin['user_id']}")
            print(f"  用户名: {admin.get('username', 'N/A')}")
            print()
    else:
        print("⚠️  没有找到管理员")
        print("  视频询问消息无法发送")
except Exception as e:
    print(f"❌ 检查管理员失败: {e}")
PYEOF
else
    echo -e "${YELLOW}⚠️  虚拟环境不存在，跳过管理员检查${NC}"
fi

# 6. 测试频道访问权限（需要手动检查）
echo ""
echo -e "${YELLOW}6️⃣  手动检查项...${NC}"
echo "请手动确认："
echo "1. ✅ Bot A 已添加到频道作为管理员"
echo "2. ✅ Bot A 有查看频道消息的权限"
echo "3. ✅ 频道 ID 是否正确"
echo ""
echo "获取频道 ID 的方法："
echo "  cd ${PROJECT_DIR}"
echo "  source venv/bin/activate"
echo "  python3 获取频道ID.py"

echo ""
echo -e "${GREEN}=========================================="
echo "✅ 诊断完成"
echo "==========================================${NC}"

