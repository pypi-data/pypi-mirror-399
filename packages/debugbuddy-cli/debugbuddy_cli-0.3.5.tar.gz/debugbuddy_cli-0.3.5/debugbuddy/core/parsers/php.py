import re
from typing import Dict, Optional
from .base import BaseParser

class PHPParser(BaseParser):
    language = 'php'

    PATTERNS = {
        'parse_error': re.compile(r'Parse error: (.+)', re.IGNORECASE),
        'fatal_error': re.compile(r'Fatal error: (.+)', re.IGNORECASE),
        'warning': re.compile(r'Warning: (.+)', re.IGNORECASE),
        'notice': re.compile(r'Notice: (.+)', re.IGNORECASE),
    }

    def parse(self, text: str) -> Optional[Dict]:
        result = {
            "type": "Unknown Error",
            "message": text.strip(),
            "file": None,
            "line": None,
            "language": "php"
        }

        for error_type, pattern in self.PATTERNS.items():
            match = pattern.search(text)
            if match:
                formatted_type = error_type.replace('_', ' ').title()
                result['type'] = formatted_type
                result['message'] = match.group(0)
                return result

        return result