# Logo 替換說明

## 已完成的工作

1. ✅ 創建了 `Logo.tsx` 組件，支持響應式大小
2. ✅ 更新了 `Dashboard.tsx` 使用 Logo 組件
3. ✅ 更新了 `LoadingScreen.tsx` 使用 Logo 組件
4. ✅ 更新了 `ProfileView.tsx` 使用 Logo 組件

## 需要執行的步驟

### 步驟 1: 在服務器上複製 Logo 文件

```bash
# 確認 logo 文件位置
ls -lh ~/wushizhifu/video/logo_300.png
# 或
ls -lh ~/wushizhifu/vidoe/logo_300.png

# 創建 public 目錄
cd ~/wushizhifu/frontend
mkdir -p public

# 複製 logo（請根據實際路徑調整）
cp ~/wushizhifu/video/logo_300.png public/logo_300.png

# 確認
ls -lh public/logo_300.png
```

### 步驟 2: 重新構建前端

```bash
cd ~/wushizhifu/frontend

# 改變所有權以便構建
sudo chown -R ubuntu:ubuntu dist

# 構建
npm run build

# 檢查 logo 是否在 dist 目錄中
ls -lh dist/logo_300.png

# 恢復權限
sudo chown -R www-data:www-data dist
sudo chmod -R 755 dist

# 重載 Nginx
sudo systemctl reload nginx
```

## Logo 組件特性

- ✅ 響應式大小（sm, md, lg, xl）
- ✅ 自動適應容器大小
- ✅ 保持寬高比
- ✅ 支持自定義 className
- ✅ 自動優化顯示

## 使用位置

1. **Dashboard** - 頂部品牌標識（md 大小）
2. **LoadingScreen** - 加載動畫中心（lg 大小）
3. **ProfileView** - 個人資料頁面（xl 大小）

