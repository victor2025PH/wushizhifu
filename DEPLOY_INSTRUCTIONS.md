# Bot B 群管理功能部署说明

## ✅ 代码已推送到 GitHub

代码已成功推送到 GitHub 仓库：`https://github.com/victor2025PH/wushizhifu.git`

## 🚀 部署步骤

### 方法 1: 使用部署脚本（推荐）

```bash
# 1. SSH 连接到服务器
ssh ubuntu@your-server-ip

# 2. 进入 Bot B 目录
cd /home/ubuntu/wushizhifu/botB

# 3. 执行部署脚本
chmod +x deploy_update.sh
./deploy_update.sh
```

### 方法 2: 手动部署

```bash
# 1. SSH 连接到服务器
ssh ubuntu@your-server-ip

# 2. 进入 Bot B 目录
cd /home/ubuntu/wushizhifu/botB

# 3. 停止服务
sudo systemctl stop otc-bot.service

# 4. 拉取最新代码
git pull origin main

# 5. 激活虚拟环境
source venv/bin/activate

# 6. 安装/更新依赖（如果需要）
pip install -r requirements.txt

# 7. 重启服务
sudo systemctl start otc-bot.service

# 8. 检查服务状态
sudo systemctl status otc-bot.service

# 9. 查看日志
sudo journalctl -u otc-bot.service -f
```

## 📋 本次更新内容

### 新增功能
1. **群组验证系统**
   - 新成员加入时自动验证
   - 支持问题验证模式
   - 管理员审核功能

2. **敏感词过滤**
   - 自动检测敏感词
   - 支持警告、删除、封禁三种处理方式
   - 支持群组级别和全局敏感词

3. **群组管理功能**
   - 群组审核（查看待审核成员）
   - 群组列表（查看所有管理的群组）
   - 群组设置（配置群组信息）
   - 全部通过/全部拒绝功能

### 新增文件
- `botB/handlers/group_management_handlers.py` - 群组管理处理器
- `botB/repositories/group_repository.py` - 群组数据访问层
- `botB/repositories/sensitive_words_repository.py` - 敏感词数据访问层
- `botB/repositories/verification_repository.py` - 验证数据访问层
- `botB/services/verification_service.py` - 验证服务层

### 数据库更新
- 新增 `groups` 表
- 新增 `group_members` 表
- 新增 `sensitive_words` 表
- 新增 `verification_questions` 表
- 新增 `verification_records` 表
- 新增 `verification_configs` 表

### UI 更新
- 扩展了底部按钮（reply keyboard）
- 群组中显示：`✅ 群组审核`、`📋 群组列表`
- 私聊中显示：`✅ 群组审核`、`📋 群组列表`、`⚙️ 群组设置`

## 🔍 部署后检查

### 1. 检查服务状态
```bash
sudo systemctl status otc-bot.service
```

### 2. 查看日志
```bash
# 实时查看日志
sudo journalctl -u otc-bot.service -f

# 查看最近 100 行日志
sudo journalctl -u otc-bot.service -n 100
```

### 3. 测试功能
1. **群组验证**
   - 将机器人添加到测试群组
   - 启用群组验证（需要配置）
   - 测试新成员加入验证流程

2. **敏感词过滤**
   - 添加敏感词（使用命令或管理界面）
   - 测试敏感词检测和处理

3. **群组管理**
   - 点击 `✅ 群组审核` 查看待审核成员
   - 点击 `📋 群组列表` 查看所有群组
   - 测试 `✅ 全部通过` 和 `❌ 全部拒绝` 功能

## ⚠️ 注意事项

1. **数据库迁移**
   - 数据库表会自动创建（在首次运行时）
   - 无需手动迁移数据

2. **配置要求**
   - 确保 `.env` 文件包含 `BOT_TOKEN_B`
   - 确保机器人有群组管理权限

3. **权限要求**
   - 机器人必须是群组管理员才能执行封禁等操作
   - 确保机器人有删除消息的权限

## 🐛 故障排除

### 服务无法启动
```bash
# 查看详细错误
sudo journalctl -u otc-bot.service -n 50

# 手动运行测试
cd /home/ubuntu/wushizhifu/botB
source venv/bin/activate
python bot.py
```

### 数据库错误
```bash
# 检查数据库文件权限
ls -la /home/ubuntu/wushizhifu/wushipay.db

# 检查数据库连接
cd /home/ubuntu/wushizhifu/botB
source venv/bin/activate
python -c "from database import db; print(db.db_path)"
```

### 导入错误
```bash
# 检查 Python 路径
cd /home/ubuntu/wushizhifu/botB
source venv/bin/activate
python -c "import sys; print(sys.path)"

# 重新安装依赖
pip install --force-reinstall -r requirements.txt
```

## 📞 支持

如有问题，请查看：
- 日志：`sudo journalctl -u otc-bot.service -f`
- 配置文件：`botB/config.py`
- 环境变量：`.env` 文件
