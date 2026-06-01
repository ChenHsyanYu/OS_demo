"""
OS 掃毒系統 - FastAPI 主應用
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

# 導入 API 路由
from app.api import scan, upload, chat, alerts, health
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """應用生命周期管理"""
    # 啟動
    print(f"啟動 {settings.app_name} v{settings.app_version}")
    
    # 確保上傳目錄存在
    os.makedirs(settings.upload_dir, exist_ok=True)
    
    yield
    
    # 關閉
    print("應用關閉")


# 建立 FastAPI 應用
app = FastAPI(
    title=settings.app_name,
    description="Linux 系統安全監控與威脅分析系統",
    version=settings.app_version,
    lifespan=lifespan,
)


# CORS 中間件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 包含 API 路由
app.include_router(scan.router)
app.include_router(upload.router)
app.include_router(chat.router)
app.include_router(alerts.router)
app.include_router(health.router)


@app.get("/")
async def root():
    """根端點"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "status": "running",
    }


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """HTTP 異常處理"""
    return {
        "error": exc.detail,
        "status_code": exc.status_code,
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info",
    )
