"""Application entrypoint wiring Hexagonal Architecture components."""
from typing import Optional
import os
import sys
from adapters.windows_audio_adapter import WindowsAudioAdapter
from adapters.keyboard_lib_adapter import KeyboardLibAdapter
from adapters.json_config_adapter import JsonConfigAdapter
from application.volume_controller import VolumeController
from application.hotkey_manager import HotkeyManager
from application.app_manager import AppManager
from i18n.translator import Translator
from ui.app_ui import AppUI

VOLUME_STEP = 0.05
REFRESH_INTERVAL = 1.0
ACTIVE_PEAK_THRESHOLD = 0.02

def build_app(language: Optional[str] = None) -> AppUI:
    if sys.platform != 'win32':
        raise SystemExit('Windows only')
    audio_repo = WindowsAudioAdapter()
    hotkey_service = KeyboardLibAdapter()
    config_path = os.path.join(os.path.dirname(__file__), 'hotkeys.json')
    config_repo = JsonConfigAdapter(config_path)
    volume_ctrl = VolumeController(audio_repo, VOLUME_STEP)
    hotkey_manager = HotkeyManager(hotkey_service, config_repo)
    app_manager = AppManager(volume_ctrl, hotkey_manager, REFRESH_INTERVAL, ACTIVE_PEAK_THRESHOLD)
    translator = Translator(language)
    ui = AppUI(app_manager, translator)
    return ui

if __name__ == '__main__':
    ui = build_app()
    ui.mainloop()
