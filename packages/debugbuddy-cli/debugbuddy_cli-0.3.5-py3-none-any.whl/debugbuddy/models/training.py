from dataclasses import dataclass
from datetime import datetime

@dataclass
class TrainingData:
    error_text: str
    explanation: str
    fix: str
    language: str
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()