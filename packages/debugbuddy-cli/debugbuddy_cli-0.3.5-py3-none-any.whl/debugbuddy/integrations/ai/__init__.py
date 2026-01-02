from typing import Dict, Optional, Any
from .base import BaseAIProvider
from .openai import OpenAIProvider
from .anthropic import AnthropicProvider
from .prompts import ERROR_EXPLANATION_PROMPT

def get_provider(provider_name: str, config: Dict[str, Any]) -> Optional[BaseAIProvider]:
    if provider_name == "openai":
        return OpenAIProvider(config.get("openai_api_key"), config)
    elif provider_name == "anthropic":
        return AnthropicProvider(config.get("anthropic_api_key"), config)
    return None

def get_explanation_prompt(error: str, language: str) -> str:
    return ERROR_EXPLANATION_PROMPT.format(error=error, language=language)