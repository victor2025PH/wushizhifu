#!/bin/bash
# 检查前端构建输出

echo "=========================================="
echo "🔍 检查前端构建输出"
echo "=========================================="
echo ""

DIST_DIR="/home/ubuntu/wushizhifu/frontend/dist"

echo "📁 构建输出目录: $DIST_DIR"
echo ""

if [ ! -d "$DIST_DIR" ]; then
    echo "❌ dist 目录不存在"
    exit 1
fi

echo "📋 目录内容:"
ls -la "$DIST_DIR"
echo ""

echo "📋 文件列表（详细）:"
find "$DIST_DIR" -type f -exec ls -lh {} \;
echo ""

echo "📄 index.html 内容（前50行）:"
head -50 "$DIST_DIR/index.html"
echo ""

echo "🔍 检查 JavaScript/CSS 文件:"
find "$DIST_DIR" -name "*.js" -o -name "*.css" | head -10
echo ""

echo "📊 文件大小统计:"
du -sh "$DIST_DIR"/*
echo ""

echo "✅ 检查完成"

