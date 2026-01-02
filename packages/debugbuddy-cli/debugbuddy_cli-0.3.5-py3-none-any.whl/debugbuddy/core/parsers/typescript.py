import re
from typing import Dict, Optional
from .base import BaseParser

class TypeScriptParser(BaseParser):
    language = 'typescript'

    PATTERNS = {
        'type_error': re.compile(r'Type error: (.+)', re.IGNORECASE),
        'declaration_error': re.compile(r'Cannot find name \'([^\']+)\''),
        'module_error': re.compile(r'Cannot find module \'([^\']+)\''),
    }

    def parse(self, text: str) -> Optional[Dict]:
        result = {
            "type": "Unknown Error",
            "message": text.strip(),
            "file": None,
            "line": None,
            "language": "typescript"
        }

        for error_type, pattern in self.PATTERNS.items():
            match = pattern.search(text)
            if match:
                formatted_type = error_type.replace('_', ' ').title()
                result['type'] = formatted_type
                result['message'] = match.group(0)
                return result

        return result