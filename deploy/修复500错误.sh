#!/bin/bash
# 修复 500 Internal Server Error 脚本

set -e

echo "=========================================="
echo "🔧 修复 500 Internal Server Error"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# 1. 检查项目实际位置
echo -e "${YELLOW}📂 步骤 1: 检查项目位置...${NC}"
if [ -d "/home/ubuntu/wushizhifu/frontend" ]; then
    PROJECT_DIR="/home/ubuntu/wushizhifu"
    FRONTEND_DIR="/home/ubuntu/wushizhifu/frontend"
    echo -e "${GREEN}✅ 找到项目在: ${PROJECT_DIR}${NC}"
elif [ -d "/opt/wushizhifu/frontend" ]; then
    PROJECT_DIR="/opt/wushizhifu"
    FRONTEND_DIR="/opt/wushizhifu/frontend"
    echo -e "${GREEN}✅ 找到项目在: ${PROJECT_DIR}${NC}"
else
    echo -e "${YELLOW}⚠️  前端项目目录不存在，尝试自动部署...${NC}"
    
    # 尝试自动部署
    PROJECT_DIR="$HOME/wushizhifu"
    FRONTEND_DIR="$PROJECT_DIR/frontend"
    REPO_URL="https://github.com/victor2025PH/wushizhifu.git"
    
    echo "创建项目目录..."
    mkdir -p ${PROJECT_DIR}
    cd ${PROJECT_DIR}
    
    echo "克隆仓库..."
    if [ ! -d "repo" ]; then
        git clone ${REPO_URL} repo
    else
        cd repo && git pull && cd ..
    fi
    
    if [ -d "repo/wushizhifu-full" ]; then
        echo "复制前端代码..."
        cp -r repo/wushizhifu-full ${FRONTEND_DIR}
        echo -e "${GREEN}✅ 前端代码已部署到: ${FRONTEND_DIR}${NC}"
    else
        echo -e "${RED}❌ 错误: 仓库中找不到 wushizhifu-full 目录${NC}"
        echo "请手动运行部署脚本: sudo ./部署前端项目.sh"
        exit 1
    fi
fi

# 2. 检查前端源代码是否存在
echo ""
echo -e "${YELLOW}📋 步骤 2: 检查前端源代码...${NC}"
if [ ! -f "${FRONTEND_DIR}/package.json" ]; then
    echo -e "${RED}❌ 错误: ${FRONTEND_DIR}/package.json 不存在${NC}"
    echo -e "${YELLOW}提示: 前端源代码可能未克隆或路径错误${NC}"
    exit 1
fi
echo -e "${GREEN}✅ 前端源代码存在${NC}"

# 3. 构建前端
echo ""
echo -e "${YELLOW}🏗️  步骤 3: 构建前端...${NC}"
cd ${FRONTEND_DIR}

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js 未安装${NC}"
    echo "安装 Node.js: curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash - && sudo apt install -y nodejs"
    exit 1
fi

# 设置 dist 目录权限（如果存在）
if [ -d "dist" ]; then
    echo "设置 dist 目录权限..."
    sudo chown -R ubuntu:ubuntu dist || sudo chown -R $USER:$USER dist
fi

# 安装依赖（如果需要）
if [ ! -d "node_modules" ]; then
    echo "安装 npm 依赖..."
    npm install
fi

# 构建前端
echo "执行构建..."
npm run build

# 检查构建结果
if [ ! -f "dist/index.html" ]; then
    echo -e "${RED}❌ 构建失败: dist/index.html 不存在${NC}"
    exit 1
fi
echo -e "${GREEN}✅ 前端构建完成${NC}"

# 4. 设置文件权限
echo ""
echo -e "${YELLOW}🔐 步骤 4: 设置文件权限...${NC}"
sudo chown -R www-data:www-data ${FRONTEND_DIR}/dist
sudo chmod -R 755 ${FRONTEND_DIR}/dist
echo -e "${GREEN}✅ 权限设置完成${NC}"

