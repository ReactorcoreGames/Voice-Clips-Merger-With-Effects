"""
Tab 4: Settings
Voice Clips Merger With Effects (VCME).
Pause gap, silence trim, output format/bitrate, effect tweaks, loudnorm target.
"""

import os
import subprocess
import sys
import tkinter as tk
import ttkbootstrap as ttk
from tkinter import ttk as _tk_ttk
from pathlib import Path
from ttkbootstrap.constants import *

from config import APP_THEME, VCME_SETTINGS_DEFAULTS, SILENCE_TRIM_DEFAULTS

try:
    from ttkbootstrap.tooltip import ToolTip
    _HAS_TOOLTIP = True
except ImportError:
    _HAS_TOOLTIP = False


def _tip(widget, text, position=None):
    if _HAS_TOOLTIP:
        try:
            kwargs = {"text": text, "delay": 400}
            if position:
                kwargs["position"] = position
            ToolTip(widget, **kwargs)
        except Exception:
            pass


class Tab4Builder:
    """Mixin class for building Tab 4 (Settings) UI."""

    def build_tab4(self, parent):
        """Build the complete Tab 4 interface."""
        canvas = ttk.Canvas(parent, background=APP_THEME["colors"]["inputbg_darker"])
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable = ttk.Frame(canvas, padding=15)

        scrollable.bind("<Configure>",
                        lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas_window = canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.bind("<Configure>",
                    lambda e: canvas.itemconfig(canvas_window, width=e.width))
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def bind_mousewheel_tab4(widget):
            widget.bind("<MouseWheel>", on_mousewheel)
            for child in widget.winfo_children():
                bind_mousewheel_tab4(child)

        canvas.bind("<MouseWheel>", on_mousewheel)
        scrollable.bind("<MouseWheel>", on_mousewheel)
        self._tab4_bind_mousewheel = bind_mousewheel_tab4

        ttk.Label(scrollable, text="Settings",
                  font=("Segoe UI", 18, "bold")).pack(pady=(0, 5))
        ttk.Label(scrollable,
                  text="Configure inter-clip pause, silence trimming, output format, and effect tweaks.",
                  font=("Segoe UI", 10), wraplength=900, justify="center").pack(pady=(0, 15))

        self._build_pause_section(scrollable)
        self._build_trim_section(scrollable)
        self._build_format_section(scrollable)
        self._build_tweaks_section(scrollable)
        self._build_quick_access_section(scrollable)

        bind_mousewheel_tab4(scrollable)

    # ── Section 1: Pause gap ────────────────────────────────────────────────

    def _build_pause_section(self, parent):
        frame = _tk_ttk.LabelFrame(parent, text="Pause Settings", padding=10)
        frame.pack(fill=X, pady=(0, 10))

        ttk.Label(frame,
                  text="Default silence gap inserted after each clip in the merged output. "
                       "Clips with a filename suffix like _1.0s override this per-clip.",
                  font=("Segoe UI", 10), foreground="#C090B8",
                  wraplength=880).pack(anchor=W, pady=(0, 8))

        row = ttk.Frame(frame)
        row.pack(anchor=W)

        ttk.Label(row, text="Default gap:", font=("Segoe UI", 10, "bold")).pack(side=LEFT, padx=(0, 8))

        gap_ms = self.config_manager.get_setting("default_gap_ms")
        self._gap_var = tk.IntVar(value=gap_ms)

        gap_scale = ttk.Scale(row, from_=0, to=10000, variable=self._gap_var,
                              orient=HORIZONTAL, length=300,
                              command=self._on_gap_changed)
        gap_scale.pack(side=LEFT, padx=(0, 8))
        _tip(gap_scale, "Range: 0 ms – 10000 ms, step 100 ms.\n"
                        "The gap added after every clip unless overridden by a _Xs filename suffix.")

        self._gap_label = ttk.Label(row, text=f"{gap_ms} ms",
                                    font=("Consolas", 10), width=8)
        self._gap_label.pack(side=LEFT)

        ttk.Label(frame,
                  text="Per-clip override: add _Xs or _X.Xs to the filename stem before the extension\n"
                       "  e.g. line01_@Alice_1.5s.wav → 1.5 s pause after that clip (up to 99999 s).\n"
                       "  The suffix-defined pause replaces (not adds to) the default gap.",
                  font=("Segoe UI", 9), foreground="#A870A0").pack(anchor=W, pady=(8, 0))

    def _on_gap_changed(self, val=None):
        raw = self._gap_var.get()
        snapped = int(round(raw / 100) * 100)
        snapped = max(0, min(10000, snapped))
        self._gap_var.set(snapped)
        self._gap_label.config(text=f"{snapped} ms")
        self.config_manager.set_setting("default_gap_ms", snapped)

    # ── Section 2: Silence trim ─────────────────────────────────────────────

    def _build_trim_section(self, parent):
        frame = _tk_ttk.LabelFrame(parent, text="Silence Trimming", padding=10)
        frame.pack(fill=X, pady=(0, 10))

        ttk.Label(frame,
                  text="Remove silence from clips before processing. Off by default — "
                       "real recordings often have intentional room tone that should be kept.",
                  font=("Segoe UI", 10), foreground="#C090B8",
                  wraplength=880).pack(anchor=W, pady=(0, 8))

        current_mode = self.config_manager.get_silence_trim("mode") or "off"
        self._silence_trim_mode_var = tk.StringVar(value=current_mode)

        modes = [
            ("off",            "Off  \u2190 default"),
            ("beginning",      "Start only  (strip head silence)"),
            ("end",            "End only  (strip tail silence)"),
            ("beginning_end",  "Start and End  (strip both)"),
            ("all",            "All  (strip head, tail, and mid-clip silence at \u221280 dB)"),
        ]

        for value, label in modes:
            rb = ttk.Radiobutton(frame, text=label,
                                 variable=self._silence_trim_mode_var, value=value,
                                 command=self._on_silence_trim_mode_changed,
                                 bootstyle="info")
            rb.pack(anchor=W, pady=1)

        _tip(frame,
             "Start/End trim: -35 dB threshold, 20 ms minimum silence duration.\n"
             "End trim uses the areverse sandwich — immune to mid-clip amplitude dips.\n"
             "All: additionally strips mid-clip silence at -80 dB (use with care on real recordings).")

        ttk.Button(frame, text="Reset to Default",
                   command=self._on_reset_silence_trim,
                   bootstyle="warning-outline", width=18).pack(anchor=W, pady=(10, 4))

    def _on_silence_trim_mode_changed(self):
        mode = self._silence_trim_mode_var.get()
        self.config_manager.set_silence_trim("mode", mode)

    def _on_reset_silence_trim(self):
        self.config_manager.reset_silence_trim_to_defaults()
        self._silence_trim_mode_var.set(SILENCE_TRIM_DEFAULTS["mode"])

    # ── Section 3: Output format ────────────────────────────────────────────

    def _build_format_section(self, parent):
        frame = _tk_ttk.LabelFrame(parent, text="Output Format", padding=10)
        frame.pack(fill=X, pady=(0, 10))

        fmt_val = self.config_manager.get_setting("output_format")
        bitrate_val = self.config_manager.get_setting("output_bitrate")
        lufs_val = self.config_manager.get_setting("loudnorm_lufs")

        self._format_var = tk.StringVar(value=fmt_val)
        self._bitrate_var = tk.StringVar(value=bitrate_val)
        self._lufs_var = tk.IntVar(value=lufs_val)

        # Format row
        fmt_row = ttk.Frame(frame)
        fmt_row.pack(anchor=W, pady=(0, 8))

        fmt_label = ttk.Label(fmt_row, text="Format:",
                              font=("Segoe UI", 10, "bold"))
        fmt_label.pack(side=LEFT, padx=(0, 8))
        _tip(fmt_label, "Recommended default: MP3.\nMP3 is universally compatible and keeps file sizes small.")

        formats = [("MP3", "mp3"), ("OGG", "ogg"), ("FLAC", "flac"),
                   ("WAV", "wav"), ("M4A (AAC)", "m4a")]
        for label, val in formats:
            rb = ttk.Radiobutton(fmt_row, text=label, value=val,
                                 variable=self._format_var,
                                 command=self._on_format_changed)
            rb.pack(side=LEFT, padx=(0, 8))

        # Lossless note
        self._lossless_note = ttk.Label(frame,
                                        text="Lossless formats produce large files.",
                                        font=("Consolas", 9), foreground="#FFD43B")

        # Bitrate row
        self._bitrate_frame = ttk.Frame(frame)
        self._bitrate_frame.pack(anchor=W, pady=(0, 8))

        bitrate_label = ttk.Label(self._bitrate_frame, text="Bitrate:",
                                  font=("Segoe UI", 10, "bold"))
        bitrate_label.pack(side=LEFT, padx=(0, 8))
        _tip(bitrate_label, "Recommended default: Standard (128k).\nMP3 128k is transparent for voice and keeps files compact.")

        bitrates = [
            ("Lo-fi (32k)", "32k"), ("Low (64k)", "64k"),
            ("Standard (128k)", "128k"), ("High (192k)", "192k"),
            ("Maximum (320k)", "320k"),
        ]
        for label, val in bitrates:
            rb = ttk.Radiobutton(self._bitrate_frame, text=label, value=val,
                                 variable=self._bitrate_var,
                                 command=lambda: self.config_manager.set_setting(
                                     "output_bitrate", self._bitrate_var.get()))
            rb.pack(side=LEFT, padx=(0, 8))

        # Loudnorm target row
        lufs_row = ttk.Frame(frame)
        lufs_row.pack(anchor=W)

        lufs_label = ttk.Label(lufs_row, text="Loudnorm target:",
                               font=("Segoe UI", 10, "bold"))
        lufs_label.pack(side=LEFT, padx=(0, 8))
        _tip(lufs_label, "LUFS target for the loudnorm merged output.\n"
                         "Streaming platforms typically target -14 LUFS.")

        lufs_options = [
            ("Broadcast (-23 LUFS)", -23), ("Podcast (-16 LUFS)", -16),
            ("Streaming (-14 LUFS)", -14), ("Loud (-11 LUFS)", -11),
        ]
        for label, val in lufs_options:
            ttk.Radiobutton(lufs_row, text=label, value=val,
                            variable=self._lufs_var,
                            command=lambda: self.config_manager.set_setting(
                                "loudnorm_lufs", self._lufs_var.get())
                            ).pack(side=LEFT, padx=(0, 8))

        # Init visibility
        self._on_format_changed()

    def _on_format_changed(self):
        fmt = self._format_var.get()
        self.config_manager.set_setting("output_format", fmt)
        lossy = fmt in ("mp3", "ogg", "m4a")
        if lossy:
            self._bitrate_frame.pack(anchor=W, pady=(0, 8))
            self._lossless_note.pack_forget()
        else:
            self._bitrate_frame.pack_forget()
            self._lossless_note.pack(anchor=W, pady=(0, 8))

    # ── Section 4: Effect tweaks ────────────────────────────────────────────

    def _build_tweaks_section(self, parent):
        frame = _tk_ttk.LabelFrame(parent, text="Audio Effect Tweaks", padding=10)
        frame.pack(fill=X, pady=(0, 10))

        ttk.Label(frame,
                  text="Tweak the intensity of some Tab 2 audio effects.",
                  font=("Segoe UI", 10), foreground="#C090B8",
                  wraplength=880).pack(anchor=W, pady=(0, 8))

        reverb_size = self.config_manager.get_setting("reverb_room_size")
        dist_drive = self.config_manager.get_setting("distortion_drive")
        noise_int = self.config_manager.get_setting("noise_intensity")

        self._reverb_room_var = tk.DoubleVar(value=float(reverb_size))
        self._distortion_drive_var = tk.DoubleVar(value=float(dist_drive))
        self._noise_intensity_var = tk.DoubleVar(value=float(noise_int))

        grid = ttk.Frame(frame)
        grid.pack(fill=X)

        def tweak_row(row_idx, label_text, var, key, tip_text, lo=0.0, hi=1.0,
                      left_label="", right_label=""):
            lbl = ttk.Label(grid, text=label_text, font=("Segoe UI", 10, "bold"),
                            width=22, anchor=W)
            lbl.grid(row=row_idx, column=0, sticky=W, pady=4, padx=(0, 8))
            _tip(lbl, tip_text)

            if left_label:
                ttk.Label(grid, text=left_label,
                          font=("Segoe UI", 9),
                          foreground="#A870A0").grid(row=row_idx, column=1, sticky=E, padx=(0, 4))

            scale = ttk.Scale(grid, from_=lo, to=hi, variable=var,
                              orient=HORIZONTAL, length=300,
                              command=lambda v, k=key, dv=var: self._on_tweak_changed(k, dv))
            scale.grid(row=row_idx, column=2, sticky=EW, padx=4)

            if right_label:
                ttk.Label(grid, text=right_label,
                          font=("Segoe UI", 9),
                          foreground="#A870A0").grid(row=row_idx, column=3, sticky=W, padx=(4, 0))

            val_lbl = ttk.Label(grid, text=f"{var.get():.2f}",
                                font=("Segoe UI", 10), width=6)
            val_lbl.grid(row=row_idx, column=4, sticky=W)
            var._val_label = val_lbl
            var._key = key

        tweak_row(0, "Reverb — Room size", self._reverb_room_var,
                  "reverb_room_size",
                  "Controls reverb wetness/decay across all reverb presets.\n"
                  "Left = smaller/drier, Right = larger/wetter.",
                  left_label="Small", right_label="Large")

        tweak_row(1, "Distortion — Grit", self._distortion_drive_var,
                  "distortion_drive",
                  "Controls drive/overdrive amount across all distortion presets.\n"
                  "Left = lighter, Right = heavier.",
                  left_label="Light", right_label="Heavy")

        tweak_row(2, "Noise intensity", self._noise_intensity_var,
                  "noise_intensity",
                  "Controls the volume of Add Noise (White/Pink/Brown) across all speaker panels.\n"
                  "Left = subtle, Right = prominent.",
                  left_label="Subtle", right_label="Prominent")

        grid.columnconfigure(2, weight=1)

    def _on_tweak_changed(self, key, var):
        raw = var.get()
        rounded = round(raw, 2)
        var.set(rounded)
        if hasattr(var, '_val_label'):
            var._val_label.config(text=f"{rounded:.2f}")
        self.config_manager.set_setting(key, rounded)

    # ── Quick access ────────────────────────────────────────────────────────

    def _build_quick_access_section(self, parent):
        frame = _tk_ttk.LabelFrame(parent, text="Quick Access", padding=10)
        frame.pack(fill=X, pady=(0, 10))

        ttk.Label(frame, text="Open data files.",
                  font=("Segoe UI", 10), foreground="#C090B8").pack(anchor=W, pady=(0, 8))

        row = ttk.Frame(frame)
        row.pack(anchor=W)

        buttons = [
            ("character_profiles.json", lambda: self.char_profiles.open_in_editor()),
            ("config.json", lambda: self._open_path(self.config_manager.path)),
        ]
        for label, cmd in buttons:
            ttk.Button(row, text=label, command=cmd,
                       bootstyle="secondary").pack(side=LEFT, padx=(0, 8))

    def _open_path(self, path):
        """Open a file or folder in the system default handler."""
        try:
            if sys.platform == "win32":
                os.startfile(str(path))
            elif sys.platform == "darwin":
                subprocess.run(["open", str(path)])
            else:
                subprocess.run(["xdg-open", str(path)])
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Error", f"Could not open:\n{path}\n\n{e}")
