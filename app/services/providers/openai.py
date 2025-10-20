import asyncio
import time
from typing import Any, Dict

from app.models.schemas import LLMConfig, LLMProvider, LLMResponse
from app.utils.logger import get_logger

from .base import LLMProviderBase

logger = get_logger(__name__)


class OpenAIProvider(LLMProviderBase):
    """OpenAI LLM provider implementation"""

    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.client = None
        if self.validate_config():
            try:
                import openai
                self.client = openai.OpenAI(api_key=self.config.api_key)
                logger.info(f"OpenAI provider initialized with model: {self.config.model}")
            except ImportError:
                logger.warning("OpenAI package not installed")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")

    async def generate_response(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate response using OpenAI"""
        if not self.is_available():
            raise Exception("OpenAI client not initialized or API key missing")

        start_time = time.time()

        try:
            # Get parameters from kwargs or use defaults
            temperature = kwargs.get('temperature', self.config.temperature)
            max_tokens = kwargs.get('max_tokens', self.config.max_tokens)

            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.chat.completions.create(
                    model=self.config.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
            )

            content = response.choices[0].message.content
            processing_time = time.time() - start_time

            return LLMResponse(
                response=content,
                provider=LLMProvider.OPENAI,
                model=self.config.model,
                confidence=0.85,
                processing_time=processing_time,
                tokens_used=response.usage.total_tokens if response.usage else None
            )

        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise

    def is_available(self) -> bool:
        """Check if OpenAI is available"""
        return (self.client is not None and
                bool(self.config.api_key) and
                bool(self.config.model))

    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for OpenAI"""
        return {
            "model": "gpt-3.5-turbo",  # Default OpenAI model
            "temperature": 0.7,
            "max_tokens": 1024,
            "api_key_required": True
        }
