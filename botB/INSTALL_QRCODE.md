# 安装二维码生成库 (qrcode)

## 问题说明

如果看到以下错误：
- `qrcode library not available. QR code generation will be disabled.`
- `error: externally-managed-environment` (使用pip install时)

说明需要安装 `qrcode` 库。

## 安装方法

### 方法1：使用虚拟环境（推荐）

```bash
# 进入项目目录
cd /path/to/wushizhifu

# 创建虚拟环境（如果还没有）
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 方法2：使用系统包管理器（Ubuntu/Debian）

```bash
# 安装系统包
sudo apt update
sudo apt install python3-qrcode python3-pil
```

### 方法3：使用pipx（如果已安装）

```bash
pipx install qrcode[pil]
```

### 方法4：使用--break-system-packages（不推荐，但可以工作）

```bash
pip install --break-system-packages qrcode[pil]
```

## 验证安装

安装后，重启bot服务：

```bash
sudo systemctl restart otc-bot.service
```

查看日志确认：

```bash
sudo journalctl -u otc-bot.service -f
```

如果看到 `qrcode library not available` 的警告消失，说明安装成功。

## 注意事项

- 如果使用systemd服务，确保服务配置中的Python路径指向正确的虚拟环境
- 如果使用Docker，需要在Dockerfile中添加安装命令
- 安装后需要重启bot服务才能生效
