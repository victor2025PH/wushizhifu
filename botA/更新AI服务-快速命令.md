# 更新并重启 AI 服务 - 快速命令

## 🚀 一键更新脚本

```bash
# 赋予执行权限（首次执行）
chmod +x ~/wushizhifu/bot/更新并重启AI服务.sh

# 执行更新
~/wushizhifu/bot/更新并重启AI服务.sh
```

## 📋 手动执行步骤

### 步骤 1：拉取最新代码
```bash
cd ~/wushizhifu/bot
git pull origin main
```

### 步骤 2：清理缓存
```bash
find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null
```

### 步骤 3：确认 .env 已更新
```bash
# 检查 API 密钥是否已配置（不显示实际密钥值）
grep -E "OPENAI_API_KEY|GEMINI_API_KEY" .env | sed 's/=.*/=***/'
```

### 步骤 4：重启服务
```bash
sudo systemctl restart wushizhifu-bot
```

### 步骤 5：查看启动日志
```bash
# 等待 5 秒让服务启动
sleep 5

# 查看 AI 服务初始化日志
sudo journalctl -u wushizhifu-bot -n 50 | grep -i "ai\|openai\|gemini\|initialized\|error"
```

## ✅ 验证 AI 服务

### 查看初始化日志
应该看到以下之一：
- ✅ `OpenAI service initialized successfully`
- ✅ `Gemini service initialized successfully (as primary)`
- ✅ `Gemini service initialized successfully (as fallback)`

### 如果看到错误
- ❌ `No AI service available` - 检查 API 密钥配置
- ❌ `401 Unauthorized` - OpenAI 密钥无效
- ❌ `404 models/... not found` - Gemini 模型名称问题（已修复）

## 🔍 完整诊断

如果 AI 仍然不可用，执行完整诊断：

```bash
cd ~/wushizhifu/bot
source venv/bin/activate

python3 << 'EOF'
import os
from dotenv import load_dotenv
load_dotenv()

print("=== AI 服务诊断 ===")
print()

print("1. 环境变量检查：")
openai_key = os.getenv('OPENAI_API_KEY')
gemini_key = os.getenv('GEMINI_API_KEY')
print(f"   OPENAI_API_KEY: {'✅ 已配置' if openai_key else '❌ 未配置'}")
print(f"   GEMINI_API_KEY: {'✅ 已配置' if gemini_key else '❌ 未配置'}")
print()

print("2. AI 服务初始化测试：")
try:
    from services.ai_service import get_ai_service
    ai_service = get_ai_service()
    
    print(f"   AI 服务可用: {'✅ 是' if ai_service.is_available() else '❌ 否'}")
    print(f"   OpenAI 可用: {'✅ 是' if ai_service.openai_available else '❌ 否'}")
    print(f"   Gemini 可用: {'✅ 是' if ai_service.gemini_available else '❌ 否'}")
    print(f"   当前提供商: {ai_service.current_provider or '无'}")
    print()
    
    if ai_service.is_available():
        print("3. 测试生成响应：")
        try:
            response = ai_service.generate_response("你好")
            print(f"   ✅ 成功生成响应: {response[:100]}...")
        except Exception as e:
            print(f"   ❌ 生成响应失败: {e}")
    else:
        print("3. ❌ AI 服务不可用，无法测试")
        
except Exception as e:
    print(f"❌ 初始化失败: {e}")
    import traceback
    traceback.print_exc()
EOF
```

## 📝 常见问题

### Q: 修改 .env 后需要重启吗？
A: 是的，必须重启服务才能加载新的环境变量。

### Q: 如何查看实时日志？
```bash
sudo journalctl -u wushizhifu-bot -f
```

### Q: 如何确认服务已启动？
```bash
sudo systemctl status wushizhifu-bot
```

### Q: 如何查看最新的错误日志？
```bash
sudo journalctl -u wushizhifu-bot -n 100 --no-pager | grep -i "error\|exception\|traceback" -A 5
```

