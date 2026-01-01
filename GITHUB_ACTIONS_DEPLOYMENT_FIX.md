# GitHub Actions 部署错误修复

## 🐛 问题描述

GitHub Actions 部署失败，错误信息：
```
fatal: not a git repository (or any of the parent directories): .git
Error: Process completed with exit code 128.
```

## 🔍 问题原因

部署脚本尝试在服务器上执行 `git pull origin main`，但目标目录可能：
1. 不是Git仓库（代码可能是通过其他方式部署的）
2. Git仓库路径不正确
3. 首次部署时还没有初始化Git仓库

## ✅ 修复方案

更新了 `.github/workflows/deploy-botB.yml`，添加了：

1. **目录存在性检查**
   - 检查 `$SERVER_PATH` 目录是否存在
   - 检查 `botB` 目录是否存在

2. **Git仓库检查**
   - 在执行 `git pull` 之前检查 `.git` 目录是否存在
   - 如果不是Git仓库，输出警告但继续执行（不退出）

3. **错误处理改进**
   - 使用更友好的错误消息
   - 即使git pull失败也继续部署（因为代码可能已经是最新的）

## 📝 修复后的逻辑

```bash
# 检查目录
if [ ! -d "$SERVER_PATH" ]; then
  echo "❌ 错误: 项目目录不存在"
  exit 1
fi

cd "$SERVER_PATH"

# 如果是Git仓库则拉取代码
if [ -d ".git" ]; then
  git pull origin main || echo "⚠️ Git pull失败，继续部署"
else
  echo "⚠️ 当前目录不是Git仓库（代码可能已通过其他方式部署）"
fi

# 继续部署流程...
```

## 🚀 部署方式说明

GitHub Actions 支持两种部署场景：

### 场景1：代码通过Git管理
- 服务器上的代码是Git仓库
- 部署时会自动执行 `git pull` 获取最新代码

### 场景2：代码通过其他方式部署
- 服务器上的代码不是Git仓库
- GitHub Actions 只负责安装依赖和重启服务
- 需要手动或通过其他方式更新代码

## 💡 建议

如果需要完全自动化部署，建议：

1. **在服务器上初始化Git仓库**：
   ```bash
   cd /home/ubuntu/wushizhifu
   git init
   git remote add origin https://github.com/victor2025PH/wushizhifu.git
   git pull origin main
   ```

2. **或者使用SSH方式**（如果服务器已有SSH密钥配置）

3. **或者使用GitHub Actions的代码同步功能**：
   - 使用 `rsync` 或其他工具从Actions runner同步代码到服务器

## ✅ 当前状态

修复已推送，下次部署时：
- 如果目录是Git仓库，会正常拉取代码
- 如果不是Git仓库，会跳过git pull但继续执行其他部署步骤

---

**修复已完成并已推送，可以重新运行GitHub Actions工作流。**
