from __future__ import annotations
import time
import threading
from typing import Callable, List, Optional
from domain.audio_session import AudioSession
from application.volume_controller import VolumeController
from application.hotkey_manager import HotkeyManager

class AppManager:
    def __init__(self,
                 volume: VolumeController,
                 hotkeys: HotkeyManager,
                 refresh_interval: float,
                 active_threshold: float) -> None:
        self._volume = volume
        self._hotkeys = hotkeys
        self._refresh_interval = refresh_interval
        self._active_threshold = active_threshold
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._current_pid: Optional[int] = None
        self._current_device: Optional[str] = None
        self._listeners: List[Callable[[List[AudioSession]], None]] = []
        self._only_active = False

    def set_only_active(self, flag: bool) -> None:
        self._only_active = flag
        self.request_refresh()

    def on_sessions_update(self, callback: Callable[[List[AudioSession]], None]) -> None:
        self._listeners.append(callback)

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running = False

    def _loop(self) -> None:
        while self._running:
            self.request_refresh()
            time.sleep(self._refresh_interval)

    def request_refresh(self) -> None:
        sessions = self._volume.list_sessions()
        if self._only_active:
            sessions = [s for s in sessions if s.peak >= self._active_threshold]
        for s in sessions:
            self._hotkeys.set_process_name(s.pid, s.process_name)
        for cb in self._listeners:
            cb(sessions)

    def select_pid(self, pid: Optional[int]) -> None:
        self._current_pid = pid

    def assign_hotkey(self, pid: int, action: str, hotkey: str) -> None:
        def register_fn(act: str, p: int):
            if act == 'up':
                return lambda: self._volume.volume_up(p)
            if act == 'down':
                return lambda: self._volume.volume_down(p)
            if act == 'mute':
                return lambda: self._volume.toggle_mute(p)
            raise ValueError(act)
        callback = register_fn(action, pid)
        self._hotkeys.assign(pid, action, hotkey, callback)

    def ensure_bindings(self, pid: int, process_name: str) -> None:
        def register_fn(act: str, p: int):
            if act == 'up':
                return lambda: self._volume.volume_up(p)
            if act == 'down':
                return lambda: self._volume.volume_down(p)
            if act == 'mute':
                return lambda: self._volume.toggle_mute(p)
            raise ValueError(act)
        self._hotkeys.ensure_for_pid(pid, process_name, register_fn)

    def get_saved_hotkeys(self, process_name: str) -> dict[str, str]:
        return self._hotkeys.get_saved_for_process(process_name)

    def clear_all_hotkeys(self) -> None:
        self._hotkeys.clear_all()
