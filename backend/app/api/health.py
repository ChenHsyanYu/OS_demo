"""
API 路由 - 健康檢查
"""

from fastapi import APIRouter
from app.models import HealthCheck
from app.modules.ollama_client import OllamaClient
from app.config import settings

router = APIRouter(tags=["health"])

ollama_client = OllamaClient()


@router.get("/api/health")
async def health_check() -> HealthCheck:
    """
    服務健康檢查
    
    檢查後端和 Ollama 的狀態
    """
    ollama_status = "healthy" if ollama_client.health_check() else "unhealthy"
    
    return HealthCheck(
        status="healthy",
        ollama_status=ollama_status,
        version=settings.app_version,
    )
