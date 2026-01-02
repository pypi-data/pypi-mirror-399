import re
from typing import Dict, Optional
from .base import BaseParser

class CParser(BaseParser):
    language = 'c'

    PATTERNS = {
        'syntax_error': re.compile(r'(syntax error|error:.*syntax)', re.IGNORECASE),
        'undefined_ref': re.compile(r'undefined reference to \'([^\']+)\''),
        'type_mismatch': re.compile(r'incompatible types (.+)'),
    }

    def parse(self, text: str) -> Optional[Dict]:
        result = {
            "type": "Unknown Error",
            "message": text.strip(),
            "file": None,
            "line": None,
            "language": "c"
        }

        for error_type, pattern in self.PATTERNS.items():
            match = pattern.search(text)
            if match:
                formatted_type = error_type.replace('_', ' ').title()
                result['type'] = formatted_type
                result['message'] = match.group(0)
                return result

        return result