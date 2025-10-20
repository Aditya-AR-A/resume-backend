import os
from pathlib import Path
from typing import Dict

import yaml

from app.utils.logger import get_logger

logger = get_logger(__name__)


class PromptManager:
    """Manages prompts loaded from YAML configuration"""

    def __init__(self, prompts_file: str = "prompts.yaml"):
        self.prompts_file = Path(__file__).parent.parent.parent.parent / prompts_file
        self.prompts: Dict[str, str] = {}
        self._load_prompts()

    def _load_prompts(self) -> None:
        """Load prompts from YAML file"""
        try:
            if not self.prompts_file.exists():
                logger.warning(f"Prompts file not found: {self.prompts_file}")
                self._create_default_prompts()
                return

            with open(self.prompts_file, 'r', encoding='utf-8') as file:
                data = yaml.safe_load(file)

            if 'prompts' in data:
                self.prompts = data['prompts']
                logger.info(f"Loaded {len(self.prompts)} prompts from {self.prompts_file}")
            else:
                logger.warning("No 'prompts' section found in YAML file")
                self._create_default_prompts()

        except Exception as e:
            logger.error(f"Failed to load prompts: {e}")
            self._create_default_prompts()

    def _create_default_prompts(self) -> None:
        """Create default prompts if file doesn't exist"""
        self.prompts = {
            "base_context": """
You are an AI assistant for Aditya's portfolio website. You help users with information about:
- Projects and work samples
- Professional experience and career history
- Certificates and educational achievements
- Skills and technologies
- Contact information

Message type: {message_type}
Intent: {intent}
Keywords: {keywords}
Entities: {entities}

User message: {user_message}
""",
            "system_message": """
You are a helpful AI assistant for a software developer's portfolio website.
Provide accurate, concise, and helpful responses about the portfolio content.
""",
            "fallback": "Please provide a helpful, accurate, and concise response."
        }

        # Save default prompts
        try:
            data = {"prompts": self.prompts}
            with open(self.prompts_file, 'w', encoding='utf-8') as file:
                yaml.dump(data, file, default_flow_style=False, allow_unicode=True)
            logger.info(f"Created default prompts file: {self.prompts_file}")
        except Exception as e:
            logger.error(f"Failed to create default prompts file: {e}")

    def get_prompt(self, key: str, **kwargs) -> str:
        """Get a prompt by key and format it with provided variables"""
        if key not in self.prompts:
            logger.warning(f"Prompt key not found: {key}")
            return self.prompts.get("fallback", "Please provide a helpful response.")

        prompt = self.prompts[key]

        try:
            return prompt.format(**kwargs)
        except KeyError as e:
            logger.warning(f"Missing variable in prompt {key}: {e}")
            return prompt
        except Exception as e:
            logger.error(f"Error formatting prompt {key}: {e}")
            return prompt

    def get_base_context(self, **kwargs) -> str:
        """Get the base context prompt"""
        return self.get_prompt("base_context", **kwargs)

    def get_system_message(self) -> str:
        """Get the system message prompt"""
        return self.prompts.get("system_message", "")

    def get_fallback_prompt(self) -> str:
        """Get the fallback prompt"""
        return self.prompts.get("fallback", "Please provide a helpful response.")

    def list_prompts(self) -> Dict[str, str]:
        """List all available prompts"""
        return self.prompts.copy()

    def reload_prompts(self) -> None:
        """Reload prompts from file"""
        self._load_prompts()
