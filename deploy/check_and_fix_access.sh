#!/bin/bash

# 检查并修复网站访问问题

echo "🔍 检查网站访问问题..."
echo ""

SERVER_PATH="/home/ubuntu/wushizhifu"
WEB_DIST="${SERVER_PATH}/web/dist"
MINIAPP_DIST="${SERVER_PATH}/wushizhifu-full/dist"

# 1. 检查构建文件
echo "📋 步骤1: 检查构建文件..."
echo "检查Web前端构建:"
if [ -d "$WEB_DIST" ]; then
    FILE_COUNT=$(find "$WEB_DIST" -type f 2>/dev/null | wc -l)
    ASSETS_COUNT=$(find "$WEB_DIST/assets" -type f 2>/dev/null 2>/dev/null | wc -l)
    echo "  总文件数: $FILE_COUNT"
    echo "  assets文件数: $ASSETS_COUNT"
    
    if [ -f "$WEB_DIST/index.html" ]; then
        echo "  ✅ index.html 存在"
    else
        echo "  ❌ index.html 不存在"
    fi
    
    if [ -d "$WEB_DIST/assets" ]; then
        echo "  ✅ assets 目录存在"
        echo "  assets目录内容:"
        ls -lh "$WEB_DIST/assets" | head -10
    else
        echo "  ❌ assets 目录不存在"
    fi
else
    echo "  ❌ Web目录不存在"
fi

echo ""
echo "检查MiniApp构建:"
if [ -d "$MINIAPP_DIST" ]; then
    FILE_COUNT=$(find "$MINIAPP_DIST" -type f 2>/dev/null | wc -l)
    ASSETS_COUNT=$(find "$MINIAPP_DIST/assets" -type f 2>/dev/null 2>/dev/null | wc -l)
    echo "  总文件数: $FILE_COUNT"
    echo "  assets文件数: $ASSETS_COUNT"
    
    if [ -f "$MINIAPP_DIST/index.html" ]; then
        echo "  ✅ index.html 存在"
    else
        echo "  ❌ index.html 不存在"
    fi
    
    if [ -d "$MINIAPP_DIST/assets" ]; then
        echo "  ✅ assets 目录存在"
        echo "  assets目录内容:"
        ls -lh "$MINIAPP_DIST/assets" | head -10
    else
        echo "  ❌ assets 目录不存在"
    fi
else
    echo "  ❌ MiniApp目录不存在"
fi

# 2. 确保HTTP配置正确（不强制HTTPS）
echo ""
echo "📋 步骤2: 确保HTTP配置正确..."
NGINX_5050="/etc/nginx/sites-available/web-5050"
NGINX_50ZF="/etc/nginx/sites-available/wushizhifu"

# 修复5050配置，确保不强制HTTPS
if [ -f "$NGINX_5050" ]; then
    echo "修复5050配置..."
    # 注释掉HTTPS重定向（如果存在）
    sudo sed -i 's|^[[:space:]]*return 301 https://|    # return 301 https://|g' "$NGINX_5050"
    # 确保有HTTP server块
    if ! grep -q "listen 80;" "$NGINX_5050"; then
        echo "  添加HTTP监听..."
        sudo sed -i '/server_name 5050.usdt2026.cc;/a\    listen 80;' "$NGINX_5050"
    fi
    echo "✅ 5050配置已修复"
fi

# 修复50zf配置
if [ -f "$NGINX_50ZF" ]; then
    echo "修复50zf配置..."
    # 注释掉HTTPS重定向（如果存在）
    sudo sed -i 's|^[[:space:]]*return 301 https://|    # return 301 https://|g' "$NGINX_50ZF"
    # 确保有HTTP server块
    if ! grep -q "listen 80;" "$NGINX_50ZF"; then
        echo "  添加HTTP监听..."
        sudo sed -i '/server_name 50zf.usdt2026.cc;/a\    listen 80;' "$NGINX_50ZF"
    fi
    echo "✅ 50zf配置已修复"
fi

# 3. 测试Nginx配置
echo ""
echo "📋 步骤3: 测试Nginx配置..."
if sudo nginx -t; then
    echo "✅ Nginx配置正确"
    sudo systemctl reload nginx
else
    echo "❌ Nginx配置错误"
    exit 1
fi

# 4. 测试本地HTTP访问
echo ""
echo "📋 步骤4: 测试本地HTTP访问..."
echo "测试 http://localhost (5050):"
HTTP_CODE_5050=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/ -H "Host: 5050.usdt2026.cc" 2>/dev/null || echo "000")
if [ "$HTTP_CODE_5050" = "200" ]; then
    echo "  ✅ HTTP 200 - 访问正常"
