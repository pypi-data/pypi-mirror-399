import json
from pathlib import Path

class CacheManager:
    def __init__(self):
        self.cache_dir = Path.home() / '.debugbuddy' / 'cache'
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get(self, key):
        file = self.cache_dir / f'{key}.json'
        if file.exists():
            with open(file, 'r') as f:
                return json.load(f)
        return None

    def set(self, key, value):
        file = self.cache_dir / f'{key}.json'
        with open(file, 'w') as f:
            json.dump(value, f)