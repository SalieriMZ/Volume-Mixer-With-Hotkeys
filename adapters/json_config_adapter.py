from __future__ import annotations
import json
import os
from typing import Dict, Optional
from ports.config_repository import ConfigRepository

class JsonConfigAdapter(ConfigRepository):
    def __init__(self, path: str) -> None:
        self._path = path
        if not os.path.exists(self._path):
            self._write({})

    def _read(self) -> Dict[str, Dict[str, str]]:
        try:
            with open(self._path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}

    def _write(self, data: Dict[str, Dict[str, str]]) -> None:
        try:
            with open(self._path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def load_all(self) -> Dict[str, Dict[str, str]]:
        return self._read()

    def save_hotkey(self, process_name: str, action: str, hotkey: Optional[str]) -> None:
        data = self._read()
        proc_key = process_name.lower()
        entry = data.get(proc_key, {})
        if hotkey:
            entry[action] = hotkey
        else:
            entry.pop(action, None)
        if entry:
            data[proc_key] = entry
        else:
            data.pop(proc_key, None)
        self._write(data)

    def clear_all(self) -> None:
        self._write({})
