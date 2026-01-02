import json
from pathlib import Path
from typing import Any, Dict, List

class ConfigManager:

    DEFAULT_CONFIG = {
        'verbose': False,
        'auto_save_history': True,
        'color_output': True,
        'max_history': 100,
        'ai_provider': 'anthropic',
        'openai_api_key': '',
        'anthropic_api_key': '',
        'ai_model': 'gpt-4',
        'default_language': 'python',
        'watch_exclude': ['__pycache__', '.git', 'node_modules', '.venv'],
        'languages': ''
    }

    def __init__(self):
        self.data_dir = Path.home() / '.debugbuddy'
        self.data_dir.mkdir(exist_ok=True)
        self.config_file = self.data_dir / 'config.json'
        self._ensure_config()

    def get(self, key: str, default: Any = None) -> Any:
        config = self._load()
        value = config.get(key, default)
        if key == 'languages' and isinstance(value, str):
            return [lang.strip() for lang in value.split(',') if lang.strip()]
        return value

    def get_all(self) -> Dict:
        return self._load()

    def set(self, key: str, value: Any):
        config = self._load()

        if key in ['verbose', 'auto_save_history', 'color_output']:
            value = self._parse_bool(value)
        elif key == 'max_history':
            value = int(value)
        elif key == 'languages':
            if isinstance(value, (list, tuple)):
                value = ','.join(str(v) for v in value if v)

        config[key] = value
        self._save(config)

    def reset(self):
        self._save(self.DEFAULT_CONFIG.copy())

    def _ensure_config(self):
        if not self.config_file.exists():
            self._save(self.DEFAULT_CONFIG.copy())

    def _load(self) -> Dict:
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)

            merged = self.DEFAULT_CONFIG.copy()
            merged.update(config)
            return merged

        except (json.JSONDecodeError, IOError):
            return self.DEFAULT_CONFIG.copy()

    def _save(self, config: Dict):
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Warning: Could not save config: {e}")

    @staticmethod
    def _parse_bool(value: Any) -> bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ['true', '1', 'yes', 'on']
        return bool(value)