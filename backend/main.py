#!/usr/bin/env python3
"""
OS 掃毒系統 - 後端啟動指令碼
"""

import sys
import os

# 添加當前目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    import uvicorn
    from app.main import app
    from app.config import settings
    
    print(f"""
    ╔════════════════════════════════════════╗
    ║     OS 掃毒系統 v{settings.app_version}              ║
    ║   Linux 安全監控與威脅分析系統      ║
    ╚════════════════════════════════════════╝
    
    啟動服務...
    - API: http://0.0.0.0:8000
    - 文檔: http://0.0.0.0:8000/docs
    - Ollama: {settings.ollama_url}
    """)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info",
    )
