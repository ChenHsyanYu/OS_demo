# OS 掃毒系統

完整的 Linux 安全監控與威脅分析系統

## 系統架構

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
│ │ - auditd           │  │
│ │ - journald         │  │
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

## 快速開始

### 後端

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
python main.py
```

後端將在 http://localhost:8000 運行

### 前端

```bash
cd frontend
npm install
npm start
```

前端將在 http://localhost:3000 運行

### Ollama

```bash
# 安裝 Ollama：https://ollama.ai
ollama pull llama3:8b
ollama serve
```

Ollama 將在 http://localhost:11434 運行

### Docker Compose（一鍵啟動）

```bash
docker compose up -d
```

自動啟動所有服務（Ollama、後端、前端、Nginx），第一次執行需下載模型約 4.7 GB。

## 前端功能

### 儀表板 `/`
- 危機 / 高危 / 中危警訊數量統計
- 風險級別圓餅圖、風險評分時間軸
- 最近警訊列表
- 「掃描系統」按鈕：掃描本機 `/var/log` 並更新警訊

### 日誌上傳 `/upload`
- 拖拉或點擊上傳 `.log` / `.txt` 檔案（最大 50 MB）
- 自動偵測格式（syslog / auditd）並解析
- 顯示解析到的事件列表（類型、嚴重程度、時間、描述）

### 警訊中心 `/alerts`
- 列出所有警報，可依嚴重程度篩選
- 點「詳情」查看相關原始事件與 LLM 分析
- 可刪除警報

### 智能對話 `/chat`
- 與本地 LLM（llama3:8b）對話，詢問安全分析建議
- 串流回應，支援 Markdown 格式顯示
- Enter 送出、Shift+Enter 換行，支援中文輸入法
- 等待回應時顯示「LLM 推理中...」提示

## 偵測的威脅類型

| 類型 | 說明 |
|------|------|
| `privilege_escalation` | 權限提升，含 sudo、su、pkexec |
| `anomalous_login` | 異常登入，SSH 密碼失敗、無效使用者 |
| `network_anomaly` | 網路異常，連接埠掃描、異常 DNS |
| `suspicious_execution` | 可疑程式執行 |
| `file_tampering` | 系統檔案竄改 |
| `rootkit_signature` | Rootkit 特徵 |

### auditd 格式特別支援

上傳 `ausearch` 輸出的 auditd 日誌可偵測：

| 特徵 | 偵測依據 |
|------|---------|
| CVE-2021-4034 (PwnKit) | `EXECVE argc=0` + cwd 含 CVE 路徑 |
| 提權成功 | `key=priv_change` + uid/gid 變為 0 |
| 可疑 exploit 執行 | proctitle 含 `./exploit` |

## 技術棧

### 後端
- **框架**: FastAPI 0.104.1 + Uvicorn
- **LLM**: Ollama + LLaMA 3 8B（本地推論，非同步串流）
- **日誌解析**: 自製 syslog / auditd parser

### 前端
- **框架**: React 18 + TypeScript 5
- **UI**: Ant Design 5
- **圖表**: Recharts
- **路由**: React Router 6
- **HTTP**: Axios + Fetch（串流）

## 環境變數

### 後端 `.env`
```env
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3:8b
JWT_SECRET=your-secret-key-change-this
DEBUG=False
LOG_DIR=/var/log
```

### 前端 `.env`
```env
REACT_APP_API_URL=http://localhost:8000
```

## API 文檔

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 系統需求

| | 最低 | 推薦 |
|---|---|---|
| OS | Ubuntu 20.04+ | Ubuntu 22.04 LTS |
| CPU | 4 核心 | 8 核心+ |
| RAM | 8 GB | 16 GB |
| 磁碟 | 15 GB | 50 GB SSD |
| GPU | — | NVIDIA 8 GB（加速推論） |

## 故障排除

**後端連線失敗**
```bash
curl http://localhost:11434/api/tags   # 確認 Ollama 狀態
python main.py                          # 查看後端 log
```

**日誌讀取權限不足**
```bash
sudo usermod -aG adm $USER
newgrp adm
```

**模型不存在**
```bash
ollama pull llama3:8b
```

---

**版本**: 1.2.0
**最後更新**: 2026-06-01
