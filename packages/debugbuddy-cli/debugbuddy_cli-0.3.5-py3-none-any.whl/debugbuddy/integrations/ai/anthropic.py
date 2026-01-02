from typing import Optional
from anthropic import Anthropic
from .base import BaseAIProvider
from .prompts import ERROR_EXPLANATION_PROMPT

class AnthropicProvider(BaseAIProvider):
    def __init__(self, api_key, config):
        super().__init__(api_key)
        self.model = config.get('ai_model', 'claude-3-5-sonnet-20241022')
        self.client = Anthropic(api_key=api_key) if api_key else None

    def explain_error(self, error_text: str, language: str) -> Optional[str]:
        if not self.client:
            return "Anthropic not available"

        prompt = ERROR_EXPLANATION_PROMPT.format(error=error_text, language=language)

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                temperature=0.2,
                system="You are a concise debugging assistant. Follow the exact format requested.",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text.strip()
        except Exception as e:
            return f"Anthropic error: {str(e)}"