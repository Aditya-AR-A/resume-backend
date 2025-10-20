import asyncio
import time
from typing import Any, Dict

from app.models.schemas import LLMConfig, LLMProvider, LLMResponse
from app.utils.logger import get_logger

from .base import LLMProviderBase

logger = get_logger(__name__)


class AnthropicProvider(LLMProviderBase):
    """Anthropic LLM provider implementation"""

    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.client = None
        if self.validate_config():
            try:
                import anthropic
                self.client = anthropic.Anthropic(api_key=self.config.api_key)
                logger.info(f"Anthropic provider initialized with model: {self.config.model}")
            except ImportError:
                logger.warning("Anthropic package not installed")
            except Exception as e:
                logger.error(f"Failed to initialize Anthropic client: {e}")

    async def generate_response(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate response using Anthropic"""
        if not self.is_available():
            raise Exception("Anthropic client not initialized or API key missing")

        start_time = time.time()

        try:
            # Get parameters from kwargs or use defaults
            temperature = kwargs.get('temperature', self.config.temperature)
            max_tokens = kwargs.get('max_tokens', self.config.max_tokens)

            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.messages.create(
                    model=self.config.model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    messages=[{"role": "user", "content": prompt}]
                )
            )

            content = response.content[0].text
            processing_time = time.time() - start_time

            return LLMResponse(
                response=content,
                provider=LLMProvider.ANTHROPIC,
                model=self.config.model,
                confidence=0.88,
                processing_time=processing_time,
                tokens_used=response.usage.input_tokens + response.usage.output_tokens
            )

        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise

    def is_available(self) -> bool:
        """Check if Anthropic is available"""
        return (self.client is not None and
                bool(self.config.api_key) and
                bool(self.config.model))

    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for Anthropic"""
        return {
            "model": "claude-3-sonnet-20240229",  # Default Anthropic model
            "temperature": 0.7,
            "max_tokens": 1024,
            "api_key_required": True
        }
