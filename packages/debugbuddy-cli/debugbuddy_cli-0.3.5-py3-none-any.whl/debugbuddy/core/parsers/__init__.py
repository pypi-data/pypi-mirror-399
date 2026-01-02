import re
import json
from .base import BaseParser
from .python import PythonParser
from .javascript import JavaScriptParser
from .typescript import TypeScriptParser
from .c import CParser
from .php import PHPParser
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

class ErrorParser:
    def __init__(self):
        self.parsers = {
            'python': PythonParser(),
            'javascript': JavaScriptParser(),
            'typescript': TypeScriptParser(),
            'c': CParser(),
            'php': PHPParser(),
        }

    def parse(self, error_text: str, language=None):
        error_text = error_text.strip()
        lower_text = error_text.lower()

        if language:
            if language in self.parsers:
                result = self.parsers[language].parse(error_text)
                if result:
                    result['language'] = language
                    return result

        js_specific_indicators = [
            'referenceerror',
            'urierror',
            'evalerror',
        ]
        
        if any(indicator in lower_text for indicator in js_specific_indicators):
            result = self.parsers['javascript'].parse(error_text)
            if result:
                result['language'] = 'javascript'
                return result
        
        python_indicators = [
            'nameerror', 'valueerror', 'indentationerror',
            'modulenotfounderror', 'zerodivisionerror', 'filenotfounderror',
            'traceback', 'file "', "name '", 'is not defined'
        ]
        
        if any(indicator in lower_text for indicator in python_indicators):
            result = self.parsers['python'].parse(error_text)
            if result:
                result['language'] = 'python'
                return result
        
        if any(err in lower_text for err in ['typeerror', 'syntaxerror']):
            if any(clue in lower_text for clue in ['cannot read property', 'undefined', 'null', 'javascript', 'js', 'node']):
                result = self.parsers['javascript'].parse(error_text)
                if result:
                    result['language'] = 'javascript'
                    return result
            
            if any(clue in lower_text for clue in ['traceback', "name '", 'python', '.py']):
                result = self.parsers['python'].parse(error_text)
                if result:
                    result['language'] = 'python'
                    return result
            
            result = self.parsers['python'].parse(error_text)
            if result:
                result['language'] = 'python'
                return result
        
        if any(err in lower_text for err in ['indexerror', 'keyerror', 'attributeerror', 'importerror']):
            result = self.parsers['python'].parse(error_text)
            if result:
                result['language'] = 'python'
                return result
        
        ts_indicators = ['type error', 'cannot find name', 'typescript', 'ts', 'ts2']
        if any(indicator in lower_text for indicator in ts_indicators):
            result = self.parsers['typescript'].parse(error_text)
            if result:
                result['language'] = 'typescript'
                return result
        
        c_indicators = ['undefined reference', 'gcc', 'segmentation fault', 'segfault']
        if any(indicator in lower_text for indicator in c_indicators):
            result = self.parsers['c'].parse(error_text)
            if result:
                result['language'] = 'c'
                return result
        
        php_indicators = ['parse error', 'fatal error', 'php']
        if any(indicator in lower_text for indicator in php_indicators):
            result = self.parsers['php'].parse(error_text)
            if result:
                result['language'] = 'php'
                return result
        
        return self._parse_generic(error_text)

    def _parse_generic(self, text: str) -> Dict:
        lines = text.split('\n')
        first_line = lines[0] if lines else text

        return {
            'raw': text,
            'type': 'Unknown Error',
            'message': first_line[:200],
            'language': 'unknown',
            'file': None,
            'line': None,
        }