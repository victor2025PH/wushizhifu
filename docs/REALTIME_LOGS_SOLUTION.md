# 实时日志显示问题解决方案

## 问题描述

使用 `sudo journalctl -u otc-bot.service -f` 或 `sudo journalctl -u wushizhifu-bot.service -f` 查看日志时，日志不是实时显示的。当在 Telegram 中点击按钮时，日志需要等待一段时间（有时几分钟）才能看到。

## 问题原因

**Python 输出缓冲**: Python 默认会对标准输出（stdout）进行缓冲：
- 在交互式终端中：Python 使用行缓冲（line buffered），每行输出后会立即刷新
- 在非交互式环境中（如 systemd service）：Python 使用块缓冲（block buffered），只有当缓冲区满（通常是 4KB）或程序退出时才会刷新

当 Python 程序作为 systemd service 运行时，由于输出被缓冲，`journalctl -f` 无法实时看到日志，需要等待缓冲区刷新。

## 解决方案

在 systemd 服务文件中添加 `PYTHONUNBUFFERED=1` 环境变量，禁用 Python 的输出缓冲。

### 已修改的文件

1. **`botB/otc-bot.service`**:
   ```ini
   Environment="PYTHONUNBUFFERED=1"
   ```

2. **`botA/wushizhifu-bot.service`**:
   ```ini
   Environment="PYTHONUNBUFFERED=1"
   ```

3. **GitHub Actions 工作流**:
   - `deploy-botB.yml`: 更新为始终复制服务文件（不再只在不存在时复制）
   - `deploy-botA.yml`: 添加了服务文件复制步骤

## 部署步骤

### 自动部署（推荐）

修改已提交到 GitHub，但需要触发部署：

#### BotB 部署触发

由于 `deploy-botB.yml` 的 `paths` 过滤器只包含 `botB/**`，服务文件的变化会自动触发部署。如果需要立即部署，可以：

1. 等待 GitHub Actions 自动运行（如果 `botB/otc-bot.service` 变化已触发）
2. 或者在 GitHub 仓库的 Actions 页面手动触发 `Deploy Bot B` 工作流

#### BotA 部署触发

`deploy-botA.yml` 的 `paths` 过滤器包含 `botA/**`，服务文件的变化会自动触发部署。如果需要立即部署：

1. 等待 GitHub Actions 自动运行（如果 `botA/wushizhifu-bot.service` 变化已触发）
2. 或者在 GitHub 仓库的 Actions 页面手动触发 `Deploy Bot A` 工作流

### 手动部署（如果自动部署未触发）

如果 GitHub Actions 没有自动触发，可以手动在服务器上更新：

#### BotB

```bash
# SSH 到服务器
ssh ubuntu@your-server

# 进入项目目录
cd /home/ubuntu/wushizhifu

# 拉取最新代码
git pull origin main

# 更新服务文件
sudo cp botB/otc-bot.service /etc/systemd/system/otc-bot.service

# 重新加载 systemd 配置
sudo systemctl daemon-reload

# 重启服务
sudo systemctl restart otc-bot.service

# 验证服务状态
sudo systemctl status otc-bot.service
```

#### BotA

```bash
# SSH 到服务器
ssh ubuntu@your-server

# 进入项目目录
cd /home/ubuntu/wushizhifu

# 拉取最新代码
git pull origin main

# 更新服务文件
sudo cp botA/wushizhifu-bot.service /etc/systemd/system/wushizhifu-bot.service

# 重新加载 systemd 配置
sudo systemctl daemon-reload

# 重启服务
sudo systemctl restart wushizhifu-bot.service

# 验证服务状态
sudo systemctl status wushizhifu-bot.service
```

## 验证修复

修复后，使用以下命令验证日志是否实时显示：

### BotB

```bash
# 实时跟踪日志
sudo journalctl -u otc-bot.service -f

# 在另一个终端或 Telegram 中点击按钮
# 日志应该立即显示（通常在 1 秒内）
```

### BotA

```bash
# 实时跟踪日志
sudo journalctl -u wushizhifu-bot.service -f

# 在另一个终端或 Telegram 中点击按钮
# 日志应该立即显示（通常在 1 秒内）
```

## 技术说明

### PYTHONUNBUFFERED 环境变量

- **作用**: 禁用 Python 的标准输出和标准错误缓冲
- **效果**: 
  - `print()` 和 `logging` 的输出会立即写入到 stdout/stderr
  - 不需要等待缓冲区满或程序退出
- **影响**: 
  - 日志实时性显著提高
  - 对性能影响极小（日志输出本身是 I/O 操作）
  - 不会影响代码逻辑

### 为什么需要这个设置？

1. **Python 默认行为**:
   - 交互式环境（终端）: 行缓冲（line buffered）
   - 非交互式环境（如 systemd）: 块缓冲（block buffered，通常是 4KB）

2. **systemd 日志**:
   - systemd 从 stdout/stderr 读取日志并写入 journal
   - 如果 Python 缓冲输出，systemd 无法立即读取到日志

3. **实时跟踪**:
   - `journalctl -f` 只能显示已经写入到 journal 的日志
   - 缓冲的日志无法实时显示

### 其他相关环境变量

- `PYTHONUNBUFFERED=1`: 禁用所有输出缓冲（推荐）
- `PYTHONIOENCODING=utf-8`: 设置 I/O 编码（如果需要）

## 相关参考

- [Python Environment Variables - PYTHONUNBUFFERED](https://docs.python.org/3/using/cmdline.html#envvar-PYTHONUNBUFFERED)
- [systemd.exec - Standard Output and Standard Error](https://www.freedesktop.org/software/systemd/man/systemd.exec.html#StandardOutput=)
- [journalctl(1) - Follow](https://www.freedesktop.org/software/systemd/man/journalctl.html#--follow,-f)

## 总结

✅ **问题**: Python 输出缓冲导致日志延迟显示  
✅ **解决**: 添加 `PYTHONUNBUFFERED=1` 环境变量  
✅ **文件**: `botB/otc-bot.service`, `botA/wushizhifu-bot.service`  
✅ **部署**: 通过 GitHub Actions 或手动更新服务文件  
✅ **验证**: 使用 `journalctl -f` 实时查看日志

修复后，日志应该能够实时显示，点击按钮后通常在 1 秒内就能看到相关日志。

