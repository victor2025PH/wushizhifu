# 快速修复服务器问题

## 🔧 问题1: API客服分配错误

**错误**: `module 'database.db' has no attribute 'assign_customer_service'`

**原因**: `botB/services/customer_service_service.py` 导入了错误的数据库模块

**修复方法**:

在服务器上执行：

```bash
cd /home/ubuntu/wushizhifu

# 编辑文件
nano botB/services/customer_service_service.py
```

找到第7行：
```python
from database import db
```

改为：
```python
# 确保导入botB的database模块
import sys
from pathlib import Path
botb_path = Path(__file__).parent.parent / "botB"
sys.path.insert(0, str(botb_path))
from database import db
```

或者更简单的方法，直接改为：
```python
# 使用botB的database模块（包含assign_customer_service方法）
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'botB'))
from database import db
```

保存后重启API服务器：
```bash
sudo systemctl restart wushipay-api
sudo journalctl -u wushipay-api -f
```

## 🔧 问题2: Nginx配置错误（MiniApp显示Web网站）

### 方法1: 手动检查并修复

```bash
# 1. 检查当前配置
sudo nginx -T | grep -A 10 "server_name 50zf.usdt2026.cc"
sudo nginx -T | grep -A 10 "server_name 5050.usdt2026.cc"

# 2. 检查目录
ls -la /home/ubuntu/wushizhifu/wushizhifu-full/dist/
ls -la /home/ubuntu/wushizhifu/web/dist/

# 3. 找到配置文件
sudo find /etc/nginx -name "*50zf*" -o -name "*wushizhifu*" -o -name "*web-5050*"

# 4. 编辑50zf.usdt2026.cc的配置
sudo nano /etc/nginx/sites-available/50zf.usdt2026.cc
# 或
sudo nano /etc/nginx/sites-available/wushizhifu
```

确保配置中的 `root` 指向MiniApp目录：
```nginx
root /home/ubuntu/wushizhifu/wushizhifu-full/dist;
# 或者如果是 /opt/wushizhifu/frontend/dist
# root /opt/wushizhifu/frontend/dist;
```

```bash
# 5. 编辑5050.usdt2026.cc的配置
sudo nano /etc/nginx/sites-available/web-5050
```

确保配置中的 `root` 指向Web网站目录：
```nginx
root /home/ubuntu/wushizhifu/web/dist;
```

```bash
# 6. 测试并重载
sudo nginx -t
sudo systemctl reload nginx
```

### 方法2: 使用sed快速修复

```bash
# 修复50zf.usdt2026.cc (MiniApp)
# 找到配置文件
CONFIG_50ZF=$(sudo find /etc/nginx/sites-available -type f | xargs grep -l "server_name 50zf.usdt2026.cc" | head -1)

if [ -n "$CONFIG_50ZF" ]; then
    echo "找到配置文件: $CONFIG_50ZF"
    # 备份
    sudo cp "$CONFIG_50ZF" "${CONFIG_50ZF}.backup"
    
    # 更新root路径（根据实际目录选择）
    # 如果MiniApp在 /home/ubuntu/wushizhifu/wushizhifu-full/dist
    sudo sed -i 's|root.*wushizhifu.*dist|root /home/ubuntu/wushizhifu/wushizhifu-full/dist;|g' "$CONFIG_50ZF"
    # 或者如果在 /opt/wushizhifu/frontend/dist
    # sudo sed -i 's|root.*wushizhifu.*dist|root /opt/wushizhifu/frontend/dist;|g' "$CONFIG_50ZF"
    
    echo "已更新: $CONFIG_50ZF"
else
    echo "未找到50zf.usdt2026.cc的配置文件"
fi

# 修复5050.usdt2026.cc (Web网站)
CONFIG_5050="/etc/nginx/sites-available/web-5050"
if [ -f "$CONFIG_5050" ]; then
    echo "找到配置文件: $CONFIG_5050"
    # 备份
    sudo cp "$CONFIG_5050" "${CONFIG_5050}.backup"
    
    # 更新root路径
    sudo sed -i 's|root.*web.*dist|root /home/ubuntu/wushizhifu/web/dist;|g' "$CONFIG_5050"
    
    echo "已更新: $CONFIG_5050"
else
    echo "未找到web-5050配置文件"
fi

# 测试并重载
sudo nginx -t && sudo systemctl reload nginx
```

## ✅ 验证修复

### 1. 验证API
```bash
curl -X POST http://localhost:8000/api/customer-service/assign \
  -H "Content-Type: application/json" \
  -d '{"user_id": 123456, "username": "testuser"}'
```

应该返回正确的客服账号，而不是错误。

### 2. 验证网站
- 访问 `https://50zf.usdt2026.cc` - 应该显示MiniApp（不是Web网站）
- 访问 `https://5050.usdt2026.cc` - 应该显示Web网站

### 3. 查看日志
```bash
# API日志
sudo journalctl -u wushipay-api -n 50

# Nginx日志
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```
