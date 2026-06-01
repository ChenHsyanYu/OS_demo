#!/bin/bash

# OS 掃毒系統 - 完整安裝和啟動指令碼

set -e

echo "╔════════════════════════════════════════╗"
echo "║   OS 掃毒系統 - 安裝和啟動             ║"
echo "╚════════════════════════════════════════╝"
echo ""

# 檢查 Python
echo "✓ 檢查 Python..."
if ! command -v python3 &> /dev/null; then
    echo "✗ Python 3 未安裝。請先安裝 Python 3.10+"
    exit 1
fi
python3 --version

# 檢查 Node.js
echo ""
echo "✓ 檢查 Node.js..."
if ! command -v node &> /dev/null; then
    echo "✗ Node.js 未安裝。請先安裝 Node.js 18+"
    exit 1
fi
node --version

# 檢查 Ollama
echo ""
echo "✓ 檢查 Ollama..."
if ! command -v ollama &> /dev/null; then
    echo "⚠ Ollama 未安裝。請先安裝: https://ollama.ai"
    echo "  安裝後運行: ollama pull llama3:8b"
else
    echo "  Ollama 已安裝"
fi

# 安裝後端依賴
echo ""
echo "✓ 安裝後端依賴..."
cd backend
pip install -r requirements.txt
cd ..

# 安裝前端依賴
echo ""
echo "✓ 安裝前端依賴..."
cd frontend
npm install
cd ..

# 創建環境文件
echo ""
echo "✓ 創建環境配置..."
if [ ! -f backend/.env ]; then
    cp backend/.env.example backend/.env
    echo "  已創建 backend/.env"
fi

if [ ! -f frontend/.env.local ]; then
    cp frontend/.env.example frontend/.env.local
    echo "  已創建 frontend/.env.local"
fi

echo ""
echo "╔════════════════════════════════════════╗"
echo "║         安裝完成！開始運行             ║"
echo "╚════════════════════════════════════════╝"
echo ""
echo "📋 需要在不同的終端窗口中運行："
echo ""
echo "1️⃣  啟動 Ollama（如果未運行）:"
echo "    ollama serve"
echo ""
echo "2️⃣  啟動後端:"
echo "    cd backend && python main.py"
echo ""
echo "3️⃣  啟動前端:"
echo "    cd frontend && npm start"
echo ""
echo "✅ 完成後訪問："
echo "   - 前端: http://localhost:3000"
echo "   - 後端 API: http://localhost:8000"
echo "   - API 文檔: http://localhost:8000/docs"
echo ""
