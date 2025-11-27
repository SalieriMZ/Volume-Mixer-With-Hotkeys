from __future__ import annotations
from typing import Dict
import locale

SUPPORTED = {"en", "es"}

_DEFAULT_KEYS = {
    # General / window
    "app.title": {"en": "Funny Volume App", "es": "cosa chistosa para la polola"},
    "filter.active": {"en": "Only apps with active audio", "es": "Solo apps con audio activo"},
    "col.pid": {"en": "PID", "es": "PID"},
    "col.process": {"en": "Process", "es": "Proceso"},
    "col.device": {"en": "Device", "es": "Dispositivo"},
    "col.peak": {"en": "Peak", "es": "Peak"},
    "col.muted": {"en": "Mute", "es": "Mute"},
    "col.volume": {"en": "Vol", "es": "Vol"},
    "label.selection.none": {"en": "Select a program from the list", "es": "Selecciona un programa de la lista"},
    "label.selection": {"en": "Selected: {name} (PID {pid})", "es": "Seleccionado: {name} (PID {pid})"},
    "hotkey.up": {"en": "Volume Up", "es": "Subir volumen"},
    "hotkey.down": {"en": "Volume Down", "es": "Bajar volumen"},
    "hotkey.mute": {"en": "Mute/Unmute", "es": "Mute/Unmute"},
    "hotkey.assign": {"en": "Assign", "es": "Asignar"},
    "hotkey.clear": {"en": "Clear hotkeys", "es": "Limpiar hotkeys"},
    "hotkey.none": {"en": "Not assigned", "es": "No asignado"},
    "hint.admin": {"en": "Tip: Run as Administrator if hotkeys fail.", "es": "Sugerencia: Ejecuta como Administrador si los hotkeys no funcionan."},
    "dialog.assign.title": {"en": "Capture hotkey", "es": "Capturar hotkey"},
    "dialog.assign.instr": {"en": "Press the key combination... (ESC to cancel)", "es": "Presiona la combinación de teclas... (ESC para cancelar)"},
    "error.select.first": {"en": "Select an application first.", "es": "Primero selecciona un programa."},
    "error.keyboard.missing": {"en": "'keyboard' library not installed.", "es": "Librería 'keyboard' no instalada."},
    "error.audio.missing": {"en": "'pycaw' library not installed.", "es": "Librería 'pycaw' no instalada."},
    "error.win.only": {"en": "This application works only on Windows.", "es": "Esta aplicación funciona solo en Windows."},
    "error.hotkey.register": {"en": "Could not register hotkey {hotkey}: {error}", "es": "No se pudo registrar hotkey {hotkey}: {error}"},
}

class Translator:
    def __init__(self, language: str | None = None) -> None:
        if language is None:
            lang_tuple = locale.getdefaultlocale()
            sys_lang = (lang_tuple[0] or "en") if lang_tuple else "en"
            language = "es" if sys_lang.lower().startswith("es") else "en"
        self._lang = language if language in SUPPORTED else "en"
        self._catalog: Dict[str, Dict[str, str]] = _DEFAULT_KEYS

    @property
    def language(self) -> str:
        return self._lang

    def set_language(self, lang: str) -> None:
        if lang in SUPPORTED:
            self._lang = lang

    def t(self, key: str, **kwargs) -> str:
        entry = self._catalog.get(key, {})
        text = entry.get(self._lang) or entry.get("en") or key
        try:
            return text.format(**kwargs)
        except Exception:
            return text
