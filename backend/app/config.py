import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration settings"""
    # Ollama configuration
    ollama_url: str = os.getenv("OLLAMA_URL", "http://localhost:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3:8b")
    ollama_timeout: int = 300
    
    # Application configuration
    app_name: str = "OS Security Scanner"
    app_version: str = "1.1.0"
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Log configuration
    log_dir: str = os.getenv("LOG_DIR", "/var/log")
    
    # JWT configuration
    jwt_secret: str = os.getenv("JWT_SECRET", "change-this-secret-key")
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    
    # File upload configuration
    max_upload_size: int = 50 * 1024 * 1024  # 50 MB
    allowed_extensions: list = ["log", "txt"]
    upload_dir: str = "/tmp/os_antivirus_uploads"
    
    # LLM configuration
    llm_temperature: float = 0.3
    llm_top_p: float = 0.9
    llm_max_tokens: int = 2048
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
