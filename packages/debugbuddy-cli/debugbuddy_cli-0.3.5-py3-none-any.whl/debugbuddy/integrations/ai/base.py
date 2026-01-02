from typing import Optional

class BaseAIProvider:
    
    def __init__(self, api_key: str):
        self.api_key = api_key

    def explain_error(self, error_text: str, language: str) -> Optional[str]:
        raise NotImplementedError("Subclasses must implement explain_error")