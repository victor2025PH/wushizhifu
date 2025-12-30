#!/bin/bash
# 清理旧的前端源代码目录脚本
# 按照方案A：删除 repo/wushizhifu-full 目录（如果存在）

set -e

echo "=========================================="
echo "🧹 清理旧的前端源代码目录"
echo "=========================================="
echo ""

PROJECT_ROOT="/home/ubuntu/wushizhifu"
OLD_DIR="$PROJECT_ROOT/repo/wushizhifu-full"
NEW_DIR="$PROJECT_ROOT/wushizhifu-full"

# 检查新目录是否存在
if [ ! -d "$NEW_DIR" ]; then
  echo "❌ 错误: 新的源代码目录不存在: $NEW_DIR"
  echo "   请确保 wushizhifu-full 目录存在"
  exit 1
fi

echo "✅ 新的源代码目录存在: $NEW_DIR"

# 检查旧目录是否存在
if [ -d "$OLD_DIR" ]; then
  echo ""
  echo "⚠️  发现旧的前端源代码目录: $OLD_DIR"
  
  # 显示旧目录信息
  echo "旧目录信息:"
  ls -lh "$OLD_DIR" | head -10
  
  # 确认是否删除
  echo ""
  echo "准备备份并删除旧目录..."
  BACKUP_DIR="${OLD_DIR}.backup.$(date +%Y%m%d_%H%M%S)"
  
  # 备份旧目录
  echo "📦 备份旧目录到: $BACKUP_DIR"
  mv "$OLD_DIR" "$BACKUP_DIR" || {
    echo "❌ 备份失败，使用 sudo 重试..."
    sudo mv "$OLD_DIR" "$BACKUP_DIR"
  }
  
  echo "✅ 旧目录已备份并删除"
  echo "   备份位置: $BACKUP_DIR"
  echo "   如需恢复，可以执行: mv $BACKUP_DIR $OLD_DIR"
else
  echo "✅ 旧目录不存在，无需清理: $OLD_DIR"
fi

echo ""
echo "=========================================="
echo "✅ 清理完成"
echo "=========================================="
echo ""
echo "📋 当前状态:"
echo "  ✅ 新的源代码目录: $NEW_DIR"
if [ -d "$BACKUP_DIR" ]; then
  echo "  📦 旧目录备份: $BACKUP_DIR"
fi
echo ""
echo "下一步: 执行 GitHub Actions 部署或手动构建部署"

