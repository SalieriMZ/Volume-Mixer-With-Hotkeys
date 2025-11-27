from __future__ import annotations
from typing import Protocol, Dict, Optional

class ConfigRepository(Protocol):
    def load_all(self) -> Dict[str, Dict[str, str]]:
        """Return mapping process_name -> {action: hotkey}."""
        ...

    def save_hotkey(self, process_name: str, action: str, hotkey: Optional[str]) -> None:
        ...

    def clear_all(self) -> None:
        ...
