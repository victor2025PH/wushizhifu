# Logo 文件配置說明

## 文件位置

Logo 文件應該放在 `public` 目錄中：

```
frontend/
└── public/
    └── logo_300.png  ← 放在這裡
```

## Vite 處理方式

Vite 會在構建時自動將 `public` 目錄中的所有文件複製到 `dist` 目錄的根目錄。

### 構建前
```
frontend/
├── public/
│   └── logo_300.png
└── src/
```

### 構建後
```
frontend/
├── public/
│   └── logo_300.png
├── dist/
│   ├── logo_300.png    ← 自動複製到這裡
│   ├── index.html
│   └── assets/
└── src/
```

## 在代碼中使用

在組件中使用絕對路徑 `/logo_300.png`：

```tsx
<img src="/logo_300.png" alt="Logo" />
```

構建後，這個路徑會指向 `dist/logo_300.png`。

## 部署步驟

### 在服務器上

1. **確認文件在 public 目錄**：
```bash
ls -lh ~/wushizhifu/frontend/public/logo_300.png
```

2. **重新構建**：
```bash
cd ~/wushizhifu/frontend
sudo chown -R ubuntu:ubuntu dist
npm run build
```

3. **檢查構建結果**：
```bash
ls -lh dist/logo_300.png  # 應該看到文件
```

4. **恢復權限**：
```bash
sudo chown -R www-data:www-data dist
sudo chmod -R 755 dist
sudo systemctl reload nginx
```

## 如果文件不存在

如果構建後 `dist/logo_300.png` 不存在：

1. 確認 `public` 目錄存在：`ls -la public/`
2. 確認文件在 public 目錄：`ls -lh public/logo_300.png`
3. 檢查構建日誌：`npm run build`
4. 檢查 Vite 配置：確認沒有自定義 `publicDir` 配置