elif [ "$HTTP_CODE_5050" = "301" ] || [ "$HTTP_CODE_5050" = "302" ]; then
    echo "  ⚠️ HTTP $HTTP_CODE_5050 - 被重定向（可能是HTTPS重定向）"
else
    echo "  ❌ HTTP $HTTP_CODE_5050 - 访问失败"
fi

echo "测试 http://localhost (50zf):"
HTTP_CODE_50ZF=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/ -H "Host: 50zf.usdt2026.cc" 2>/dev/null || echo "000")
if [ "$HTTP_CODE_50ZF" = "200" ]; then
    echo "  ✅ HTTP 200 - 访问正常"
elif [ "$HTTP_CODE_50ZF" = "301" ] || [ "$HTTP_CODE_50ZF" = "302" ]; then
    echo "  ⚠️ HTTP $HTTP_CODE_50ZF - 被重定向（可能是HTTPS重定向）"
else
    echo "  ❌ HTTP $HTTP_CODE_50ZF - 访问失败"
fi

# 5. 检查端口监听
echo ""
echo "📋 步骤5: 检查端口监听..."
if sudo ss -tlnp | grep -q ":80 "; then
    echo "✅ 端口80正在监听"
    sudo ss -tlnp | grep ":80 "
else
    echo "❌ 端口80未监听"
fi

if sudo ss -tlnp | grep -q ":443 "; then
    echo "✅ 端口443正在监听"
    sudo ss -tlnp | grep ":443 "
else
    echo "⚠️ 端口443未监听（如果使用HTTPS需要此端口）"
fi

# 6. 获取服务器公网IP
echo ""
echo "📋 步骤6: 获取服务器信息..."
SERVER_IP=$(curl -s ifconfig.me || curl -s ipinfo.io/ip || echo "无法获取")
echo "  服务器公网IP: $SERVER_IP"

# 7. 检查DNS
echo ""
echo "📋 步骤7: 检查DNS解析..."
DNS_5050=$(dig +short 5050.usdt2026.cc @8.8.8.8 2>/dev/null | tail -1 || echo "无法解析")
DNS_50ZF=$(dig +short 50zf.usdt2026.cc @8.8.8.8 2>/dev/null | tail -1 || echo "无法解析")
echo "  5050.usdt2026.cc -> $DNS_5050"
echo "  50zf.usdt2026.cc -> $DNS_50ZF"

if [ "$DNS_5050" = "$SERVER_IP" ]; then
    echo "  ✅ 5050 DNS指向正确"
else
    echo "  ⚠️ 5050 DNS可能不正确"
fi

if [ "$DNS_50ZF" = "$SERVER_IP" ]; then
    echo "  ✅ 50zf DNS指向正确"
else
    echo "  ⚠️ 50zf DNS可能不正确"
fi

# 8. 提供云服务商安全组检查指南
echo ""
echo "📋 步骤8: 云服务商安全组检查..."
echo ""
echo "⚠️ 如果本地测试成功但外部无法访问，请检查云服务商安全组："
echo ""
echo "1. 阿里云/腾讯云/华为云："
echo "   - 登录云服务商控制台"
echo "   - 找到「安全组」或「防火墙」设置"
echo "   - 确保开放以下端口："
echo "     * 入方向：TCP 80 (HTTP)"
echo "     * 入方向：TCP 443 (HTTPS)"
echo "     * 源地址：0.0.0.0/0 (允许所有IP访问)"
echo ""
echo "2. AWS EC2："
echo "   - 找到「Security Groups」"
echo "   - 添加入站规则："
echo "     * Type: HTTP, Port: 80, Source: 0.0.0.0/0"
echo "     * Type: HTTPS, Port: 443, Source: 0.0.0.0/0"
echo ""
echo "3. 测试端口是否开放："
echo "   从外部机器运行："
echo "   telnet $SERVER_IP 80"
echo "   或"
echo "   curl -v http://$SERVER_IP -H 'Host: 5050.usdt2026.cc'"
echo ""

# 9. 最终建议
echo ""
echo "✅ 检查完成！"
echo ""
echo "💡 重要提示："
echo "   1. 如果访问 https://，但SSL证书不存在，会显示连接被拒绝"
echo "   2. 请使用 http://5050.usdt2026.cc 和 http://50zf.usdt2026.cc 测试"
echo "   3. 如果HTTP可以访问，再申请SSL证书："
echo "      sudo certbot --nginx -d 5050.usdt2026.cc"
echo "      sudo certbot --nginx -d 50zf.usdt2026.cc"
echo "   4. 确保云服务商安全组已开放80和443端口"
