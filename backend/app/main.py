"""
OS Security Scanner - FastAPI main application
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

# Import API routers
from app.api import scan, upload, chat, alerts, health
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management"""
    # Startup
    print(f"Starting {settings.app_name} v{settings.app_version}")
    
    # Ensure the upload directory exists
    os.makedirs(settings.upload_dir, exist_ok=True)
    
    yield
    
    # Shutdown
    print("Application shutdown")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="Linux system security monitoring and threat analysis system",
    version=settings.app_version,
    lifespan=lifespan,
)


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include API routers
app.include_router(scan.router)
app.include_router(upload.router)
app.include_router(chat.router)
app.include_router(alerts.router)
app.include_router(health.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "status": "running",
    }


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """HTTP exception handler"""
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
