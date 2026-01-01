# Web前端部署指南

## 📋 项目概述

`web/` 文件夹是一个基于 React + TypeScript + Vite 的前端网站项目，用于展示"伍拾支付"的产品和服务信息。

## 🏗️ 技术栈

- **框架**: React 19
- **语言**: TypeScript
- **构建工具**: Vite
- **样式**: Tailwind CSS (CDN)
- **部署**: Nginx (静态文件服务)

## 🚀 部署方式

### 方式一：GitHub Actions 自动部署（推荐）

已配置 `.github/workflows/deploy-web.yml`，当 `web/` 目录有变更时自动：

1. ✅ 安装依赖
2. ✅ 构建项目（`npm run build`）
3. ✅ 上传构建产物到服务器
4. ✅ 配置 Nginx 并重载

#### 前提条件

确保 GitHub Secrets 已配置：
- `SERVER_HOST` - 服务器IP地址
- `SERVER_USER` - SSH用户名（通常是 `ubuntu`）
- `SSH_PRIVATE_KEY` - SSH私钥
- `SSH_PORT` - SSH端口（可选，默认22）

#### 部署步骤

1. 提交代码到 `main` 分支
2. GitHub Actions 自动触发部署
3. 检查 Actions 日志确认部署状态

### 方式二：手动部署

#### 1. 本地构建

```bash
cd web
npm install
npm run build
```

构建产物会在 `web/dist/` 目录中生成。

#### 2. 上传到服务器

```bash
# 使用 scp 上传
scp -r web/dist/* user@server:/home/ubuntu/wushizhifu/web/dist/

# 或使用 rsync
rsync -avz --delete web/dist/ user@server:/home/ubuntu/wushizhifu/web/dist/
```

#### 3. 配置 Nginx

在服务器上创建或更新 Nginx 配置：

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # Web前端静态文件
    root /home/ubuntu/wushizhifu/web/dist;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
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
```

#### 4. 设置权限并重载 Nginx

```bash
# 设置文件权限
sudo chown -R www-data:www-data /home/ubuntu/wushizhifu/web/dist

# 测试配置
sudo nginx -t

# 重载 Nginx
sudo systemctl reload nginx
```

## 📁 项目结构

```
web/
├── index.html          # HTML入口文件
├── index.tsx           # React入口文件
├── App.tsx             # 主应用组件
├── vite.config.ts      # Vite配置
├── tsconfig.json       # TypeScript配置
├── package.json        # 项目依赖
├── metadata.json       # 元数据配置
├── components/         # React组件
│   ├── Navbar.tsx
│   ├── Hero.tsx
│   ├── FeatureGrid.tsx
│   ├── ComparisonTable.tsx
│   ├── FAQ.tsx
│   ├── Footer.tsx
│   └── ...
└── dist/               # 构建输出目录（不提交到Git）
```

## 🔧 开发说明

### 本地开发

```bash
cd web
npm install
npm run dev
```

开发服务器默认运行在 `http://localhost:5173`

### 构建生产版本

```bash
npm run build
```

构建产物输出到 `dist/` 目录。

## 🌐 服务器路径

- **构建目录**: `/home/ubuntu/wushizhifu/web/dist/`
- **Nginx配置**: `/etc/nginx/sites-available/wushizhifu`

## 📝 注意事项

1. **依赖管理**: 项目使用 CDN 加载 React 和 Tailwind CSS，无需打包这些依赖
2. **路由配置**: 单页应用需要配置 Nginx 的 `try_files` 支持前端路由
3. **缓存策略**: 静态资源设置长期缓存，HTML 文件不缓存
4. **权限设置**: Web 文件需要 `www-data` 用户权限

## 🔍 故障排查

### 构建失败

```bash
# 清除缓存重新安装
cd web
rm -rf node_modules package-lock.json
npm install
npm run build
```

### Nginx 404 错误

检查 Nginx 配置中的 `root` 路径是否正确：

```bash
sudo nginx -t
ls -la /home/ubuntu/wushizhifu/web/dist/
```

### 权限问题

```bash
sudo chown -R www-data:www-data /home/ubuntu/wushizhifu/web/dist
sudo chmod -R 755 /home/ubuntu/wushizhifu/web/dist
```

## 🔗 相关文档

- [GitHub Actions 部署配置](.github/workflows/deploy-web.yml)
- [Nginx 配置示例](deploy/nginx.conf)
