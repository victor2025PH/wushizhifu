# API 502 Bad Gateway 错误分析

## 问题描述

从控制台日志看到多个 502 Bad Gateway 错误：
1. `GET https://50zf.usdt2026.cc/api/videos/alipay 502 (Bad Gateway)`
2. `GET https://50zf.usdt2026.cc/api/videos/wechat 502 (Bad Gateway)`
3. `GET https://50zf.usdt2026.cc/api/binance/p2p?payment_method=alipay&rows=10&page=1 502 (Bad Gateway)`
4. `GET https://50zf.usdt2026.cc/api/binance/p2p?payment_method=wechat&rows=10&page=1 502 (Bad Gateway)`
5. `GET https://50zf.usdt2026.cc/api/binance/p2p?payment_method=bank&rows=10&page=1 502 (Bad Gateway)`

## 502 错误的含义

502 Bad Gateway 表示：
- **Nginx 成功接收了请求**
- **但是无法连接到后端 API 服务**（`api_server.py`）
- 或者后端 API 服务返回了无效响应

## 可能的原因

### 1. API 服务没有运行（最可能）

**症状**：
- 所有 `/api/*` 端点都返回 502
- Nginx 配置正确，但后端服务未启动

**原因**：
- Systemd 服务 `wushipay-api.service` 未启动
- 服务启动失败
- 服务崩溃后未自动重启

### 2. API 服务运行在错误的端口

**症状**：
- API 服务运行了，但端口不匹配
- Nginx 配置的代理端口（通常是 8000）与 API 服务监听的端口不一致

**检查**：
- Nginx 配置中的 `proxy_pass` 应该指向 `http://127.0.0.1:8000`
- API 服务应该监听 `127.0.0.1:8000`

### 3. API 服务启动失败

**症状**：
- 服务配置存在但无法启动
- 可能有 Python 依赖缺失
- 可能有代码错误

**常见原因**：
- 缺少 Python 依赖包
- Python 虚拟环境路径错误
- 代码中有语法错误或运行时错误
- 端口被其他进程占用

### 4. Nginx 配置问题

**症状**：
- API 服务运行正常，但 Nginx 无法连接

**可能原因**：
- `proxy_pass` 配置错误
- Nginx 无法访问本地服务（权限问题）
- Nginx 配置语法错误

## 诊断步骤

### 步骤1：检查 API 服务状态

```bash
# 检查服务状态
sudo systemctl status wushipay-api.service

# 查看服务日志
sudo journalctl -u wushipay-api.service -n 50 --no-pager

# 检查服务是否在运行
ps aux | grep api_server
```

### 步骤2：检查端口监听

```bash
# 检查 8000 端口是否被监听
sudo lsof -i:8000
# 或者
sudo netstat -tlnp | grep 8000
```

### 步骤3：检查 Nginx 配置

```bash
# 查看 Nginx 配置中的 API 代理设置
sudo cat /etc/nginx/sites-available/50zf.usdt2026.cc | grep -A 10 "location /api"

# 测试 Nginx 配置
sudo nginx -t
```

### 步骤4：手动测试 API 服务

```bash
# 如果服务没有运行，尝试手动启动
cd /home/ubuntu/wushizhifu
source venv/bin/activate  # 如果使用虚拟环境
python3 api_server.py

# 或者使用 uvicorn
uvicorn api_server:app --host 127.0.0.1 --port 8000
```

### 步骤5：检查 API 服务日志

```bash
# 实时查看服务日志
sudo journalctl -u wushipay-api.service -f

# 查看最近的错误日志
sudo journalctl -u wushipay-api.service --since "10 minutes ago" | grep -i error
```

## 修复方案

### 方案1：启动/重启 API 服务（最可能需要的）

```bash
# 启动服务
sudo systemctl start wushipay-api.service

# 如果服务不存在，需要创建服务文件
# 服务文件应该在 /etc/systemd/system/wushipay-api.service
# 模板应该在 /home/ubuntu/wushizhifu/deploy/systemd/wushipay-api.service

# 如果服务文件不存在，从模板创建
sudo cp /home/ubuntu/wushizhifu/deploy/systemd/wushipay-api.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable wushipay-api.service
sudo systemctl start wushipay-api.service
```

### 方案2：检查并修复服务配置

```bash
# 检查服务文件是否存在
ls -la /etc/systemd/system/wushipay-api.service

# 检查服务文件内容
sudo cat /etc/systemd/system/wushipay-api.service

# 如果服务文件有问题，从模板重新创建
cd /home/ubuntu/wushizhifu
sudo cp deploy/systemd/wushipay-api.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl restart wushipay-api.service
```

### 方案3：检查 Python 依赖

```bash
cd /home/ubuntu/wushizhifu

# 如果使用虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 或者安装核心依赖
pip install fastapi uvicorn python-multipart httpx requests
```

### 方案4：检查端口占用

```bash
# 检查端口是否被占用
sudo lsof -i:8000

# 如果被占用，停止占用端口的进程
sudo kill -9 <PID>

# 然后重启服务
sudo systemctl restart wushipay-api.service
```

### 方案5：手动启动服务进行调试

```bash
cd /home/ubuntu/wushizhifu

# 激活虚拟环境（如果使用）
source venv/bin/activate

# 直接运行 API 服务，查看错误信息
python3 api_server.py
# 或者
uvicorn api_server:app --host 127.0.0.1 --port 8000 --reload
```

## 快速诊断脚本

```bash
#!/bin/bash
# 快速诊断 API 502 错误

echo "=== 1. 检查服务状态 ==="
sudo systemctl status wushipay-api.service --no-pager -l | head -20

echo ""
echo "=== 2. 检查端口监听 ==="
sudo lsof -i:8000 || echo "端口 8000 未被监听"

echo ""
echo "=== 3. 检查进程 ==="
ps aux | grep api_server | grep -v grep

echo ""
echo "=== 4. 检查服务日志（最近20行）==="
sudo journalctl -u wushipay-api.service -n 20 --no-pager

echo ""
echo "=== 5. 检查 Nginx 配置 ==="
sudo cat /etc/nginx/sites-available/50zf.usdt2026.cc | grep -A 5 "location /api" || echo "未找到 /api 配置"

echo ""
echo "=== 6. 测试 API 端点（如果服务运行）==="
curl -s http://127.0.0.1:8000/ || echo "无法连接到 API 服务"
```

## 总结

**最可能的原因**：API 服务 `wushipay-api.service` 没有运行或启动失败。

**推荐的修复步骤**：
1. 检查服务状态：`sudo systemctl status wushipay-api.service`
2. 查看服务日志：`sudo journalctl -u wushipay-api.service -n 50`
3. 如果服务不存在，创建并启动服务
4. 如果服务存在但未运行，启动服务：`sudo systemctl start wushipay-api.service`
5. 如果服务启动失败，查看日志找出原因并修复

