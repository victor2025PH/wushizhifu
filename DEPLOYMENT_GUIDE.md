# 部署指南

## 📦 最新更新内容

本次更新包含以下功能：

### ✅ 批量用户操作功能
- `/batch_set_vip` - 批量设置VIP等级（最多50个用户）
- `/batch_disable_users` - 批量禁用用户（最多50个用户）
- `/batch_enable_users` - 批量启用用户（最多50个用户）
- `/batch_export_users` - 批量导出用户数据（最多100个用户）

### ✅ 所有功能模块
- P0功能：100%完成
- P1功能：100%完成
- P2功能：100%完成
- 用户体验优化：100%完成

## 🚀 GitHub Actions 自动部署

### 配置说明

1. **GitHub Secrets 配置**
   
   在GitHub仓库设置中添加以下Secrets：
   - `SSH_PRIVATE_KEY`: 服务器SSH私钥
   - `SERVER_HOST`: 服务器地址
   - `SERVER_USER`: 服务器用户名
   - `SERVER_PATH`: 服务器项目路径（如：/home/ubuntu/wushizhifu）

2. **工作流触发**
   - 推送到 `main` 分支时自动触发
   - 手动触发：在Actions页面点击"Run workflow"

3. **部署流程**
   - 自动拉取最新代码
   - 安装Python依赖
   - 重启Bot B服务

### 手动部署

如果GitHub Actions未配置，可以手动部署：

```bash
# 在服务器上
cd /home/ubuntu/wushizhifu
git pull origin main

cd botB
source venv/bin/activate
pip install -r requirements.txt

# 重启服务
sudo systemctl restart otc-bot.service

# 查看日志
sudo journalctl -u otc-bot.service -f
```

## 📝 更新日志

### 2025-01-XX
- ✅ 完成批量用户操作功能开发
- ✅ 修复语法错误
- ✅ 添加GitHub Actions部署配置
- ✅ 更新帮助文档

---

**部署完成后，请测试所有新功能是否正常工作。**