# 5. 更新 Nginx 配置
echo ""
echo -e "${YELLOW}⚙️  步骤 5: 更新 Nginx 配置...${NC}"
NGINX_CONFIG="/etc/nginx/sites-available/wushizhifu"

# 检查 Nginx 配置文件是否存在
if [ ! -f "${NGINX_CONFIG}" ]; then
    # 如果没有，从模板创建
    echo "创建 Nginx 配置文件..."
    sudo tee ${NGINX_CONFIG} > /dev/null <<EOF
server {
    listen 80;
    server_name 50zf.usdt2026.cc;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name 50zf.usdt2026.cc;
    
    # SSL 证书路径（Certbot 会自动配置）
    # ssl_certificate /etc/letsencrypt/live/50zf.usdt2026.cc/fullchain.pem;
    # ssl_certificate_key /etc/letsencrypt/live/50zf.usdt2026.cc/privkey.pem;
    
    # SSL 配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # 前端静态文件
    root ${FRONTEND_DIR}/dist;
    index index.html;
    
    location / {
        try_files \$uri \$uri/ /index.html;
    }
    
    # API 代理
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # 静态资源缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Gzip 压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/json;
}
EOF
    echo -e "${GREEN}✅ Nginx 配置文件已创建${NC}"
else
    # 更新现有配置中的 root 路径
    echo "更新 Nginx 配置中的 root 路径..."
    sudo sed -i "s|root /.*/frontend/dist;|root ${FRONTEND_DIR}/dist;|g" ${NGINX_CONFIG}
    echo -e "${GREEN}✅ Nginx 配置已更新${NC}"
fi

# 启用站点（如果未启用）
if [ ! -L "/etc/nginx/sites-enabled/wushizhifu" ]; then
    sudo ln -sf ${NGINX_CONFIG} /etc/nginx/sites-enabled/wushizhifu
    echo -e "${GREEN}✅ Nginx 站点已启用${NC}"
fi

# 测试 Nginx 配置
echo "测试 Nginx 配置..."
if sudo nginx -t; then
    echo -e "${GREEN}✅ Nginx 配置测试通过${NC}"
else
    echo -e "${RED}❌ Nginx 配置测试失败${NC}"
    exit 1
fi

# 重载 Nginx
echo "重载 Nginx..."
sudo systemctl reload nginx
echo -e "${GREEN}✅ Nginx 已重载${NC}"

# 6. 检查 API 服务
echo ""
echo -e "${YELLOW}🔌 步骤 6: 检查 API 服务...${NC}"
if curl -s http://127.0.0.1:8000/ > /dev/null 2>&1; then
    echo -e "${GREEN}✅ API 服务正在运行${NC}"
else
    echo -e "${YELLOW}⚠️  API 服务未运行（这不会影响前端访问）${NC}"
    echo "如果需要启动 API 服务，请执行:"
    echo "  cd ${PROJECT_DIR}"
    echo "  python3 -m uvicorn api_server:app --host 127.0.0.1 --port 8000"
fi

# 完成
echo ""
echo -e "${GREEN}=========================================="
echo "✅ 修复完成！"
echo "==========================================${NC}"
echo ""
echo -e "${BLUE}📋 检查清单:${NC}"
echo "  ✅ 前端文件位置: ${FRONTEND_DIR}/dist"
echo "  ✅ Nginx root 路径: ${FRONTEND_DIR}/dist"
echo "  ✅ 文件权限: www-data:www-data"
echo ""
echo -e "${BLUE}🌐 访问网站: https://50zf.usdt2026.cc${NC}"
echo ""
echo -e "${YELLOW}如果仍然有 500 错误，请检查:${NC}"
echo "  1. sudo tail -50 /var/log/nginx/error.log"
echo "  2. sudo systemctl status nginx"
echo "  3. ls -la ${FRONTEND_DIR}/dist/"

