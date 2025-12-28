# AI 服务修复方案 - 立即执行

## 🔍 问题确认

根据日志显示，问题很明确：
```
WARNING - openai package not installed, install with: pip install openai
WARNING - google-generativeai package not installed
WARNING - No AI service available
```

**根本原因**：虽然您在本地虚拟环境中看到了包，但 **systemd 服务运行时使用的 Python 环境可能不同**。

## ✅ 立即修复步骤

### 第一步：在正确的虚拟环境中安装包

```bash
# 1. 进入项目目录并激活虚拟环境
cd ~/wushizhifu/bot
source venv/bin/activate

# 2. 确认虚拟环境已激活（提示符应该显示 (venv)）
which python  # 应该显示 ~/wushizhifu/bot/venv/bin/python

# 3. 安装缺失的包
pip install openai google-generativeai

# 4. 验证安装
pip list | grep -E "openai|google-generativeai"
```

### 第二步：确认 systemd 服务配置正确

```bash
# 查看服务配置
sudo cat /etc/systemd/system/wushizhifu-bot.service
```

**确保配置如下**（关键部分）：
```ini
[Service]
WorkingDirectory=/home/ubuntu/wushizhifu/bot
ExecStart=/home/ubuntu/wushizhifu/bot/venv/bin/python /home/ubuntu/wushizhifu/bot/bot.py
Environment="PATH=/home/ubuntu/wushizhifu/bot/venv/bin:$PATH"
```

如果 `ExecStart` 不是使用虚拟环境的 Python，需要修改。

### 第三步：重启服务并验证

```bash
# 重启服务
sudo systemctl daemon-reload
sudo systemctl restart wushizhifu-bot

# 等待 3 秒
sleep 3

# 查看日志，应该看到成功初始化
sudo journalctl -u wushizhifu-bot -n 50 | grep -i "ai\|openai\|gemini"
```

**应该看到**：
```
✅ OpenAI service initialized successfully
或
✅ Gemini service initialized successfully
```

### 第四步：测试 AI 服务

```bash
# 进入虚拟环境测试
cd ~/wushizhifu/bot
source venv/bin/activate

python3 << 'EOF'
import os
from dotenv import load_dotenv
load_dotenv()

print("=== 测试 AI 服务 ===")
from services.ai_service import get_ai_service
ai_service = get_ai_service()

print(f"AI 服务可用: {ai_service.is_available()}")
print(f"OpenAI 可用: {ai_service.openai_available}")
print(f"Gemini 可用: {ai_service.gemini_available}")
print(f"当前提供商: {ai_service.current_provider}")

if ai_service.is_available():
    print("\n✅ AI 服务已成功初始化！")
else:
    print("\n❌ AI 服务仍然不可用")
EOF
```

## 🔧 如果服务配置错误

如果 systemd 服务没有使用虚拟环境，修改服务文件：

```bash
# 编辑服务文件
sudo nano /etc/systemd/system/wushizhifu-bot.service
```

**确保 ExecStart 使用虚拟环境的 Python**：
```ini
[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/wushizhifu/bot
ExecStart=/home/ubuntu/wushizhifu/bot/venv/bin/python /home/ubuntu/wushizhifu/bot/bot.py
Restart=on-failure
RestartSec=10
Environment="PATH=/home/ubuntu/wushizhifu/bot/venv/bin:/usr/bin:/bin"
EnvironmentFile=/home/ubuntu/wushizhifu/bot/.env
```

然后：
```bash
sudo systemctl daemon-reload
sudo systemctl restart wushizhifu-bot
```

## 📋 一键修复脚本

```bash
#!/bin/bash
cd ~/wushizhifu/bot

echo "=== 修复 AI 服务 ==="

# 激活虚拟环境
source venv/bin/activate

# 安装包
echo "安装 AI 相关包..."
pip install openai google-generativeai

# 验证安装
echo ""
echo "验证安装..."
pip list | grep -E "openai|google-generativeai"

# 重启服务
echo ""
echo "重启服务..."
sudo systemctl restart wushizhifu-bot

# 等待启动
sleep 3

# 查看日志
echo ""
echo "查看启动日志..."
sudo journalctl -u wushizhifu-bot -n 30 | grep -i "ai\|openai\|gemini"
```

保存为 `fix_ai_service.sh`，然后执行：
```bash
chmod +x fix_ai_service.sh
./fix_ai_service.sh
```

## ✅ 预期结果

修复后，日志应该显示：
- ✅ `OpenAI service initialized successfully` 或
- ✅ `Gemini service initialized successfully`
- ✅ 不再有 "package not installed" 警告
- ✅ `No AI service available` 警告消失

用户发送消息时，AI 应该能正常回复。

