#!/bin/bash
# 修复MiniApp和Web网站的Nginx配置

echo "=========================================="
echo "🔧 修复Nginx配置 - MiniApp和Web网站"
echo "=========================================="
echo ""

# 检查当前配置
echo "1. 检查当前Nginx配置..."
echo ""

echo "📋 当前50zf.usdt2026.cc配置:"
sudo nginx -T 2>/dev/null | grep -A 5 "server_name 50zf.usdt2026.cc" | grep "root" || echo "  未找到root配置"

echo ""
echo "📋 当前5050.usdt2026.cc配置:"
sudo nginx -T 2>/dev/null | grep -A 5 "server_name 5050.usdt2026.cc" | grep "root" || echo "  未找到root配置"

echo ""
echo "2. 检查目录结构..."
echo ""

# 检查MiniApp目录
MINIAPP_DIRS=(
    "/home/ubuntu/wushizhifu/wushizhifu-full/dist"
    "/opt/wushizhifu/frontend/dist"
    "/home/ubuntu/wushizhifu/frontend/dist"
)

MINIAPP_DIR=""
for dir in "${MINIAPP_DIRS[@]}"; do
    if [ -d "$dir" ] && [ -f "$dir/index.html" ]; then
        MINIAPP_DIR="$dir"
        echo "  ✅ 找到MiniApp目录: $dir"
        break
    fi
done

if [ -z "$MINIAPP_DIR" ]; then
    echo "  ❌ 未找到MiniApp的dist目录"
    echo "  请检查以下目录是否存在:"
    for dir in "${MINIAPP_DIRS[@]}"; do
        echo "    - $dir"
    done
    exit 1
fi

# 检查Web目录
WEB_DIR="/home/ubuntu/wushizhifu/web/dist"
if [ -d "$WEB_DIR" ] && [ -f "$WEB_DIR/index.html" ]; then
    echo "  ✅ 找到Web网站目录: $WEB_DIR"
else
    echo "  ❌ 未找到Web网站的dist目录: $WEB_DIR"
    exit 1
fi

echo ""
echo "3. 修复50zf.usdt2026.cc配置 (MiniApp)..."
echo ""

# 查找现有的配置文件
NGINX_CONFIG_50ZF=""
CONFIG_FILES=(
    "/etc/nginx/sites-available/50zf.usdt2026.cc"
    "/etc/nginx/sites-available/wushizhifu"
    "/etc/nginx/sites-available/miniapp"
)

for config in "${CONFIG_FILES[@]}"; do
    if [ -f "$config" ]; then
        if grep -q "server_name 50zf.usdt2026.cc" "$config" 2>/dev/null; then
            NGINX_CONFIG_50ZF="$config"
            echo "  ✅ 找到配置文件: $config"
            break
        fi
    fi
done

if [ -z "$NGINX_CONFIG_50ZF" ]; then
    NGINX_CONFIG_50ZF="/etc/nginx/sites-available/50zf.usdt2026.cc"
    echo "  📝 创建新配置文件: $NGINX_CONFIG_50ZF"
fi

# 备份原配置
if [ -f "$NGINX_CONFIG_50ZF" ]; then
    sudo cp "$NGINX_CONFIG_50ZF" "${NGINX_CONFIG_50ZF}.backup.$(date +%Y%m%d_%H%M%S)"
    echo "  ✅ 已备份原配置"
fi

# 更新root路径
sudo sed -i "s|root.*;|root $MINIAPP_DIR;|g" "$NGINX_CONFIG_50ZF" 2>/dev/null || {
    echo "  ⚠️  无法自动更新，请手动编辑: $NGINX_CONFIG_50ZF"
    echo "  确保 root 指向: $MINIAPP_DIR"
}

echo ""
echo "4. 修复5050.usdt2026.cc配置 (Web网站)..."
echo ""

NGINX_CONFIG_5050="/etc/nginx/sites-available/web-5050"
if [ -f "$NGINX_CONFIG_5050" ]; then
    # 备份
    sudo cp "$NGINX_CONFIG_5050" "${NGINX_CONFIG_5050}.backup.$(date +%Y%m%d_%H%M%S)"
    echo "  ✅ 已备份原配置"
    
    # 更新root路径
    sudo sed -i "s|root.*;|root $WEB_DIR;|g" "$NGINX_CONFIG_5050" 2>/dev/null || {
        echo "  ⚠️  无法自动更新，请手动编辑: $NGINX_CONFIG_5050"
        echo "  确保 root 指向: $WEB_DIR"
    }
else
    echo "  ⚠️  配置文件不存在: $NGINX_CONFIG_5050"
    echo "  请参考 FIX_DEPLOYMENT_ISSUES.md 手动创建配置"
fi

echo ""
echo "5. 测试Nginx配置..."
echo ""

if sudo nginx -t; then
    echo "  ✅ Nginx配置测试通过"
    echo ""
    echo "6. 重载Nginx..."
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
echo "📝 验证步骤:"
echo "  1. 访问 https://50zf.usdt2026.cc - 应该显示MiniApp"
echo "  2. 访问 https://5050.usdt2026.cc - 应该显示Web网站"
echo ""
echo "📋 当前配置:"
echo "  MiniApp (50zf.usdt2026.cc): $MINIAPP_DIR"
echo "  Web网站 (5050.usdt2026.cc): $WEB_DIR"
