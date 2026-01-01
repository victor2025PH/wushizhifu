#!/bin/bash
# 快速修复Nginx配置 - 确保50zf指向MiniApp，5050指向Web

echo "=========================================="
echo "🔧 修复Nginx配置"
echo "=========================================="
echo ""

# 配置文件路径
CONFIG_50ZF="/etc/nginx/sites-available/wushizhifu"
CONFIG_5050="/etc/nginx/sites-available/web-5050"

# MiniApp和Web的目录
MINIAPP_DIR="/home/ubuntu/wushizhifu/wushizhifu-full/dist"
WEB_DIR="/home/ubuntu/wushizhifu/web/dist"

echo "1. 检查目录..."
if [ ! -d "$MINIAPP_DIR" ]; then
    echo "  ❌ MiniApp目录不存在: $MINIAPP_DIR"
    exit 1
fi
echo "  ✅ MiniApp目录: $MINIAPP_DIR"

if [ ! -d "$WEB_DIR" ]; then
    echo "  ❌ Web目录不存在: $WEB_DIR"
    exit 1
fi
echo "  ✅ Web目录: $WEB_DIR"

echo ""
echo "2. 修复50zf.usdt2026.cc配置 (MiniApp)..."
if [ -f "$CONFIG_50ZF" ]; then
    # 备份
    sudo cp "$CONFIG_50ZF" "${CONFIG_50ZF}.backup.$(date +%Y%m%d_%H%M%S)"
    echo "  ✅ 已备份原配置"
    
    # 替换root路径（确保指向MiniApp）
    sudo sed -i "s|root /home/ubuntu/wushizhifu/web/dist;|root $MINIAPP_DIR;|g" "$CONFIG_50ZF"
    sudo sed -i "s|root /opt/wushizhifu/frontend/dist;|root $MINIAPP_DIR;|g" "$CONFIG_50ZF"
    
    echo "  ✅ 已更新root路径为: $MINIAPP_DIR"
else
    echo "  ⚠️  配置文件不存在: $CONFIG_50ZF"
fi

echo ""
echo "3. 修复5050.usdt2026.cc配置 (Web网站)..."
if [ -f "$CONFIG_5050" ]; then
    # 备份
    sudo cp "$CONFIG_5050" "${CONFIG_5050}.backup.$(date +%Y%m%d_%H%M%S)"
    echo "  ✅ 已备份原配置"
    
    # 替换root路径（确保指向Web）
    sudo sed -i "s|root /home/ubuntu/wushizhifu/wushizhifu-full/dist;|root $WEB_DIR;|g" "$CONFIG_5050"
    sudo sed -i "s|root /opt/wushizhifu/frontend/dist;|root $WEB_DIR;|g" "$CONFIG_5050"
    
    echo "  ✅ 已更新root路径为: $WEB_DIR"
else
    echo "  ⚠️  配置文件不存在: $CONFIG_5050"
fi

echo ""
echo "4. 测试Nginx配置..."
if sudo nginx -t; then
    echo "  ✅ Nginx配置测试通过"
    echo ""
    echo "5. 重载Nginx..."
    sudo systemctl reload nginx
    echo "  ✅ Nginx已重载"
else
    echo "  ❌ Nginx配置测试失败"
    echo "  请检查配置文件并修复错误"
    exit 1
fi

echo ""
echo "=========================================="
echo "✅ 修复完成"
echo "=========================================="
echo ""
echo "📋 当前配置:"
echo "  50zf.usdt2026.cc (MiniApp): $MINIAPP_DIR"
echo "  5050.usdt2026.cc (Web): $WEB_DIR"
echo ""
echo "🧪 验证:"
echo "  访问 https://50zf.usdt2026.cc - 应该显示MiniApp"
echo "  访问 https://5050.usdt2026.cc - 应该显示Web网站"
