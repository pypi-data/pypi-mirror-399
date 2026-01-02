from pathlib import Path

def validate_path(path):
    if not Path(path).exists():
        raise ValueError("Path does not exist")