from __future__ import annotations
from typing import List, Optional
from domain.audio_session import AudioSession
from ports.audio_repository import AudioRepository

try:
    from pycaw.pycaw import (
        AudioUtilities,
        IAudioMeterInformation,
        IAudioSessionControl2,
    )
    from pycaw.utils import AudioSession as PycawAudioSession
    from pycaw.constants import EDataFlow, DEVICE_STATE
except Exception:
    AudioUtilities = None

try:
    import comtypes
except Exception:
    comtypes = None

class WindowsAudioAdapter(AudioRepository):
    def __init__(self) -> None:
        self._com_init = False
        self._DEVICE_FALLBACK = "(device)"

    def _ensure_com(self) -> None:
        if comtypes and not self._com_init:
            try:
                comtypes.CoInitialize()
                self._com_init = True
            except Exception:
                pass

    def _get_all_devices(self):
        if AudioUtilities is None:
            return []
        try:
            return AudioUtilities.GetAllDevices(
                data_flow=EDataFlow.eRender.value,
                device_state=DEVICE_STATE.MASK_ALL.value,
            )
        except Exception:
            try:
                return [AudioUtilities.GetSpeakers()]
            except Exception:
                return []

    def _get_device_name(self, dev) -> str:
        if dev is None:
            return self._DEVICE_FALLBACK
        try:
            return dev.FriendlyName or self._DEVICE_FALLBACK
        except Exception:
            return self._DEVICE_FALLBACK

    def _get_session_enumerator(self, dev):
        if dev is None:
            return None, 0
        try:
            mgr = dev.AudioSessionManager
        except Exception:
            mgr = None
        if mgr is None:
            return None, 0
        try:
            enum = mgr.GetSessionEnumerator()
            count = enum.GetCount()
            return enum, count
        except Exception:
            return None, 0

    def _get_pycaw_session(self, enum, index):
        try:
            ctl = enum.GetSession(index)
            ctl2 = ctl.QueryInterface(IAudioSessionControl2)
            return PycawAudioSession(ctl2)
        except Exception:
            return None

    def _get_proc_info(self, session) -> tuple[Optional[int], Optional[str]]:
        proc = getattr(session, "Process", None)
        if proc is None:
            return None, None
        try:
            name = proc.name()
            pid = proc.pid
            return pid, name
        except Exception:
            return None, None

    def _get_peak(self, session) -> float:
        try:
            meter = session._ctl.QueryInterface(IAudioMeterInformation)
            return float(meter.GetPeakValue())
        except Exception:
            return 0.0

    def _get_mute_and_volume(self, session) -> tuple[bool, float]:
        try:
            muted = bool(session.SimpleAudioVolume.GetMute())
            vol = float(session.SimpleAudioVolume.GetMasterVolume())
            return muted, vol
        except Exception:
            return False, 0.0

    def _find_session_in_devices(self, pid: int):
        devices = self._get_all_devices()
        for dev in devices:
            enum, count = self._get_session_enumerator(dev)
            if enum is None or count <= 0:
                continue
            for i in range(count):
                session = self._get_pycaw_session(enum, i)
                if session and self._session_matches_pid(session, pid):
                    return session
        return None

    def _find_session_in_all(self, pid: int):
        try:
            for s in AudioUtilities.GetAllSessions():
                if self._session_matches_pid(s, pid):
                    return s
        except Exception:
            pass
        return None

    def _session_matches_pid(self, session, pid: int) -> bool:
        proc = getattr(session, "Process", None)
        if proc is None:
            return False
        try:
            return proc.pid == pid
        except Exception:
            return False

    def list_sessions(self) -> List[AudioSession]:
        self._ensure_com()
        items: List[AudioSession] = []
        if AudioUtilities is None:
            return items
        devices = self._get_all_devices()
        for dev in devices:
            device_name = self._get_device_name(dev)
            enum, count = self._get_session_enumerator(dev)
            if enum is None or count <= 0:
                continue
            for i in range(count):
                session = self._get_pycaw_session(enum, i)
                if session is None:
                    continue
                pid, name = self._get_proc_info(session)
                if not pid or not name:
                    continue
                peak = self._get_peak(session)
                muted, vol = self._get_mute_and_volume(session)
                items.append(AudioSession(
                    pid=pid,
                    process_name=name,
                    device_name=device_name,
                    peak=peak,
                    muted=muted,
                    volume=vol,
                ))
        return items

    def _get_session(self, pid: int):
        if AudioUtilities is None:
            return None
        s = self._find_session_in_devices(pid)
        if s:
            return s
        return self._find_session_in_all(pid)

    def adjust_volume(self, pid: int, delta: float) -> None:
        s = self._get_session(pid)
        if not s:
            return
        try:
            current = float(s.SimpleAudioVolume.GetMasterVolume())
            new_v = min(1.0, max(0.0, current + delta))
            s.SimpleAudioVolume.SetMasterVolume(new_v, None)
        except Exception:
            pass

    def toggle_mute(self, pid: int) -> None:
        s = self._get_session(pid)
        if not s:
            return
        try:
            m = bool(s.SimpleAudioVolume.GetMute())
            s.SimpleAudioVolume.SetMute(not m, None)
        except Exception:
            pass
