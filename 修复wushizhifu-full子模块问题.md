# 修复 wushizhifu-full 子模块问题

## 问题分析

`wushizhifu-full` 被 Git 当作子模块处理，但子模块配置不正确，导致：
1. 克隆到服务器后目录为空
2. 文件无法正常部署

## 解决方案：将子模块转换为普通目录

### 步骤 1: 在本地执行（Windows）

```bash
cd D:\wushizhifu

# 1. 移除 Git 的子模块索引
git rm --cached wushizhifu-full

# 2. 删除 .git/modules/wushizhifu-full（如果存在）
rm -rf .git/modules/wushizhifu-full

# 3. 将 wushizhifu-full 作为普通目录添加
git add wushizhifu-full/

# 4. 提交更改
git commit -m "将 wushizhifu-full 从子模块转换为普通目录"

# 5. 推送到 GitHub
git push origin main
```

### 步骤 2: 在服务器上重新克隆

```bash
cd ~/wushizhifu
rm -rf repo
git clone https://github.com/victor2025PH/wushizhifu.git repo

# 现在应该能看到文件了
ls -la repo/wushizhifu-full/package.json
```

## 或者：直接在服务器上上传文件

如果上面的方法有问题，可以：

1. 使用 WinSCP 将 `D:\wushizhifu\wushizhifu-full` 上传到服务器
2. 上传到 `/home/ubuntu/wushizhifu/wushizhifu-full`
3. 然后运行部署脚本

