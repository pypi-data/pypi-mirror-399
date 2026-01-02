from typing import Optional
from openai import OpenAI
from .base import BaseAIProvider
from .prompts import ERROR_EXPLANATION_PROMPT

class OpenAIProvider(BaseAIProvider):
    def __init__(self, api_key, config):
        super().__init__(api_key)
        self.model = config.get('ai_model', 'gpt-3.5-turbo')
        self.client = OpenAI(api_key=api_key) if api_key else None

    def explain_error(self, error_text: str, language: str) -> Optional[str]:
        if not self.client:
            return "OpenAI not available"

        prompt = ERROR_EXPLANATION_PROMPT.format(error=error_text, language=language)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                temperature=0.2,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"OpenAI error: {str(e)}"