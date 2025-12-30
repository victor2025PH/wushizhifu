# 实时日志显示修复方案

## 问题描述

使用 `sudo journalctl -u otc-bot.service -f` 查看日志时，日志不是实时显示的，点击按钮后的日志需要等待一段时间才能看到。

## 问题原因

Python 默认会对标准输出（stdout）进行缓冲，导致日志不会立即写入到 systemd journal。当使用 `journalctl -f` 实时跟踪日志时，由于缓冲机制，日志会延迟显示。

## 解决方案

在 systemd 服务文件中添加 `PYTHONUNBUFFERED=1` 环境变量，禁用 Python 的输出缓冲。

### 修改内容

在 `otc-bot.service` 的 `[Service]`  section 中添加：

```ini
Environment="PYTHONUNBUFFERED=1"
```

### 完整的服务文件配置

```ini
[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/wushizhifu/botB
Environment="PATH=/home/ubuntu/wushizhifu/botB/venv/bin:/usr/local/bin:/usr/bin:/bin"
Environment="PYTHONUNBUFFERED=1"  # 新增：禁用Python输出缓冲
ExecStart=/home/ubuntu/wushizhifu/botB/venv/bin/python /home/ubuntu/wushizhifu/botB/bot.py
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal
```

## 应用修复

### 方法 1: 手动更新服务文件（如果服务文件在服务器上）

1. SSH 到服务器
2. 编辑服务文件：
   ```bash
   sudo nano /etc/systemd/system/otc-bot.service
   ```
3. 在 `Environment="PATH=..."` 下面添加：
   ```ini
   Environment="PYTHONUNBUFFERED=1"
   ```
4. 重新加载 systemd 配置并重启服务：
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl restart otc-bot.service
   ```

### 方法 2: 通过 GitHub Actions 部署（推荐）

如果服务文件在代码仓库中（如 `botB/otc-bot.service`），修改后提交到 GitHub，GitHub Actions 会自动部署并应用更改。

## 验证修复

修复后，使用以下命令验证日志是否实时显示：

```bash
# 实时跟踪日志
sudo journalctl -u otc-bot.service -f

# 在另一个终端或 Telegram 中点击按钮
# 日志应该立即显示（通常在 1 秒内）
```

## 技术说明

### PYTHONUNBUFFERED 环境变量

- **作用**: 禁用 Python 的标准输出缓冲
- **效果**: `print()` 和 `logging` 的输出会立即写入到 stdout/stderr
- **影响**: 
  - 日志实时性提高
  - 对性能影响极小（日志输出本身是 I/O 操作）
  - 不会影响代码逻辑

### 为什么需要这个设置？

1. **Python 默认行为**: Python 默认对 stdout 进行行缓冲（line buffered）或块缓冲（block buffered）
2. **systemd 日志**: systemd 从 stdout/stderr 读取日志，如果 Python 缓冲输出，日志会延迟写入
3. **实时跟踪**: `journalctl -f` 只能显示已经写入到 journal 的日志，缓冲的日志无法实时显示

## 相关参考

- Python 文档: [Python Environment Variables](https://docs.python.org/3/using/cmdline.html#envvar-PYTHONUNBUFFERED)
- systemd 文档: [Standard Output and Standard Error](https://www.freedesktop.org/software/systemd/man/systemd.exec.html#StandardOutput=)
- journalctl 文档: [journalctl(1)](https://www.freedesktop.org/software/systemd/man/journalctl.html)

