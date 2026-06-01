# OS 掃毒系統 - 前端

React + TypeScript + Ant Design 實現的安全監控儀表板

## 功能

- 📊 實時警訊儀表板
- 📤 日誌上傳與分析
- 🚨 警訊管理中心
- 💬 LLM 智能對話
- 📈 風險評分可視化

## 開始

```bash
cd frontend
npm install
npm start
```

應用將在 http://localhost:3000 運行

> 如果您使用 Docker Compose 啟動整個系統，Ollama 會自動檢查並下載 `llama3:8b` 模型。

## 結構

```
src/
├── components/     # 可複用組件
├── pages/         # 頁面組件
├── services/      # API 服務
├── types/         # TypeScript 類型定義
└── utils/         # 工具函數
```
