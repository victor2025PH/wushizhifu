# 修复 get_main_keyboard TypeError 错误

## 问题

日志显示错误：
```
TypeError: get_main_keyboard() got an unexpected keyword argument 'user_id'
File "/home/ubuntu/wushizhifu/bot/handlers/user_handlers.py", line 41
```

## 原因

`get_main_keyboard()` 函数定义时没有 `user_id` 和 `is_admin` 参数，但代码中多处调用时传递了这些参数。

## 修复

已更新 `keyboards/main_kb.py`：
- 添加了 `user_id: int = None` 和 `is_admin: bool = False` 参数
- 如果 `is_admin` 未提供但 `user_id` 提供了，会自动检查管理员状态
- 添加了 `AdminRepository` 导入

## 部署步骤

### 1. 本地推送代码

```bash
cd D:\wushizhifu\wushizhifu-bot
git add keyboards/main_kb.py
git commit -m "修复 get_main_keyboard 函数签名错误"
git push origin main
```

### 2. 服务器上更新并重启

```bash
# SSH 到服务器
cd /home/ubuntu/wushizhifu/bot

# 拉取最新代码
git pull origin main

# 清除 Python 缓存
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -r {} + 2>/dev/null || true

# 停止服务
sudo systemctl stop wushizhifu-bot

# 强制终止所有 Bot 进程
sudo pkill -9 -f bot.py
sleep 2

# 重新加载 systemd 配置
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start wushizhifu-bot

# 查看日志
sleep 4
sudo journalctl -u wushizhifu-bot -n 50 --no-pager
```

### 3. 验证修复

在 Telegram 中：
1. 发送 `/start` 命令
2. 应该收到欢迎消息（没有错误）
3. 应该看到所有按钮正常显示

日志中应该：
- ✅ 没有 `TypeError: get_main_keyboard()` 错误
- ✅ 没有 `TelegramConflictError` 错误
- ✅ Bot 正常启动和处理消息

