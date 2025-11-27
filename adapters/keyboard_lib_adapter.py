from __future__ import annotations
from typing import Callable
from ports.hotkey_service import HotkeyService

try:
    import keyboard
except Exception:
    keyboard = None

class KeyboardLibAdapter(HotkeyService):
    def register(self, hotkey: str, callback: Callable[[], None]) -> int:
        if keyboard is None:
            raise RuntimeError("keyboard lib not available")
        return keyboard.add_hotkey(hotkey, callback, suppress=False)

    def remove(self, handler_id: int) -> None:
        if keyboard is None:
            return
        try:
            keyboard.remove_hotkey(handler_id)
        except Exception:
            pass

    def clear_all(self) -> None:
        if keyboard is None:
            return
        try:
            keyboard.clear_all_hotkeys()
        except Exception:
            pass
