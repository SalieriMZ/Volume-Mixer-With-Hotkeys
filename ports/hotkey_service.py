from __future__ import annotations
from typing import Protocol, Callable

class HotkeyService(Protocol):
    def register(self, hotkey: str, callback: Callable[[], None]) -> int:
        """Register global hotkey; returns handler id."""
        ...

    def remove(self, handler_id: int) -> None:
        ...

    def clear_all(self) -> None:
        ...
