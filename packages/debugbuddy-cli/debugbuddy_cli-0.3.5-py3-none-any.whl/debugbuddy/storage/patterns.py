import json
from pathlib import Path

class PatternManager:
    def load_patterns(self, language=None):
        pattern_dir = Path(__file__).parent.parent.parent / 'patterns'
        if language:
            file = pattern_dir / f'{language}.json'
            if file.exists():
                with open(file, 'r') as f:
                    return json.load(f)['errors']
            return []
        else:
            patterns = {}
            for file in pattern_dir.glob('*.json'):
                with open(file, 'r') as f:
                    patterns[file.stem] = json.load(f)['errors']
            return patterns

    def save_patterns(self, language, patterns):
        pattern_dir = Path(__file__).parent.parent.parent / 'patterns'
        file = pattern_dir / f'{language}.json'
        with open(file, 'w') as f:
            json.dump({'errors': patterns}, f, indent=2)