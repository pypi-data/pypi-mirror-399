from dataclasses import dataclass

@dataclass
class Error:
    raw: str
    type: str
    message: str
    file: str = None
    line: str = None
    language: str = 'unknown'