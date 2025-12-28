# 立即清理多个 Bot 服务 - 快速命令

## ⚠️ 问题
服务器上有两个 Bot 服务：
- `wushipay-bot.service` (旧服务，应该删除)
- `wushizhifu-bot.service` (正确服务)

## 🚀 快速清理命令（一键执行）

```bash
# 1. 停止并禁用旧服务
sudo systemctl stop wushipay-bot.service 2>/dev/null || true
sudo systemctl disable wushipay-bot.service 2>/dev/null || true

# 2. 强制停止所有 Bot 进程
sudo pkill -9 -f "bot.py" 2>/dev/null || true

# 3. 重新加载 systemd
sudo systemctl daemon-reload

# 4. 确保正确服务已启用并启动
sudo systemctl enable wushizhifu-bot.service
sudo systemctl restart wushizhifu-bot.service

# 5. 等待 3 秒
sleep 3

# 6. 检查状态
echo "=== 服务状态 ==="
sudo systemctl status wushizhifu-bot.service --no-pager | head -15

echo ""
echo "=== 运行的 Bot 进程 ==="
ps aux | grep "bot.py" | grep -v grep || echo "无进程"

echo ""
echo "=== 最新日志 ==="
sudo journalctl -u wushizhifu-bot.service -n 20 --no-pager | grep -E "(Menu button|Bot description|Initialized|ERROR|Error)"
```

## 📋 详细检查步骤

### 步骤 1：检查所有 Bot 服务

```bash
systemctl list-units --all --type=service | grep -E "(bot|Bot)"
```

### 步骤 2：检查旧服务状态

```bash
sudo systemctl status wushipay-bot.service --no-pager
```

如果服务存在且运行中，需要停止它。

### 步骤 3：停止并删除旧服务

```bash
# 停止服务
sudo systemctl stop wushipay-bot.service

# 禁用服务（防止开机自启）
sudo systemctl disable wushipay-bot.service

# 删除服务文件（可选，如果需要完全清理）
sudo rm /etc/systemd/system/wushipay-bot.service
sudo systemctl daemon-reload
```

### 步骤 4：确保正确服务运行

```bash
# 启用服务（如果未启用）
sudo systemctl enable wushizhifu-bot.service

# 启动服务
sudo systemctl restart wushizhifu-bot.service

# 检查状态
sudo systemctl status wushizhifu-bot.service
```

### 步骤 5：检查进程

```bash
# 查看所有 Bot 相关进程
ps aux | grep -E "bot.py|python.*bot" | grep -v grep

# 应该只看到一个进程（wushizhifu-bot）
```

### 步骤 6：验证日志

```bash
# 查看正确服务的日志
sudo journalctl -u wushizhifu-bot.service -n 50 --no-pager

# 应该看到：
# ✅ Menu button set: '打开应用'
# ✅ Bot description set successfully
# ✅ WuShiPay System Initialized Successfully
```

## 🔍 验证清单

更新后，请验证：

- [ ] 只有一个 Bot 服务在运行：`wushizhifu-bot.service`
- [ ] 只有一个 `bot.py` 进程在运行
- [ ] 日志显示菜单按钮和描述设置成功
- [ ] 在 Telegram 中测试 Bot 功能正常

## ⚠️ 注意事项

1. **不要同时运行两个 Bot**：这会导致 Telegram Conflict Error
2. **确保只启用一个服务**：`wushizhifu-bot.service`
3. **如果看到冲突错误**：立即停止所有 Bot 进程，然后只启动正确的服务

## 🆘 如果出现问题

如果清理后 Bot 仍然无法正常工作：

```bash
# 1. 停止所有服务
sudo systemctl stop wushipay-bot.service 2>/dev/null
sudo systemctl stop wushizhifu-bot.service

# 2. 强制杀死所有进程
sudo pkill -9 -f "bot.py"

# 3. 重新加载 systemd
sudo systemctl daemon-reload

# 4. 只启动正确服务
sudo systemctl start wushizhifu-bot.service

# 5. 检查状态
sudo systemctl status wushizhifu-bot.service
```

