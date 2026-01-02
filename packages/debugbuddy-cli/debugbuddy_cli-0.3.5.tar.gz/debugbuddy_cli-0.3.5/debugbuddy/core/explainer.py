import json
import difflib
from pathlib import Path
from typing import Dict, List, Optional
import builtins
import re

class ErrorExplainer:

    def __init__(self):
        self.patterns = self._load_patterns()

    def _load_patterns(self) -> Dict:
        patterns = {}
        pattern_dir = Path(__file__).parent.parent.parent / 'patterns'

        for pattern_file in pattern_dir.glob('*.json'):
            try:
                with open(pattern_file, 'r', encoding='utf-8') as f:
                    patterns[pattern_file.stem] = json.load(f)
            except Exception as e:
                print(f"Warning: Could not load {pattern_file}: {e}")

        return patterns

    def explain(self, parsed_error: Dict) -> Dict:

        error_type = parsed_error.get('type', '').lower()
        language = parsed_error.get('language', 'common')
        message = parsed_error.get('message', '')

        explanation = self._match_pattern(error_type, message, language)

        if not explanation:
            explanation = self._generic_explanation(parsed_error)

        if 'name' in error_type.lower() and 'not defined' in message.lower():
            explanation['suggestions'] = self._get_name_suggestions(message, parsed_error)

        return explanation

    def _match_pattern(self, error_type: str, message: str, language: str) -> Optional[Dict]:

        if language in self.patterns:
            for pattern in self.patterns[language].get('errors', []):
                if self._matches(error_type, message, pattern):
                    return pattern.copy()

        if 'common' in self.patterns:
            for pattern in self.patterns['common'].get('errors', []):
                if self._matches(error_type, message, pattern):
                    return pattern.copy()

        return None

    def _matches(self, error_type: str, message: str, pattern: Dict) -> bool:

        pattern_type = pattern.get('type', '').lower()
        keywords = pattern.get('keywords', [])

        if pattern_type and pattern_type in error_type:
            return True

        message_lower = message.lower()
        for keyword in keywords:
            if keyword.lower() in message_lower:
                return True

        return False

    def _generic_explanation(self, parsed_error: Dict) -> Dict:
        return {
            'simple': 'Generic error occurred.',
            'fix': 'Check the error message for clues.',
            'example': '',
            'did_you_mean': [],
        }

    def _get_name_suggestions(self, message: str, parsed_error: Dict) -> List[str]:
        match = re.search(r"name '([^']+)' is not defined", message)
        if not match:
            return []

        undefined_name = match.group(1)

        dir_builtins = dir(builtins)
        close_matches = difflib.get_close_matches(
            undefined_name,
            dir_builtins,
            n=3,
            cutoff=0.6
        )

        suggestions = []
        if close_matches:
            suggestions.extend([f"Did you mean: {match}?" for match in close_matches])

        if not suggestions:
            suggestions = [
                f"Check spelling of '{undefined_name}'",
                f"Did you forget to define '{undefined_name}'?",
                f"Need to import '{undefined_name}'?"
            ]

        return suggestions

    def search_patterns(self, keyword: str) -> List[Dict]:

        results = []
        keyword_lower = keyword.lower()

        for lang, data in self.patterns.items():
            for pattern in data.get('errors', []):
                searchable = [
                    pattern.get('type', ''),
                    pattern.get('simple', ''),
                    pattern.get('fix', ''),
                ] + pattern.get('keywords', [])

                if any(keyword_lower in str(field).lower() for field in searchable):
                    results.append({
                        'name': pattern.get('type', 'Unknown'),
                        'description': pattern.get('simple', '').replace('Search ', ''),
                        'language': lang
                    })

        return results