from pydantic_settings import BaseSettings
from pathlib import Path
from typing import Dict, Optional
from app.models.schemas import (
    AppConfig, DatabaseConfig, CacheConfig, AIConfig, LLMConfig, LLMProvider, Settings
)


class AppSettings(BaseSettings):
    """Application settings with new structured configuration"""

    # Application Configuration
    app_name: str = "Resume Backend API"
    app_version: str = "1.0.0"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False

    # Database Configuration
    database_url: str = "sqlite:///./resume.db"

    # Cache Configuration
    cache_enabled: bool = True
    cache_ttl: int = 3600
    cache_max_size: int = 1000

    # Data Directory
    data_dir: Path = Path(__file__).parent.parent.parent / "data"

    # CORS
    cors_origins: list = ["*"]

    # Logging
    log_level: str = "INFO"
    log_file: str = "app.log"

    # Security
    secret_key: str = "your-secret-key-here"

    # AI Provider API Keys
    groq_api_key: str = ""
    openai_api_key: str = ""
    anthropic_api_key: str = ""

    # AI Configuration
    primary_llm_provider: LLMProvider = LLMProvider.GROQ
    ai_cache_enabled: bool = True
    ai_cache_ttl: int = 3600
    ai_max_retries: int = 3
    ai_timeout: int = 30

    # Groq Configuration
    groq_model: str = "llama3-8b-8192"
    groq_temperature: float = 0.7
    groq_max_tokens: int = 1000

    # OpenAI Configuration
    openai_model: str = "gpt-3.5-turbo"
    openai_temperature: float = 0.7
    openai_max_tokens: int = 1000

    # Anthropic Configuration
    anthropic_model: str = "claude-3-sonnet-20240229"
    anthropic_temperature: float = 0.7
    anthropic_max_tokens: int = 1000

    class Config:
        env_file = [".env", ".env.local"]
        case_sensitive = False
        extra = "ignore"  # Allow extra fields from env files

    def get_app_config(self) -> AppConfig:
        """Get application configuration"""
        return AppConfig(
            name=self.app_name,
            version=self.app_version,
            debug=self.debug,
            host=self.host,
            port=self.port
        )

    def get_database_config(self) -> DatabaseConfig:
        """Get database configuration"""
        return DatabaseConfig(
            url=self.database_url
        )

    def get_cache_config(self) -> CacheConfig:
        """Get cache configuration"""
        return CacheConfig(
            enabled=self.cache_enabled,
            ttl=self.cache_ttl,
            max_size=self.cache_max_size
        )

    def get_ai_config(self) -> AIConfig:
        """Get AI configuration with provider settings"""
        providers = {}

        # Configure Groq provider
        if self.groq_api_key:
            providers[LLMProvider.GROQ] = LLMConfig(
                provider=LLMProvider.GROQ,
                api_key=self.groq_api_key,
                model=self.groq_model,
                temperature=self.groq_temperature,
                max_tokens=self.groq_max_tokens
            )

        # Configure OpenAI provider
        if self.openai_api_key:
            providers[LLMProvider.OPENAI] = LLMConfig(
                provider=LLMProvider.OPENAI,
                api_key=self.openai_api_key,
                model=self.openai_model,
                temperature=self.openai_temperature,
                max_tokens=self.openai_max_tokens
            )

        # Configure Anthropic provider
        if self.anthropic_api_key:
            providers[LLMProvider.ANTHROPIC] = LLMConfig(
                provider=LLMProvider.ANTHROPIC,
                api_key=self.anthropic_api_key,
                model=self.anthropic_model,
                temperature=self.anthropic_temperature,
                max_tokens=self.anthropic_max_tokens
            )

        return AIConfig(
            primary_provider=self.primary_llm_provider,
            providers=providers,
            enable_caching=self.ai_cache_enabled,
            cache_ttl=self.ai_cache_ttl,
            max_retries=self.ai_max_retries,
            timeout=self.ai_timeout
        )

    def get_structured_settings(self) -> Settings:
        """Get structured settings object"""
        return Settings(
            app=self.get_app_config(),
            database=self.get_database_config(),
            cache=self.get_cache_config(),
            ai=self.get_ai_config()
        )


# Create global settings instance
app_settings = AppSettings()

# Create structured settings for use throughout the app
settings = app_settings.get_structured_settings()


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def validate_settings() -> bool:
    """Validate that all required settings are properly configured"""
    errors = []

    # Check if at least one LLM provider is configured
    if not any([
        app_settings.groq_api_key,
        app_settings.openai_api_key,
        app_settings.anthropic_api_key
    ]):
        errors.append("No LLM provider API keys configured")

    # Check data directory exists
    if not app_settings.data_dir.exists():
        errors.append(f"Data directory does not exist: {app_settings.data_dir}")

    if errors:
        print("Configuration errors:")
        for error in errors:
            print(f"  - {error}")
        return False

    return True


def print_settings_summary():
    """Print a summary of current settings"""
    print("=== Application Settings Summary ===")
    print(f"App Name: {app_settings.app_name}")
    print(f"Version: {app_settings.app_version}")
    print(f"Debug Mode: {app_settings.debug}")
    print(f"Host: {app_settings.host}:{app_settings.port}")
    print(f"Data Directory: {app_settings.data_dir}")

    print("\n=== AI Configuration ===")
    print(f"Primary Provider: {app_settings.primary_llm_provider.value}")
    print(f"Cache Enabled: {app_settings.ai_cache_enabled}")

    providers = []
    if app_settings.groq_api_key:
        providers.append("Groq")
    if app_settings.openai_api_key:
        providers.append("OpenAI")
    if app_settings.anthropic_api_key:
        providers.append("Anthropic")

    print(f"Available Providers: {', '.join(providers) if providers else 'None'}")
    print("=" * 40)


# Validate settings on import
if not validate_settings():
    print("Warning: Some settings are not properly configured!")
    print_settings_summary()
