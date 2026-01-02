import re
from typing import Dict, Optional
from .base import BaseParser

class PythonParser(BaseParser):
    language = 'python'

    PATTERNS = {
        'traceback': re.compile(r'Traceback \(most recent call last\):.*?(\w+Error.*?)(?:\n|$)', re.DOTALL),
        'error_line': re.compile(r'(\w+Error): (.+)'),
        'syntax_error': re.compile(r'SyntaxError: (.+)'),
        'name_error': re.compile(r'NameError: name \'([^\']+)\' is not defined'),
        'type_error': re.compile(r'TypeError: (.+)'),
        'attribute_error': re.compile(r'AttributeError: (.+)'),
        'import_error': re.compile(r'(ImportError|ModuleNotFoundError): (.+)'),
        'index_error': re.compile(r'IndexError: (.+)'),
        'key_error': re.compile(r'KeyError: (.+)'),
        'value_error': re.compile(r'ValueError: (.+)'),
    }

    def parse(self, text: str) -> Optional[Dict]:
        result = {
            "raw": text,
            "type": "Unknown Error",
            "message": text.strip(),
            "file": None,
            "line": None,
            "language": "python"
        }

        file_match = re.search(r'File "([^"]+)", line (\d+)', text)
        if file_match:
            result['file'] = file_match.group(1)
            result['line'] = int(file_match.group(2))

        text_clean = text.strip()

        if "NameError" in text_clean:
            name_patterns = [
                r"name ['\"]([^'\"]+)['\"] is not defined",
                r"name ([^\s]+) is not defined",
            ]
            
            for pattern in name_patterns:
                match = re.search(pattern, text_clean, re.IGNORECASE)
                if match:
                    var_name = match.group(1)
                    result['type'] = 'Name Error'
                    result['message'] = f"name '{var_name}' is not defined"
                    return result
            
            msg_match = re.search(r'NameError:\s*(.+?)(?:\n|$)', text_clean)
            if msg_match:
                result['type'] = 'Name Error'
                result['message'] = msg_match.group(1).strip()
                return result

        if "TypeError" in text_clean:
            msg_match = re.search(r'TypeError:\s*(.+?)(?:\n|$)', text_clean)
            if msg_match:
                result['type'] = 'Type Error'
                result['message'] = msg_match.group(1).strip()
                return result

        if "IndexError" in text_clean:
            msg_match = re.search(r'IndexError:\s*(.+?)(?:\n|$)', text_clean)
            if msg_match:
                result['type'] = 'Index Error'
                result['message'] = msg_match.group(1).strip()
                return result

        if "KeyError" in text_clean:
            msg_match = re.search(r'KeyError:\s*(.+?)(?:\n|$)', text_clean)
            if msg_match:
                result['type'] = 'Key Error'
                result['message'] = msg_match.group(1).strip()
                return result

        if "SyntaxError" in text_clean:
            msg_match = re.search(r'SyntaxError:\s*(.+?)(?:\n|$)', text_clean)
            if msg_match:
                result['type'] = 'Syntax Error'
                result['message'] = msg_match.group(1).strip()
                return result

        if "AttributeError" in text_clean:
            msg_match = re.search(r'AttributeError:\s*(.+?)(?:\n|$)', text_clean)
            if msg_match:
                result['type'] = 'Attribute Error'
                result['message'] = msg_match.group(1).strip()
                return result

        if "ImportError" in text_clean or "ModuleNotFoundError" in text_clean:
            msg_match = re.search(r'(ImportError|ModuleNotFoundError):\s*(.+?)(?:\n|$)', text_clean)
            if msg_match:
                error_name = msg_match.group(1)
                result['type'] = 'Import Error' if error_name == 'ImportError' else 'Module Not Found Error'
                result['message'] = msg_match.group(2).strip()
                return result

        if "ValueError" in text_clean:
            msg_match = re.search(r'ValueError:\s*(.+?)(?:\n|$)', text_clean)
            if msg_match:
                result['type'] = 'Value Error'
                result['message'] = msg_match.group(1).strip()
                return result

        error_match = re.search(r'(\w+Error):\s*(.+?)(?:\n|$)', text_clean)
        if error_match:
            error_type = error_match.group(1)
            if error_type.endswith('Error'):
                base = error_type[:-5]
                spaced = re.sub(r'([A-Z])', r' \1', base).strip()
                result['type'] = f"{spaced} Error"
            else:
                result['type'] = error_type
            result['message'] = error_match.group(2).strip()
            return result

        return result