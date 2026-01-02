from typing import List
from pathlib import Path
import re
import json
from ..models.training import TrainingData
from ..models.pattern import Pattern
from ..storage.patterns import PatternManager

class PatternTrainer:

    def __init__(self, storage_manager):
        self.storage = storage_manager
        self.custom_patterns_dir = Path.home() / '.debugbuddy' / 'patterns' / 'custom'
        self.custom_patterns_dir.mkdir(parents=True, exist_ok=True)
        self.pattern_mgr = PatternManager()

    def add_training_example(self, error_text: str, explanation: str, 
                            fix: str, language: str) -> bool:
        training_data = TrainingData(
            error_text=error_text,
            explanation=explanation,
            fix=fix,
            language=language
        )
        return True

    def train_pattern(self, training_examples: List[TrainingData]) -> Pattern:
        keywords = self._extract_keywords(training_examples)

        pattern = Pattern(
            type=self._determine_error_type(training_examples),
            keywords=keywords,
            simple=self._generate_explanation(training_examples),
            fix=self._generate_fix(training_examples),
            language=training_examples[0].language
        )

        self._save_custom_pattern(pattern)

        return pattern

    def list_custom_patterns(self) -> List[Pattern]:
        patterns = []
        for file in self.custom_patterns_dir.glob('*.json'):
            with open(file, 'r') as f:
                data = json.load(f)
                for p in data.get('errors', []):
                    patterns.append(Pattern(**p))
        return patterns

    def delete_custom_pattern(self, pattern_id: str) -> bool:
        for file in self.custom_patterns_dir.glob('*.json'):
            with open(file, 'r+') as f:
                data = json.load(f)
                errors = [p for p in data['errors'] if p['type'] != pattern_id]
                if len(errors) < len(data['errors']):
                    f.seek(0)
                    json.dump({'errors': errors}, f)
                    f.truncate()
                    return True
        return False

    def _extract_keywords(self, examples: List[TrainingData]) -> List[str]:
        keywords = {}
        
        stop_words = {'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'and', 'or', 
                     'is', 'was', 'are', 'were', 'been', 'be', 'have', 'has', 'had',
                     'something', 'went', 'issue', 'failed', 'line'}
        
        for ex in examples:
            words = re.findall(r'\b\w+\b', ex.error_text.lower())
            for word in words:
                if len(word) > 2 and not word.isdigit() and word not in stop_words:
                    keywords[word] = keywords.get(word, 0) + 1
        
        sorted_keywords = sorted(keywords.items(), key=lambda x: x[1], reverse=True)
        return [word for word, count in sorted_keywords[:10]]

    def _determine_error_type(self, examples: List[TrainingData]) -> str:
        common_type = re.search(r'(\w+Error)', examples[0].error_text)
        if common_type:
            return common_type.group(1)
        
        keywords = self._extract_keywords(examples)
        if keywords:
            return f"{keywords[0].capitalize()}Error"
        
        return 'CustomError'

    def _generate_explanation(self, examples: List[TrainingData]) -> str:
        explanations = set(ex.explanation for ex in examples)
        return ' '.join(explanations)

    def _generate_fix(self, examples: List[TrainingData]) -> str:
        fixes = set(ex.fix for ex in examples)
        return ' '.join(fixes)

    def _save_custom_pattern(self, pattern: Pattern):
        file_path = self.custom_patterns_dir / f"{pattern.language}.json"
        patterns = []
        if file_path.exists():
            with open(file_path, 'r') as f:
                data = json.load(f)
                patterns = data.get('errors', [])
        patterns.append(pattern.__dict__)
        with open(file_path, 'w') as f:
            json.dump({'errors': patterns}, f, indent=2)