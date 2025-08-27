from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    """Application settings"""

    # Application
    app_name: str = "Resume Backend API"
    app_version: str = "1.0.0"
    debug: bool = True

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # CORS
    cors_origins: list = ["*"]  # Configure appropriately for production

    # Data
    data_dir: Path = Path(__file__).parent.parent.parent / "data"

    # AI (Future)
    openai_api_key: str = ""  # Will be set via environment variable

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
