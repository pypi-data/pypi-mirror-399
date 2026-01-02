import re
from typing import Dict, Optional

class BaseParser:
    PATTERNS = {}
    language = 'unknown'

    def parse(self, text: str) -> Optional[Dict]:
        result = {
            'raw': text,
            'type': "Unknown Error",
            'message': text.strip(),
            'file': None,
            'line': None,
            'language': self.language,
        }

        file_match = re.search(r'File "([^"]+)", line (\d+)', text)
        if file_match:
            result['file'] = file_match.group(1)
            result['line'] = int(file_match.group(2))

        return result if 'type' in result and result['type'] != "Unknown Error" else result