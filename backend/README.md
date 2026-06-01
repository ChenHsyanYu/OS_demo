# OS 掃毒系統 - 後端

Python FastAPI 實現的 Linux 安全監控與威脅分析系統

## 功能

- 📝 日誌掃描與事件排序（支援 syslog、journald、auditd 等）
- 🤖 基於 Ollama LLM 的風險評估
- 🔍 安全事件關聯分析
- 💾 日誌上傳與解析
- 💬 多輪對話介面
- 🔐 JWT 認證與檔案驗證

## 環境要求

- Python 3.10+
- Ollama（或相容的 LLM 服務）
- Linux/Ubuntu 20.04+

## 安裝

```bash
cd backend

# 安裝依賴
pip install -r requirements.txt

# 複製環境配置
cp .env.example .env

# 編輯 .env，配置 Ollama 地址
```

## 啟動

```bash
# 方式 1：使用啟動指令碼
python main.py

# 方式 2：直接使用 uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

API 文檔將在 http://localhost:8000/docs 可用

## API 端點

### 掃描
- `POST /api/scan/log` - 掃描系統日誌

### 上傳
- `POST /api/upload/log` - 上傳日誌檔案

### 警報
- `GET /api/alerts` - 獲取警報列表
- `GET /api/alerts/{id}` - 獲取警報詳情
- `DELETE /api/alerts/{id}` - 刪除警報

### 對話
- `POST /api/chat` - LLM 對話（串流）
- `GET /api/chat/sessions/{id}` - 獲取對話會話

### 健康檢查
- `GET /api/health` - 服務健康檢查

## 配置

編輯 `.env` 檔案：

```env
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3:8b
JWT_SECRET=your-secret-key-change-this
DEBUG=False
LOG_DIR=/var/log
```

## 項目結構

```
backend/
├── app/
│   ├── core/          # 核心模組（安全、設置）
│   ├── modules/       # 業務模組（日誌解析、Ollama 等）
│   ├── api/           # API 路由
│   ├── utils/         # 工具函數
│   ├── config.py      # 配置
│   ├── models.py      # 數據模型
│   └── main.py        # FastAPI 應用
├── requirements.txt   # Python 依賴
└── main.py           # 入口指令碼
```

## 注意事項

1. **Ollama 要求**：確保 Ollama 服務正在運行且模型已下載
   ```bash
   ollama pull llama3:8b
   ```

2. **日誌路徑**：確保後端有權限讀取系統日誌
   ```bash
   sudo usermod -aG adm username
   ```

3. **安全性**：生產環境務必修改 `JWT_SECRET`

## 故障排除

### Ollama 連線失敗
- 檢查 Ollama 是否運行：`curl http://localhost:11434/api/tags`
- 確認 `OLLAMA_URL` 正確

### 權限問題
- 後端需要讀取系統日誌
- Linux：加入 `adm` 組
- 可能需要 sudo 執行

### 模型下載
```bash
# 如果模型不存在
ollama pull llama3:8b
```

## 性能目標

- Log 掃描（1GB）: ≤ 60 秒
- LLM 首 Token: ≤ 5 秒
- 完整分析: ≤ 30 秒
- UI 頁面載入: ≤ 3 秒
