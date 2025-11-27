from dataclasses import dataclass, field
from typing import Dict, Optional

ACTIONS = ("up", "down", "mute")

@dataclass(slots=True)
class HotkeyConfig:
    process_name: str
    bindings: Dict[str, str] = field(default_factory=dict)  # action -> hotkey

    def set(self, action: str, hotkey: Optional[str]) -> None:
        if action not in ACTIONS:
            raise ValueError(f"Invalid action: {action}")
        if hotkey:
            self.bindings[action] = hotkey
        else:
            self.bindings.pop(action, None)

    def get(self, action: str) -> Optional[str]:
        return self.bindings.get(action)
