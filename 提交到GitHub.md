# 提交 Bot B 代码到 GitHub

## 📋 提交步骤

### 1. 检查当前状态

```bash
cd D:\wushizhifu
git status
```

### 2. 添加所有更改

```bash
git add .
```

### 3. 提交更改

```bash
git commit -m "Bot B: 实现核心功能 - 管理员快捷命令、数学计算、UI增强"
```

### 4. 推送到 GitHub

```bash
git push origin main
```

## ✅ 完整命令（一键执行）

```bash
cd D:\wushizhifu
git add .
git commit -m "Bot B: 实现核心功能 - 管理员快捷命令、数学计算、UI增强"
git push origin main
```

## 🔍 验证 GitHub Actions

推送后，访问：
https://github.com/victor2025PH/wushizhifu/actions

应该看到：
- `Deploy Bot B` 工作流自动触发
- 查看运行状态和日志

## 📝 提交内容

本次提交包含：

### Bot B 核心功能
- ✅ 管理员快捷命令（w01-w04, w08）
- ✅ 数学表达式解析和计算
- ✅ 结算账单生成
- ✅ 持久菜单（ReplyKeyboard）
- ✅ 账单确认按钮（InlineKeyboard）
- ✅ 收据样式账单模板

### 新增文件
- `botB/handlers/message_handlers.py`
- `botB/handlers/callback_handlers.py`
- `botB/services/math_service.py`
- `botB/services/settlement_service.py`
- `botB/keyboards/reply_keyboard.py`
- `botB/keyboards/inline_keyboard.py`
- `botB/功能说明.md`
- `botB/UI功能说明.md`
- `botB/快捷指令列表.md`

### 修改文件
- `botB/bot.py` - 集成消息和回调处理器
- `botB/config.py` - 添加 INITIAL_ADMINS
- `botB/services/settlement_service.py` - 更新账单格式

## ⚙️ GitHub Actions 配置

确保 `.github/workflows/deploy-botB.yml` 已配置：

- 触发条件：`botB/**` 路径更改
- SSH 部署到服务器
- 自动重启 `botB.service`

## 🚀 部署后验证

在服务器上验证：

```bash
# 检查服务状态
sudo systemctl status botB.service

# 查看日志
sudo journalctl -u botB.service -n 50 -f
```

## 📞 如果 Actions 失败

1. 检查 GitHub Secrets 配置
2. 查看 Actions 日志
3. 手动部署：

```bash
# SSH 到服务器
ssh ubuntu@165.154.203.182

# 拉取代码
cd /home/ubuntu/wushizhifu
git pull origin main

# 重启服务
sudo systemctl restart botB.service
```

