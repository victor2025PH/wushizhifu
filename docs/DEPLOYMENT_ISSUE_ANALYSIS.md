# Miniapp 部署问题深入分析

## 问题描述

1. **UI恢复到旧版本**：汇率计算和交易记录按钮又出现了，开通帐户按钮消失了
2. **网页版正常更新**：网页版修复后能正常更新
3. **Miniapp不更新**：Miniapp始终显示旧版本，新修改不生效

## 根本原因分析

### 1. 服务器上存在多个前端源代码目录

根据 GitHub Actions 工作流代码，服务器上可能同时存在：
- `/home/ubuntu/wushizhifu/repo/wushizhifu-full/` (优先检查)
- `/home/ubuntu/wushizhifu/wushizhifu-full/` (备选)

**问题**：如果 `repo/wushizhifu-full` 目录存在但代码是旧的，工作流会优先使用这个旧目录进行构建，导致部署的始终是旧代码。

### 2. 构建和部署步骤分离导致的不一致

工作流分为两个步骤：
1. **步骤1：Pull Code and Build** - 在 `repo/wushizhifu-full` 或 `wushizhifu-full` 中构建
2. **步骤2：Deploy Frontend** - 从构建好的 `dist` 目录复制到 `frontend/dist`

**问题**：
- 如果步骤1使用的是旧代码目录（`repo/wushizhifu-full`），构建出的就是旧代码
- 步骤2只是复制，不会检查代码是否是最新的
- 两个步骤使用不同的目录判断逻辑，可能导致不一致

### 3. Git Pull 的位置问题

```bash
cd /home/ubuntu/wushizhifu
git pull origin main
```

**问题**：
- Git pull 在项目根目录执行
- 如果 `wushizhifu-full` 是 Git 子模块（submodule），需要在子模块目录中单独 pull
- 如果 `repo/wushizhifu-full` 是独立目录或旧版本，不会自动更新

### 4. 前端代码目录结构混乱

可能的情况：
- `wushizhifu-full` 是最新的代码目录
- `repo/wushizhifu-full` 是旧的代码目录（可能是历史遗留）
- 工作流优先选择 `repo/wushizhifu-full`，导致始终构建旧代码

### 5. 构建缓存问题

即使代码更新了，如果构建缓存没有清理：
- `node_modules` 可能包含旧依赖
- 构建工具（Vite/Webpack）的缓存可能保留旧文件
- 构建出的文件可能混合新旧代码

### 6. 部署目录权限和文件残留

虽然工作流中有删除旧文件的逻辑：
```bash
sudo rm -rf "$TARGET_DIR"/*
```

**问题**：
- 可能存在隐藏文件（以 `.` 开头）没有被删除
- 权限问题可能导致部分文件无法删除
- 如果删除不彻底，新旧文件混合，可能导致加载了旧的 JS 文件

### 7. 浏览器/Telegram 缓存

即使服务器文件更新了：
- 浏览器缓存可能导致加载旧的 JS/CSS 文件
- Telegram WebApp 可能有自己的缓存机制
- Service Worker 缓存（如果存在）

## 为什么网页版正常但 Miniapp 不正常？

可能的原因：

1. **不同的访问路径**
   - 网页版可能访问的是不同的域名或路径
   - Miniapp 可能有自己的 CDN 或缓存层

2. **Telegram WebApp 的特殊性**
   - Telegram WebApp 可能有独立的缓存机制
   - 可能使用了不同的文件加载逻辑

3. **构建输出不一致**
   - 如果构建时使用了不同的配置，可能生成不同的文件
   - 文件哈希（hash）可能不同，导致浏览器认为文件已更新

## 诊断步骤

### 1. 检查服务器目录结构

```bash
# 检查所有可能的前端目录
ls -la /home/ubuntu/wushizhifu/ | grep wushizhifu-full
ls -la /home/ubuntu/wushizhifu/repo/ 2>/dev/null

# 检查部署目录
ls -la /home/ubuntu/wushizhifu/frontend/dist/

# 检查构建时间
stat /home/ubuntu/wushizhifu/wushizhifu-full/dist/index.html
stat /home/ubuntu/wushizhifu/repo/wushizhifu-full/dist/index.html 2>/dev/null
stat /home/ubuntu/wushizhifu/frontend/dist/index.html
```

### 2. 检查 Git 状态

```bash
cd /home/ubuntu/wushizhifu
git status
git log --oneline -5

# 如果是子模块
cd wushizhifu-full
git status
git log --oneline -5
```

### 3. 检查构建产物

```bash
# 检查最新的构建文件内容
grep -r "openAccount\|开通帐户" /home/ubuntu/wushizhifu/wushizhifu-full/dist/
grep -r "openAccount\|开通帐户" /home/ubuntu/wushizhifu/repo/wushizhifu-full/dist/ 2>/dev/null
grep -r "openAccount\|开通帐户" /home/ubuntu/wushizhifu/frontend/dist/
```

### 4. 检查 Nginx 配置

```bash
# 检查 Nginx 实际使用的 root 目录
cat /etc/nginx/sites-available/50zf.usdt2026.cc | grep root
```

### 5. 检查文件时间戳

```bash
# 比较三个位置的 index.html 修改时间
find /home/ubuntu/wushizhifu -name "index.html" -type f -exec ls -lh {} \;
```

## 修复方案

### 方案1：统一源代码目录（推荐）

**步骤**：
1. 确定唯一的前端源代码目录（应该是 `wushizhifu-full`）
2. 删除或重命名 `repo/wushizhifu-full` 目录（如果是旧代码）
3. 修改 GitHub Actions 工作流，只使用 `wushizhifu-full` 目录
4. 确保 Git pull 正确更新该目录

