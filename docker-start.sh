#!/bin/bash

# 使用 docker-compose 快速啟動

echo "╔════════════════════════════════════════╗"
echo "║   OS 掃毒系統 - Docker 快速啟動       ║"
echo "╚════════════════════════════════════════╝"
echo ""

# 檢查 Docker
if ! command -v docker &> /dev/null; then
    echo "✗ Docker 未安裝"
    exit 1
fi

# 檢查 Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "✗ Docker Compose 未安裝"
    exit 1
fi

echo "✓ Docker 環境檢查通過"
echo ""

# 啟動服務
echo "啟動服務..."
docker-compose up -d

# 等待服務啟動
echo ""
echo "等待服務啟動..."
sleep 10

# 檢查服務狀態
echo ""
echo "檢查服務狀態..."
docker-compose ps

echo ""
echo "╔════════════════════════════════════════╗"
echo "║           啟動完成！               ║"
echo "╚════════════════════════════════════════╝"
echo ""
echo "✅ 訪問地址："
echo "   - 前端應用: http://localhost"
echo "   - 後端 API: http://localhost/api"
echo "   - API 文檔: http://localhost/api/docs"
echo ""
echo "📋 查看日誌："
echo "   docker-compose logs -f backend"
echo "   docker-compose logs -f frontend"
echo ""
echo "🛑 停止服務："
echo "   docker-compose down"
echo ""
