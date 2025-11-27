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

    def _ensure_com(self) -> None:
        if comtypes and not self._com_init:
            try:
                comtypes.CoInitialize()
                self._com_init = True
            except Exception:
                pass

    def list_sessions(self) -> List[AudioSession]:
        self._ensure_com()
        items: List[AudioSession] = []
        if AudioUtilities is None:
            return items
        try:
            devices = AudioUtilities.GetAllDevices(
                data_flow=EDataFlow.eRender.value,
                device_state=DEVICE_STATE.MASK_ALL.value,
            )
        except Exception:
            try:
                devices = [AudioUtilities.GetSpeakers()]
            except Exception:
                devices = []
        for dev in devices:
            if dev is None:
                continue
            try:
                device_name = dev.FriendlyName or "(device)"
            except Exception:
                device_name = "(device)"
            try:
                mgr = dev.AudioSessionManager
            except Exception:
                mgr = None
            if mgr is None:
                continue
            try:
                enum = mgr.GetSessionEnumerator()
                count = enum.GetCount()
            except Exception:
                continue
            for i in range(count):
                try:
                    ctl = enum.GetSession(i)
                    ctl2 = ctl.QueryInterface(IAudioSessionControl2)
                    session = PycawAudioSession(ctl2)
                except Exception:
                    continue
                proc = getattr(session, "Process", None)
                pid: Optional[int] = None
                name: Optional[str] = None
                if proc is not None:
                    try:
                        name = proc.name()
                        pid = proc.pid
                    except Exception:
                        pass
                if not pid or not name:
                    continue
                # Peak
                peak = 0.0
                try:
                    meter = session._ctl.QueryInterface(IAudioMeterInformation)
                    peak = float(meter.GetPeakValue())
                except Exception:
                    pass
                muted = False
                vol = 0.0
                try:
                    muted = bool(session.SimpleAudioVolume.GetMute())
                    vol = float(session.SimpleAudioVolume.GetMasterVolume())
                except Exception:
                    pass
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
        try:
            devices = AudioUtilities.GetAllDevices(
                data_flow=EDataFlow.eRender.value,
                device_state=DEVICE_STATE.MASK_ALL.value,
            )
        except Exception:
            devices = []
        for dev in devices:
            if dev is None:
                continue
            try:
                mgr = dev.AudioSessionManager
                enum = mgr.GetSessionEnumerator()
                count = enum.GetCount()
            except Exception:
                continue
            for i in range(count):
                try:
                    ctl = enum.GetSession(i)
                    ctl2 = ctl.QueryInterface(IAudioSessionControl2)
                    session = PycawAudioSession(ctl2)
                except Exception:
                    continue
                proc = getattr(session, "Process", None)
                if proc is None:
                    continue
                try:
                    if proc.pid == pid:
                        return session
                except Exception:
                    continue
        try:
            for s in AudioUtilities.GetAllSessions():
                proc = getattr(s, "Process", None)
                if proc is None:
                    continue
                try:
                    if proc.pid == pid:
                        return s
                except Exception:
                    continue
        except Exception:
            pass
        return None

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
