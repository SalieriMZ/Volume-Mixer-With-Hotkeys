from __future__ import annotations
from typing import Protocol, List
from domain.audio_session import AudioSession

class AudioRepository(Protocol):
    def list_sessions(self) -> List[AudioSession]:
        """Return all audio sessions across output devices."""
        ...

    def adjust_volume(self, pid: int, delta: float) -> None:
        """Adjust volume of session by pid."""
        ...

    def toggle_mute(self, pid: int) -> None:
        """Toggle mute state for session by pid."""
        ...
