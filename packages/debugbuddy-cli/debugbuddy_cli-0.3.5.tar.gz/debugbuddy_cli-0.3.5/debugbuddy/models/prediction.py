from dataclasses import dataclass
from typing import Optional

@dataclass
class Prediction:
    file: str
    line: int
    column: Optional[int]
    error_type: str
    message: str
    confidence: float
    suggestion: str
    severity: str