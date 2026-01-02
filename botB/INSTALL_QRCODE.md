# 安装二维码生成库 (qrcode)

## 问题说明

如果看到以下错误：
- `qrcode library not available. QR code generation will be disabled.`
- `二维码生成功能不可用，请安装qrcode库`

说明需要在 **bot 运行的虚拟环境** 中安装 `qrcode` 库。

⚠️ **重要**：bot 运行在虚拟环境中，系统级的安装（如 `apt install python3-qrcode`）不会生效！

## 快速安装（推荐）

### 方法1：使用自动安装脚本

```bash
# 进入 botB 目录
cd /home/ubuntu/wushizhifu/botB

# 运行安装脚本
chmod +x install_qrcode.sh
./install_qrcode.sh
```

脚本会自动：
1. 检测 systemd 服务配置中的虚拟环境路径
2. 在正确的虚拟环境中安装 qrcode[pil]
3. 重启 bot 服务
4. 验证安装

### 方法2：手动安装（如果脚本失败）

#### 步骤1：找到虚拟环境路径

```bash
# 查看服务配置
sudo cat /etc/systemd/system/otc-bot.service | grep ExecStart
```

通常会显示类似：
```
ExecStart=/home/ubuntu/wushizhifu/botB/venv/bin/python /home/ubuntu/wushizhifu/botB/bot.py
```

虚拟环境路径就是 `/home/ubuntu/wushizhifu/botB/venv`

#### 步骤2：使用虚拟环境的 pip 安装

```bash
# 直接使用虚拟环境的 pip（推荐）
/home/ubuntu/wushizhifu/botB/venv/bin/pip install qrcode[pil]
```

或者：

```bash
# 进入项目目录
cd /home/ubuntu/wushizhifu/botB

# 激活虚拟环境
source venv/bin/activate

# 安装 qrcode
pip install qrcode[pil]

# 退出虚拟环境
deactivate
```

#### 步骤3：重启服务

```bash
sudo systemctl restart otc-bot.service
```

#### 步骤4：验证安装

```bash
# 查看日志，确认没有 "qrcode library not available" 警告
sudo journalctl -u otc-bot.service -n 50 | grep -i qrcode
```

如果看到警告消失，说明安装成功。

## 常见问题

### Q1: 为什么用 apt 安装了还是不行？

**A**: bot 运行在虚拟环境中，系统级的包不会被虚拟环境识别。必须在虚拟环境中安装。

### Q2: 如何确认虚拟环境路径？

```bash
# 方法1：查看服务配置
sudo cat /etc/systemd/system/otc-bot.service | grep ExecStart

# 方法2：查看运行中的进程
ps aux | grep bot.py | grep python
```

### Q3: 安装后还是显示警告？

1. 确认安装到了正确的虚拟环境
2. 确认服务已重启：`sudo systemctl restart otc-bot.service`
3. 查看日志确认：`sudo journalctl -u otc-bot.service -n 50`

### Q4: 找不到 requirements.txt？

如果项目目录中没有 requirements.txt，可以直接安装：

```bash
/home/ubuntu/wushizhifu/botB/venv/bin/pip install qrcode[pil]
```

## 验证安装成功

安装并重启后，在 Telegram 中点击"地址"按钮，应该能看到二维码图片，而不是警告信息。
