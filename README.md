# OS 掃毒系統 - 工程規格書實現

完整的 Linux 安全監控與威脅分析系統

## 📋 系統架構

```
┌─────────────┐
│  React UI   │ ← 前端展示層
└──────┬──────┘
       │ HTTP/REST
┌──────▼──────────────────┐
│  FastAPI 後端服務       │ ← 應用層
├──────────────────────────┤
│ ┌────────────────────┐  │
│ │ Log Parser         │  │
│ │ - syslog           │  │
│ │ - journald         │  │
│ │ - auditd           │  │
│ └────────────────────┘  │
│ ┌────────────────────┐  │
│ │ Event Correlator   │  │
│ │ 時間軸排序         │  │
│ └────────────────────┘  │
│ ┌────────────────────┐  │
│ │ Ollama LLM         │  │ ← LLM 推論層
│ │ LLaMA 3 8B         │  │
│ └────────────────────┘  │
└──────────────────────────┘
```

## 🚀 快速開始

### 後端

```bash
# 1. 進入後端目錄
cd backend

# 2. 安裝依賴
pip install -r requirements.txt

# 3. 配置環境
cp .env.example .env

# 4. 啟動服務
python main.py
```

後端將在 http://localhost:8000 運行

### 前端

```bash
# 1. 進入前端目錄
cd frontend

# 2. 安裝依賴
npm install

# 3. 啟動開發服務器
npm start
```

前端將在 http://localhost:3000 運行

### Ollama 服務

```bash
# 1. 確保 Ollama 已安裝
# https://ollama.ai

# 2. 下載模型
ollama pull llama3:8b

# 3. 啟動服務
ollama serve

> 如果使用 Docker Compose，Ollama 服務會在啟動時自動檢查並下載 `llama3:8b` 模型。
```

Ollama 將在 http://localhost:11434 運行

## 📦 項目結構

```
OS_demo/
├── backend/                    # Python FastAPI 後端
│   ├── app/
│   │   ├── core/              # 核心服務（安全、配置）
│   │   ├── modules/           # 業務模組
│   │   │   ├── log_parser.py  # 日誌解析
│   │   │   └── ollama_client.py # LLM 客戶端
│   │   ├── api/               # API 路由
│   │   │   ├── scan.py        # 掃描端點
│   │   │   ├── upload.py      # 上傳端點
│   │   │   ├── chat.py        # 對話端點
│   │   │   ├── alerts.py      # 警報端點
│   │   │   └── health.py      # 健康檢查
│   │   ├── utils/             # 工具函數
│   │   ├── config.py          # 配置
│   │   ├── models.py          # 數據模型
│   │   └── main.py            # FastAPI 應用
│   ├── requirements.txt       # Python 依賴
│   ├── .env.example          # 環境配置示例
│   ├── README.md             # 後端文檔
│   └── main.py               # 啟動指令碼
│
└── frontend/                   # React 前端
    ├── src/
    │   ├── components/        # 可複用組件
    │   │   └── Layout.tsx     # 主佈局
    │   ├── pages/             # 頁面組件
    │   │   ├── Dashboard.tsx  # 儀表板
    │   │   ├── Alerts.tsx     # 警訊中心
    │   │   ├── Upload.tsx     # 上傳
    │   │   └── Chat.tsx       # 對話
    │   ├── services/
    │   │   └── api.ts         # API 客戶端
    │   ├── types/
    │   │   └── index.ts       # TypeScript 類型
    │   ├── utils/
    │   │   └── helpers.ts     # 工具函數
    │   ├── App.tsx            # 主應用
    │   └── index.tsx          # 入口
    ├── public/
    │   └── index.html         # HTML 模板
    ├── package.json           # Node 依賴
    ├── tsconfig.json         # TypeScript 配置
    ├── README.md             # 前端文檔
    └── .env.example          # 環境配置示例
```

## 🛠 技術棧

### 後端
- **框架**: FastAPI 0.104.1
- **伺服器**: Uvicorn
- **LLM**: Ollama + LLaMA 7B
- **認證**: JWT + bcrypt

### 前端
- **框架**: React 18
- **語言**: TypeScript 5
- **UI**: Ant Design 5
- **可視化**: Recharts
- **路由**: React Router 6
- **HTTP**: Axios

## 📊 核心功能

### 1. Log 掃描與事件排序
- 支援多種 Linux 日誌格式
- 實時事件檢測
- 時間軸排序與關聯分析

### 2. LLM 風險評估
- MITRE ATT&CK 分類
- CVE 編號關聯
- 自然語言分析與建議

### 3. UI 功能
- 📊 警訊儀表板
- 📋 漏洞詳情頁
- 📤 Log 上傳
- 💬 LLM 對話介面

## 🔒 安全性

- 所有日誌本地處理
- Ollama 僅綁定 localhost
- JWT Token 認證
- 檔案上傳驗證（副檔名、Magic Number、大小）
- 自動刪除敏感數據

## 📈 性能目標

| 指標 | 目標 |
|-----|-----|
| Log 掃描（1GB） | ≤ 60 秒 |
| LLM 首 Token | ≤ 5 秒 |
| 完整分析 | ≤ 30 秒 |
| UI 載入 | ≤ 3 秒 |

## ⚙️ 系統需求

### 最低配置
- OS: Ubuntu 20.04+
- CPU: 4 核心
- RAM: 8 GB
- 磁碟: 15 GB

### 推薦配置
- OS: Ubuntu 22.04 LTS
- CPU: 8 核心+
- RAM: 16 GB
- 磁碟: 50 GB SSD
- GPU: NVIDIA 8GB（可選，加速）

## 🔧 環境變數

### 後端 (.env)
```env
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3:8b
JWT_SECRET=your-secret-key-change-this
DEBUG=False
LOG_DIR=/var/log
```

### 前端 (.env)
```env
REACT_APP_API_URL=http://localhost:8000
```

## 📝 API 文檔

完整的 API 文檔可在以下位置訪問：
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🐛 故障排除

### 後端連線失敗
```bash
# 檢查 Ollama 狀態
curl http://localhost:11434/api/tags

# 查看後端日誌
python main.py
```

### 日誌讀取權限
```bash
# 加入 adm 組
sudo usermod -aG adm $USER
newgrp adm
```

### 模型不存在
```bash
# 下載 LLaMA 7B
ollama pull llama3:8b
```

## 📚 相關文檔

- [後端開發文檔](backend/README.md)
- [前端開發文檔](frontend/README.md)
- [工程規格書](OS掃毒系統_工程規格書_v1.1.docx)

## 📄 授權

內部使用

---

**版本**: 1.1.0  
**最後更新**: 2026-06-01
