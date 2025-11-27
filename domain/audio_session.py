from dataclasses import dataclass
from typing import Optional

@dataclass(slots=True)
class AudioSession:
    pid: int
    process_name: str
    device_name: str
    peak: float
    muted: bool
    volume: float

    @property
    def active(self) -> bool:
        return self.peak > 0.0
