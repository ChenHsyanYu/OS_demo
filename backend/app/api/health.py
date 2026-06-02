"""
API routes - health check
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
    Service health check.
    
    Checks backend and Ollama status.
    """
    ollama_status = "healthy" if ollama_client.health_check() else "unhealthy"
    
    return HealthCheck(
        status="healthy",
        ollama_status=ollama_status,
        version=settings.app_version,
    )
