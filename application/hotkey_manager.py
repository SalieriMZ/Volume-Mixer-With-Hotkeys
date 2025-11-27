from __future__ import annotations
from typing import Dict, Optional
from ports.hotkey_service import HotkeyService
from ports.config_repository import ConfigRepository

class HotkeyManager:
    def __init__(self, hotkeys: HotkeyService, config_repo: ConfigRepository) -> None:
        self._svc = hotkeys
        self._cfg = config_repo
        self._handlers: Dict[tuple[int, str], int] = {}
        self._pid_to_name: Dict[int, str] = {}

    def set_process_name(self, pid: int, name: str) -> None:
        if name:
            self._pid_to_name[pid] = name

    def assign(self, pid: int, action: str, hotkey: str, callback) -> None:
        key = (pid, action)
        handler_id = self._handlers.get(key)
        if handler_id is not None:
            self._svc.remove(handler_id)
        new_id = self._svc.register(hotkey, callback)
        self._handlers[key] = new_id
        name = self._pid_to_name.get(pid)
        if name:
            self._cfg.save_hotkey(name, action, hotkey)

    def clear_all(self) -> None:
        self._svc.clear_all()
        self._handlers.clear()
        self._cfg.clear_all()

    def remove_pid(self, pid: int) -> None:
        to_remove = [k for k in self._handlers.keys() if k[0] == pid]
        for k in to_remove:
            hid = self._handlers.pop(k, None)
            if hid is not None:
                self._svc.remove(hid)

    def ensure_for_pid(self, pid: int, process_name: str, register_fn) -> None:
        all_cfg = self._cfg.load_all()
        saved = all_cfg.get(process_name.lower(), {})
        if not saved:
            return
        self.set_process_name(pid, process_name)
        for action, hotkey in saved.items():
            key = (pid, action)
            if key in self._handlers:
                continue
            self.assign(pid, action, hotkey, register_fn(action, pid))

    def get_saved_for_process(self, process_name: str) -> Dict[str, str]:
        all_cfg = self._cfg.load_all()
        return all_cfg.get(process_name.lower(), {})
