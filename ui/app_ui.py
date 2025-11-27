from __future__ import annotations
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Tuple, List
from application.app_manager import AppManager
from domain.audio_session import AudioSession
from i18n.translator import Translator

class AppUI(tk.Tk):
    def __init__(self, manager: AppManager, translator: Translator) -> None:
        super().__init__()
        self._m = manager
        self._t = translator
        self.title(self._t.t("app.title"))
        self.geometry("820x520")
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._current_selection_pid: Optional[int] = None
        self._current_selection_key: Optional[Tuple[int, str]] = None
        self._pid_to_name: dict[int, str] = {}

        self.only_active_var = tk.BooleanVar(value=False)
        self._build_ui()
        self._m.on_sessions_update(self._update_sessions)
        self._m.start()

    def _build_ui(self) -> None:
        top = ttk.Frame(self)
        top.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        toolbar = ttk.Frame(top)
        toolbar.pack(fill=tk.X, pady=(0, 6))
        chk = ttk.Checkbutton(toolbar, text=self._t.t("filter.active"), variable=self.only_active_var,
                               command=self._toggle_only_active)
        chk.pack(side=tk.LEFT)

        cols = ("pid", "name", "device", "peak", "muted", "volume")
        self.tree = ttk.Treeview(top, columns=cols, show="headings", height=12)
        self.tree.heading("pid", text=self._t.t("col.pid"))
        self.tree.heading("name", text=self._t.t("col.process"))
        self.tree.heading("device", text=self._t.t("col.device"))
        self.tree.heading("peak", text=self._t.t("col.peak"))
        self.tree.heading("muted", text=self._t.t("col.muted"))
        self.tree.heading("volume", text=self._t.t("col.volume"))

        self.tree.column("pid", width=80, anchor=tk.CENTER)
        self.tree.column("name", width=300)
        self.tree.column("device", width=180)
        self.tree.column("peak", width=80, anchor=tk.CENTER)
        self.tree.column("muted", width=80, anchor=tk.CENTER)
        self.tree.column("volume", width=80, anchor=tk.CENTER)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        scroll = ttk.Scrollbar(top, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        bottom = ttk.LabelFrame(self, text=self._t.t("label.selection.none"))
        bottom.pack(fill=tk.X, padx=10, pady=5)
        self.sel_label_frame = bottom
        self.sel_label = bottom  # reuse for title text

        self.up_var = tk.StringVar(value=self._t.t("hotkey.none"))
        self.down_var = tk.StringVar(value=self._t.t("hotkey.none"))
        self.mute_var = tk.StringVar(value=self._t.t("hotkey.none"))

        ttk.Label(bottom, text=f"{self._t.t('hotkey.up')}:" ).grid(row=0, column=0, sticky="e", padx=6, pady=6)
        ttk.Button(bottom, text=self._t.t("hotkey.assign"), command=lambda: self._capture_hotkey('up')).grid(row=0, column=1, sticky="w", padx=6, pady=6)
        ttk.Label(bottom, textvariable=self.up_var, foreground="#555").grid(row=0, column=2, sticky="w", padx=6)

        ttk.Label(bottom, text=f"{self._t.t('hotkey.down')}:" ).grid(row=1, column=0, sticky="e", padx=6, pady=6)
        ttk.Button(bottom, text=self._t.t("hotkey.assign"), command=lambda: self._capture_hotkey('down')).grid(row=1, column=1, sticky="w", padx=6, pady=6)
        ttk.Label(bottom, textvariable=self.down_var, foreground="#555").grid(row=1, column=2, sticky="w", padx=6)

        ttk.Label(bottom, text=f"{self._t.t('hotkey.mute')}:" ).grid(row=2, column=0, sticky="e", padx=6, pady=6)
        ttk.Button(bottom, text=self._t.t("hotkey.assign"), command=lambda: self._capture_hotkey('mute')).grid(row=2, column=1, sticky="w", padx=6, pady=6)
        ttk.Label(bottom, textvariable=self.mute_var, foreground="#555").grid(row=2, column=2, sticky="w", padx=6)

        ttk.Button(bottom, text=self._t.t("hotkey.clear"), command=self._clear_hotkeys).grid(row=3, column=0, padx=6, pady=10)

        note = ttk.Label(self, text=self._t.t("hint.admin"), foreground="#666")
        note.pack(anchor="w", padx=12, pady=(0, 10))

    def _toggle_only_active(self) -> None:
        self._m.set_only_active(self.only_active_var.get())

    def _update_sessions(self, sessions: List[AudioSession]) -> None:
        prev_key = self._current_selection_key
        seen = set()
        for s in sessions:
            iid = f"{s.pid}::{s.device_name}"
            seen.add(iid)
            vals = [s.pid, s.process_name, s.device_name, f"{s.peak:.2f}", ("Sí" if s.muted else "No"), f"{int(s.volume*100):d}%"]
            if iid in self.tree.get_children():
                self.tree.item(iid, values=vals)
            else:
                self.tree.insert('', tk.END, iid=iid, values=vals)
            self._m.ensure_bindings(s.pid, s.process_name)
        for iid in list(self.tree.get_children()):
            if iid not in seen:
                self.tree.delete(iid)
        if prev_key:
            pid, device = prev_key
            iid = f"{pid}::{device}"
            if iid in self.tree.get_children():
                self.tree.selection_set(iid)
            else:
                self._clear_selection_labels()

    def _clear_selection_labels(self) -> None:
        self._current_selection_pid = None
        self._current_selection_key = None
        self.sel_label_frame.configure(text=self._t.t("label.selection.none"))
        self.up_var.set(self._t.t("hotkey.none"))
        self.down_var.set(self._t.t("hotkey.none"))
        self.mute_var.set(self._t.t("hotkey.none"))

    def _on_select(self, _evt=None) -> None:
        sel = self.tree.selection()
        if not sel:
            self._clear_selection_labels()
            return
        iid = sel[0]
        item = self.tree.item(iid)
        values = item['values']
        pid = int(values[0])
        name = str(values[1])
        device = str(values[2])
        self._current_selection_pid = pid
        self._current_selection_key = (pid, device)
        self.sel_label_frame.configure(text=self._t.t("label.selection", name=name, pid=pid))

    def _capture_hotkey(self, action: str) -> None:
        if self._current_selection_pid is None:
            messagebox.showinfo(self._t.t("hotkey.assign"), self._t.t("error.select.first"))
            return
        try:
            import keyboard
        except Exception:
            messagebox.showerror(self._t.t("hotkey.assign"), self._t.t("error.keyboard.missing"))
            return
        pid = self._current_selection_pid
        cap = tk.Toplevel(self)
        cap.title(self._t.t("dialog.assign.title"))
        cap.geometry("360x120")
        cap.transient(self)
        cap.grab_set()
        ttk.Label(cap, text=self._t.t("dialog.assign.instr")).pack(padx=10, pady=10)
        key_var = tk.StringVar(value="...")
        ttk.Label(cap, textvariable=key_var, font=("Segoe UI", 12, "bold")).pack(pady=4)

        def capture_thread():
            import threading
            def run():
                try:
                    hk = keyboard.read_hotkey(suppress=False)
                    if hk and hk.lower() == 'esc':
                        return
                    key_var.set(hk)
                    self.after(0, lambda: self._assign(pid, action, hk))
                finally:
                    self.after(0, cap.destroy)
            threading.Thread(target=run, daemon=True).start()
        capture_thread()

        cap.bind('<Escape>', lambda _e: cap.destroy())

    def _assign(self, pid: int, action: str, hotkey: str) -> None:
        self._m.assign_hotkey(pid, action, hotkey)
        if action == 'up':
            self.up_var.set(hotkey)
        elif action == 'down':
            self.down_var.set(hotkey)
        elif action == 'mute':
            self.mute_var.set(hotkey)

    def _clear_hotkeys(self) -> None:
        self._m.clear_all_hotkeys()
        self.up_var.set(self._t.t("hotkey.none"))
        self.down_var.set(self._t.t("hotkey.none"))
        self.mute_var.set(self._t.t("hotkey.none"))

    def _on_close(self) -> None:
        self._m.stop()
        try:
            import keyboard
            keyboard.clear_all_hotkeys()
        except Exception:
            pass
        self.destroy()
