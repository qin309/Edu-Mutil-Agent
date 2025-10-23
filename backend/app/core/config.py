"""
Configuration settings for the EduAgent application
"""
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import validator


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """
    # Project settings
    PROJECT_NAME: str = "EduAgent"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Multi-modal educational agent platform"

    # API settings
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "changethis"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days

    # CORS settings
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",  # Vue dev server
        "http://localhost:3001",  # Vue dev server (configured port)
        "http://localhost:8080",  # Alternative Vue dev port
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:8080",
    ]

    # Database settings
    DATABASE_URL: str = "sqlite+aiosqlite:///./eduagent.db"

    # OpenRouter settings
    OPENROUTER_API_KEY: str = "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"  # Default API key provided
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    DEFAULT_MODEL: str = "deepseek-ai/DeepSeek-V3.1-Terminus"  # Updated to DeepSeek-V3.1-Terminus

    # SiliconFlow settings
    SILICONFLOW_API_KEY: Optional[str] = None  # SiliconFlow API key for embeddings and LLM

    # File upload settings
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(
        cls, v
    ) -> List[str]:
        if isinstance(v, str):
            # Try to parse as JSON first
            import json
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
            except json.JSONDecodeError:
                pass
            # Fallback to comma-separated
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        raise ValueError(v)

    @validator("DATABASE_URL", pre=True)
    def assemble_db_connection(cls, v: str) -> str:
        if v.startswith("sqlite"):
            return v
        return v

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()