**优点**：
- 简单明确，避免混乱
- 易于维护和调试

### 方案2：修复目录选择逻辑

**步骤**：
1. 检查两个目录的 Git 提交时间，使用最新的
2. 或者始终使用 `wushizhifu-full`，忽略 `repo/wushizhifu-full`
3. 在构建前确保代码是最新的（添加额外的 git pull）

**优点**：
- 保留灵活性
- 自动选择最新代码

### 方案3：清理并重新构建

**步骤**：
1. 清理所有构建缓存：`rm -rf node_modules dist .vite`
2. 清理部署目录：`sudo rm -rf /home/ubuntu/wushizhifu/frontend/dist/*`
3. 确保代码是最新的
4. 重新构建和部署

**优点**：
- 彻底解决缓存问题
- 确保干净的构建环境

### 方案4：强制更新构建

**步骤**：
1. 在构建前强制 git pull（包括子模块）
2. 清理构建缓存
3. 使用 `npm run build -- --force` 强制重新构建
4. 部署时使用 `rsync --delete` 确保完全同步

**优点**：
- 确保使用最新代码
- 避免文件残留

## 推荐的完整修复流程

### 立即执行的诊断命令

```bash
# 1. 检查目录结构
cd /home/ubuntu/wushizhifu
echo "=== 目录结构 ==="
ls -la | grep -E "wushizhifu-full|repo"

# 2. 检查 Git 状态
echo "=== Git 状态 ==="
git status
git log --oneline -3

# 3. 检查两个前端目录的最新提交
if [ -d "wushizhifu-full" ]; then
  echo "=== wushizhifu-full 最新提交 ==="
  cd wushizhifu-full
  git log --oneline -1 2>/dev/null || echo "不是 Git 仓库"
  cd ..
fi

if [ -d "repo/wushizhifu-full" ]; then
  echo "=== repo/wushizhifu-full 最新提交 ==="
  cd repo/wushizhifu-full
  git log --oneline -1 2>/dev/null || echo "不是 Git 仓库"
  cd ../..
fi

# 4. 检查部署目录中的文件时间
echo "=== 部署目录文件时间 ==="
if [ -f "frontend/dist/index.html" ]; then
  stat frontend/dist/index.html | grep Modify
fi

# 5. 检查构建目录中的文件时间
echo "=== 构建目录文件时间 ==="
if [ -d "wushizhifu-full/dist" ] && [ -f "wushizhifu-full/dist/index.html" ]; then
  stat wushizhifu-full/dist/index.html | grep Modify
fi

if [ -d "repo/wushizhifu-full/dist" ] && [ -f "repo/wushizhifu-full/dist/index.html" ]; then
  stat repo/wushizhifu-full/dist/index.html | grep Modify
fi

# 6. 检查代码内容
echo "=== 检查代码内容 ==="
echo "wushizhifu-full 中是否有 openAccount:"
grep -r "openAccount" wushizhifu-full/src wushizhifu-full/components 2>/dev/null | head -3

if [ -d "repo/wushizhifu-full" ]; then
  echo "repo/wushizhifu-full 中是否有 openAccount:"
  grep -r "openAccount" repo/wushizhifu-full/src repo/wushizhifu-full/components 2>/dev/null | head -3
fi

echo "部署目录中是否有 openAccount:"
grep -r "openAccount" frontend/dist/assets/*.js 2>/dev/null | head -3
```

### 修复步骤（根据诊断结果）

1. **如果 `repo/wushizhifu-full` 是旧代码**：
   ```bash
   # 备份后删除
   mv /home/ubuntu/wushizhifu/repo/wushizhifu-full /home/ubuntu/wushizhifu/repo/wushizhifu-full.backup.$(date +%Y%m%d)
   ```

2. **统一使用 `wushizhifu-full` 目录**：
   - 修改 GitHub Actions 工作流，移除 `repo/wushizhifu-full` 的检查
   - 确保 Git pull 正确更新该目录

3. **清理并重新构建**：
   ```bash
   cd /home/ubuntu/wushizhifu/wushizhifu-full
   rm -rf node_modules dist .vite .cache
   npm install
   npm run build
   ```

4. **完全清理部署目录**：
   ```bash
   sudo rm -rf /home/ubuntu/wushizhifu/frontend/dist/*
   sudo cp -r /home/ubuntu/wushizhifu/wushizhifu-full/dist/* /home/ubuntu/wushizhifu/frontend/dist/
   sudo chown -R www-data:www-data /home/ubuntu/wushizhifu/frontend/dist
   ```

5. **验证 Nginx 配置**：
   ```bash
   sudo nginx -t
   sudo systemctl reload nginx
   ```

## 预防措施

1. **统一目录结构**：只保留一个前端源代码目录
2. **添加构建验证**：在部署前检查构建产物是否包含最新代码
3. **添加部署验证**：部署后检查部署目录中的文件
4. **清理旧目录**：定期清理服务器上的旧目录和备份
5. **使用 Git 子模块或单一仓库**：避免多个目录的混乱

## 总结

最可能的原因是：**服务器上存在 `repo/wushizhifu-full` 旧代码目录，GitHub Actions 工作流优先使用了这个旧目录进行构建，导致部署的始终是旧代码**。

修复方法：**删除或重命名 `repo/wushizhifu-full` 目录，确保工作流只使用 `wushizhifu-full` 目录，并在构建前确保代码是最新的**。

