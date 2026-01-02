from dataclasses import dataclass
from typing import List

@dataclass
class Pattern:
    type: str
    keywords: List[str]
    simple: str
    fix: str
    language: str
    example: str = ''