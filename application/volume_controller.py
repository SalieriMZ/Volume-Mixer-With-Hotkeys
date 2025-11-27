from __future__ import annotations
from typing import List
from ports.audio_repository import AudioRepository
from domain.audio_session import AudioSession

class VolumeController:
    def __init__(self, audio_repo: AudioRepository, volume_step: float) -> None:
        self._audio = audio_repo
        self._step = volume_step

    def list_sessions(self) -> List[AudioSession]:
        return self._audio.list_sessions()

    def volume_up(self, pid: int) -> None:
        self._audio.adjust_volume(pid, +self._step)

    def volume_down(self, pid: int) -> None:
        self._audio.adjust_volume(pid, -self._step)

    def toggle_mute(self, pid: int) -> None:
        self._audio.toggle_mute(pid)
