import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from app.models.schemas import LLMConfig, LLMProvider, LLMResponse
from app.utils.logger import get_logger

logger = get_logger(__name__)


class LLMProviderBase(ABC):
    """Abstract base class for LLM providers"""

    def __init__(self, config: LLMConfig):
        self.config = config
        self.client = None

    @abstractmethod
    async def generate_response(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate response from LLM"""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is available"""
        pass

    @abstractmethod
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for this provider"""
        pass

    def validate_config(self) -> bool:
        """Validate provider configuration"""
        return bool(self.config.api_key and self.config.model)

    def get_provider_info(self) -> Dict[str, Any]:
        """Get provider information"""
        return {
            "provider": self.config.provider.value,
            "model": self.config.model,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "available": self.is_available()
        }
