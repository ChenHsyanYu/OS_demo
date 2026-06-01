import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """應用配置設置"""
    # Ollama 配置
    ollama_url: str = os.getenv("OLLAMA_URL", "http://localhost:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3:8b")
    ollama_timeout: int = 300
    
    # 應用配置
    app_name: str = "OS 掃毒系統"
    app_version: str = "1.1.0"
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # 日誌配置
    log_dir: str = os.getenv("LOG_DIR", "/var/log")
    
    # JWT 配置
    jwt_secret: str = os.getenv("JWT_SECRET", "change-this-secret-key")
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    
    # 文件上傳配置
    max_upload_size: int = 50 * 1024 * 1024  # 50 MB
    allowed_extensions: list = ["log", "txt"]
    upload_dir: str = "/tmp/os_antivirus_uploads"
    
    # LLM 配置
    llm_temperature: float = 0.3
    llm_top_p: float = 0.9
    llm_max_tokens: int = 2048
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
