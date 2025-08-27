import asyncio
import logging
from typing import Dict, List, Optional, Any
from app.models.schemas import LLMConfig, LLMResponse, LLMProvider
from .base import LLMProviderBase
from .groq import GroqProvider
from .openai import OpenAIProvider
from .anthropic import AnthropicProvider

logger = logging.getLogger(__name__)


class LLMProviderManager:
    """Manages multiple LLM providers with fallback"""

    def __init__(self):
        self.providers: Dict[LLMProvider, LLMProviderBase] = {}
        self.provider_priority: List[LLMProvider] = [
            LLMProvider.GROQ,      # Primary
            LLMProvider.OPENAI,    # Secondary
            LLMProvider.ANTHROPIC  # Tertiary
        ]

    def add_provider(self, config: LLMConfig) -> None:
        """Add a provider configuration"""
        try:
            if config.provider == LLMProvider.GROQ:
                provider = GroqProvider(config)
            elif config.provider == LLMProvider.OPENAI:
                provider = OpenAIProvider(config)
            elif config.provider == LLMProvider.ANTHROPIC:
                provider = AnthropicProvider(config)
            else:
                logger.warning(f"Unknown provider: {config.provider}")
                return

            self.providers[config.provider] = provider
            logger.info(f"Added provider: {config.provider.value}")

        except Exception as e:
            logger.error(f"Failed to add provider {config.provider}: {e}")

    def get_provider(self, provider_type: LLMProvider) -> Optional[LLMProviderBase]:
        """Get a specific provider"""
        return self.providers.get(provider_type)

    def get_available_providers(self) -> List[LLMProvider]:
        """Get list of available providers"""
        available = []
        for provider_type, provider in self.providers.items():
            if provider.is_available():
                available.append(provider_type)
        return available

    async def generate_response(self, prompt: str, preferred_provider: Optional[LLMProvider] = None, **kwargs) -> LLMResponse:
        """Generate response using available providers with fallback"""
        providers_to_try = []

        # If preferred provider is specified and available, try it first
        if preferred_provider and preferred_provider in self.providers:
            if self.providers[preferred_provider].is_available():
                providers_to_try.append(preferred_provider)

        # Add remaining providers in priority order
        for provider_type in self.provider_priority:
            if provider_type not in providers_to_try and provider_type in self.providers:
                if self.providers[provider_type].is_available():
                    providers_to_try.append(provider_type)

        if not providers_to_try:
            raise Exception("No available LLM providers")

        last_error = None

        # Try each provider in order
        for provider_type in providers_to_try:
            try:
                provider = self.providers[provider_type]
                logger.info(f"Attempting to generate response with {provider_type.value}")
                response = await provider.generate_response(prompt, **kwargs)
                logger.info(f"Successfully generated response with {provider_type.value}")
                return response

            except Exception as e:
                logger.warning(f"Provider {provider_type.value} failed: {e}")
                last_error = e
                continue

        # If all providers failed
        raise Exception(f"All LLM providers failed. Last error: {last_error}")

    def get_provider_configs(self) -> Dict[str, Dict[str, Any]]:
        """Get configuration information for all providers"""
        configs = {}
        for provider_type, provider in self.providers.items():
            configs[provider_type.value] = provider.get_provider_info()
        return configs

    def get_default_configs(self) -> Dict[str, Dict[str, Any]]:
        """Get default configurations for all provider types"""
        return {
            LLMProvider.GROQ.value: GroqProvider(LLMConfig(provider=LLMProvider.GROQ)).get_default_config(),
            LLMProvider.OPENAI.value: OpenAIProvider(LLMConfig(provider=LLMProvider.OPENAI)).get_default_config(),
            LLMProvider.ANTHROPIC.value: AnthropicProvider(LLMConfig(provider=LLMProvider.ANTHROPIC)).get_default_config()
        }
