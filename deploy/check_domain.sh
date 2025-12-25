#!/bin/bash
# 檢查域名解析和服務器配置

DOMAIN="50zf.usdt2026.cc"

echo "=========================================="
echo "🔍 檢查域名和服務器配置"
echo "=========================================="

# 1. 檢查域名解析
echo "1. 檢查域名解析:"
echo "   域名: ${DOMAIN}"
DIG_RESULT=$(dig +short ${DOMAIN} 2>/dev/null || echo "無法解析")
SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || echo "無法獲取")

echo "   DNS 解析結果: ${DIG_RESULT}"
echo "   服務器公網 IP: ${SERVER_IP}"

if [ "$DIG_RESULT" != "$SERVER_IP" ] && [ "$DIG_RESULT" != "無法解析" ]; then
    echo "   ⚠️  警告: DNS 解析的 IP 與服務器 IP 不一致"
    echo "   請確保域名正確解析到服務器 IP: ${SERVER_IP}"
else
    echo "   ✅ 域名解析正確"
fi

echo ""

# 2. 檢查端口
echo "2. 檢查端口開放情況:"
if command -v ufw &> /dev/null; then
    echo "   UFW 狀態:"
    sudo ufw status | grep -E '(80|443|22)' || echo "   未配置相關規則"
fi

echo "   監聽端口:"
sudo netstat -tlnp 2>/dev/null | grep -E ':(80|443|22)' || ss -tlnp | grep -E ':(80|443|22)'

echo ""

# 3. 檢查 Nginx
echo "3. 檢查 Nginx:"
if command -v nginx &> /dev/null; then
    echo "   ✅ Nginx 已安裝"
    if sudo systemctl is-active --quiet nginx; then
        echo "   ✅ Nginx 正在運行"
    else
        echo "   ⚠️  Nginx 未運行"
    fi
else
    echo "   ⚠️  Nginx 未安裝"
fi

echo ""

# 4. 檢查 Certbot
echo "4. 檢查 Certbot:"
if command -v certbot &> /dev/null; then
    echo "   ✅ Certbot 已安裝"
else
    echo "   ⚠️  Certbot 未安裝"
fi

echo ""

# 5. 檢查項目目錄
echo "5. 檢查項目目錄:"
PROJECT_DIR="/opt/wushizhifu"
if [ -d "$PROJECT_DIR" ]; then
    echo "   ✅ 項目目錄存在: $PROJECT_DIR"
    if [ -d "$PROJECT_DIR/frontend" ]; then
        echo "   ✅ 前端目錄存在"
    else
        echo "   ⚠️  前端目錄不存在"
    fi
    if [ -d "$PROJECT_DIR/bot" ]; then
        echo "   ✅ Bot 目錄存在"
        if [ -f "$PROJECT_DIR/bot/.env" ]; then
            echo "   ✅ .env 文件存在"
        else
            echo "   ⚠️  .env 文件不存在"
        fi
    else
        echo "   ⚠️  Bot 目錄不存在"
    fi
else
    echo "   ⚠️  項目目錄不存在"
fi

echo ""
echo "=========================================="
echo "檢查完成"
echo "=========================================="

