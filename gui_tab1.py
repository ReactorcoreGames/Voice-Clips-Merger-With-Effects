"""
Tab 1: Load Clips
Voice Clips Merger With Effects (VCME)
"""

import tkinter as tk
from tkinter import scrolledtext
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from config import APP_THEME


class Tab1Builder:
    """Mixin class for building Tab 1 (Load Clips) UI."""

    def build_tab1(self, parent):
        """Build the complete Tab 1 interface."""
        # Main scrollable container
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

        def bind_mousewheel(widget):
            widget.bind("<MouseWheel>", on_mousewheel)
            for child in widget.winfo_children():
                bind_mousewheel(child)

        canvas.bind("<MouseWheel>", on_mousewheel)
        scrollable.bind("<MouseWheel>", on_mousewheel)

        self._tab1_canvas = canvas
        self._tab1_bind_mousewheel = bind_mousewheel

        # --- Title ---
        ttk.Label(scrollable, text="Load Clips",
                  font=("Segoe UI", 18, "bold")).pack(pady=(0, 5))
        ttk.Label(scrollable,
                  text="Select a folder of audio clips. Files are ordered alphanumerically. "
                       "Use @Speaker_ prefix in filenames to assign per-speaker effects.",
                  wraplength=900, justify="center",
                  font=("Segoe UI", 10)).pack(pady=(0, 15))

        # --- Folder picker ---
        folder_frame = ttk.LabelFrame(scrollable, text="Clips Folder", padding=10)
        folder_frame.pack(fill=X, pady=(0, 10))

        btn_row = ttk.Frame(folder_frame)
        btn_row.pack(fill=X, pady=5)

        self.btn_load_folder = ttk.Button(btn_row, text="Open Clips Folder...",
                                          command=self.on_load_folder,
                                          bootstyle=PRIMARY, width=22)
        self.btn_load_folder.pack(side=LEFT, padx=(0, 10))

        self.btn_reload_folder = ttk.Button(btn_row, text="Reload Folder",
                                            command=self.on_reload_folder,
                                            bootstyle=INFO, width=16,
                                            state="disabled")
        self.btn_reload_folder.pack(side=LEFT, padx=(0, 10))

        self._clips_folder_var = tk.StringVar()
        self.loaded_folder_label = ttk.Label(folder_frame,
                                             textvariable=self._clips_folder_var,
                                             text="No folder loaded",
                                             font=("Segoe UI", 9),
                                             foreground="#A870A0")
        self.loaded_folder_label.pack(anchor=W, pady=(0, 5))

        # --- Clip list ---
        list_outer = ttk.LabelFrame(scrollable, text="Clip List", padding=10)
        list_outer.pack(fill=BOTH, expand=True, pady=(0, 10))

        # Enable/Disable All row
        toggle_row = ttk.Frame(list_outer)
        toggle_row.pack(fill=X, pady=(0, 5))

        self._include_all_var = tk.BooleanVar(value=True)
        self._include_all_check = ttk.Checkbutton(
            toggle_row, text="Enable All / Disable All",
            variable=self._include_all_var,
            command=self._on_include_all_toggle,
            bootstyle="success-round-toggle"
        )
        self._include_all_check.pack(side=LEFT)

        self._clip_count_label = ttk.Label(toggle_row, text="",
                                           font=("Segoe UI", 9), foreground="#A870A0")
        self._clip_count_label.pack(side=RIGHT)

        # Scrollable clip list frame
        list_container = ttk.Frame(list_outer,
                                   relief="flat",
                                   style="TFrame")
        list_container.pack(fill=BOTH, expand=True)

        clip_canvas = tk.Canvas(list_container,
                                bg=APP_THEME["colors"]["inputbg"],
                                highlightthickness=0)
        clip_scrollbar = ttk.Scrollbar(list_container, orient="vertical",
                                       command=clip_canvas.yview)
        self._clip_list_frame = ttk.Frame(clip_canvas)

        self._clip_list_frame.bind(
            "<Configure>",
            lambda e: clip_canvas.configure(scrollregion=clip_canvas.bbox("all"))
        )
        clip_canvas_window = clip_canvas.create_window(
            (0, 0), window=self._clip_list_frame, anchor="nw"
        )
        clip_canvas.bind(
            "<Configure>",
            lambda e: clip_canvas.itemconfig(clip_canvas_window, width=e.width)
        )
        clip_canvas.configure(yscrollcommand=clip_scrollbar.set, height=250)

        clip_canvas.pack(side=LEFT, fill=BOTH, expand=True)
        clip_scrollbar.pack(side=RIGHT, fill=Y)

        # Forward mousewheel to the clip canvas
        def on_clip_mousewheel(event):
            clip_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        clip_canvas.bind("<MouseWheel>", on_clip_mousewheel)
        self._clip_list_frame.bind("<MouseWheel>", on_clip_mousewheel)
        self._clip_canvas = clip_canvas
        self._on_clip_mousewheel = on_clip_mousewheel

        # Storage for per-clip checkbox vars and entries
        self._clip_vars = []   # list of (tk.BooleanVar, ClipEntry index)
        self._clip_rows = []   # list of ttk.Frame for each row

        # --- Parse log ---
        log_frame = ttk.LabelFrame(scrollable, text="Folder Log", padding=10)
        log_frame.pack(fill=BOTH, expand=True, pady=(0, 10))

        self.parse_log = scrolledtext.ScrolledText(
            log_frame, height=8,
            font=("Consolas", 9),
            bg=APP_THEME["colors"]["inputbg"],
            fg=APP_THEME["colors"]["inputfg"],
            insertbackground=APP_THEME["colors"]["inputfg"],
            relief="flat", borderwidth=1,
            state='disabled', wrap='word'
        )
        self.parse_log.pack(fill=BOTH, expand=True)

        self.parse_log.tag_configure("error", foreground="#FF6B6B")
        self.parse_log.tag_configure("success", foreground="#69DB7C")
        self.parse_log.tag_configure("info", foreground="#74C0FC")
        self.parse_log.tag_configure("warning", foreground="#FFD43B")
        self.parse_log.tag_configure("header",
                                     foreground=APP_THEME["colors"]["accent"],
                                     font=("Segoe UI", 10, "bold"))

        # --- Continue button ---
        nav_frame = ttk.Frame(scrollable)
        nav_frame.pack(fill=X, pady=(5, 10))

        self.btn_continue_to_tab2 = ttk.Button(
            nav_frame, text="Continue to Effects  >>",
            command=self.on_continue_to_tab2,
            bootstyle=SUCCESS, width=28,
            state="disabled"
        )
        self.btn_continue_to_tab2.pack(side=RIGHT)

        bind_mousewheel(scrollable)

    # ── Log helpers ────────────────────────────────────────────────────────────

    def log_message(self, text, tag=None):
        """Append a message to the parse log."""
        self.parse_log.config(state='normal')
        if tag:
            self.parse_log.insert('end', text + '\n', tag)
        else:
            self.parse_log.insert('end', text + '\n')
        self.parse_log.see('end')
        self.parse_log.config(state='disabled')

    def clear_log(self):
        """Clear the parse log."""
        self.parse_log.config(state='normal')
        self.parse_log.delete('1.0', 'end')
        self.parse_log.config(state='disabled')

    # ── Clip list population ───────────────────────────────────────────────────

    def populate_clip_list(self, clip_list):
        """
        Populate the scrollable clip list from a ClipList object.
        Called after folder is loaded/reloaded.
        """
        # Clear existing rows
        for row in self._clip_rows:
            row.destroy()
        self._clip_rows.clear()
        self._clip_vars.clear()

        if not clip_list or not clip_list.clips:
            self._clip_count_label.config(text="0 clips")
            return

        for idx, clip in enumerate(clip_list.clips):
            var = tk.BooleanVar(value=clip.included)
            self._clip_vars.append((var, idx))

            row = ttk.Frame(self._clip_list_frame, padding=(4, 1))
            row.pack(fill=X)
            self._clip_rows.append(row)

            # Alternating row backgrounds
            bg = APP_THEME["colors"]["inputbg"] if idx % 2 == 0 else APP_THEME["colors"]["bg"]
            row.configure(style="TFrame")

            cb = ttk.Checkbutton(
                row, variable=var,
                command=lambda v=var, i=idx: self._on_clip_toggle(v, i),
                bootstyle="success-round-toggle"
            )
            cb.pack(side=LEFT, padx=(0, 6))

            # Speaker badge (shown in grouped mode)
            if clip_list.is_grouped:
                speaker_text = f"[{clip.speaker_id}]" if clip.speaker_id else "[Ungrouped]"
                ttk.Label(row, text=speaker_text,
                          font=("Segoe UI", 9),
                          foreground=APP_THEME["colors"]["accent"],
                          width=14).pack(side=LEFT, padx=(0, 6))

            # Filename
            ttk.Label(row, text=clip.filename,
                      font=("Consolas", 9)).pack(side=LEFT)

            # Pause suffix note
            if clip.pause_after_s > 0:
                pause_text = f"+{clip.pause_after_s:.1f}s pause after"
                ttk.Label(row, text=pause_text,
                          font=("Segoe UI", 8),
                          foreground="#A870A0").pack(side=RIGHT, padx=(0, 4))

            # Bind mousewheel to each row
            row.bind("<MouseWheel>", self._on_clip_mousewheel)
            for child in row.winfo_children():
                child.bind("<MouseWheel>", self._on_clip_mousewheel)

        total = len(clip_list.clips)
        self._clip_count_label.config(text=f"{total} clip{'s' if total != 1 else ''}")
        self._sync_include_all_state()

    def _on_clip_toggle(self, var, clip_index):
        """Update the ClipEntry.included when checkbox is toggled."""
        if hasattr(self, '_current_clip_list') and self._current_clip_list:
            self._current_clip_list.clips[clip_index].included = var.get()
        self._sync_include_all_state()

    def _on_include_all_toggle(self):
        """Enable or disable all clips at once."""
        state = self._include_all_var.get()
        for var, idx in self._clip_vars:
            var.set(state)
            if hasattr(self, '_current_clip_list') and self._current_clip_list:
                self._current_clip_list.clips[idx].included = state

    def _sync_include_all_state(self):
        """Sync the Enable All checkbox to reflect actual clip states."""
        if not self._clip_vars:
            return
        all_on = all(v.get() for v, _ in self._clip_vars)
        # Suppress command trigger by temporarily removing command
        self._include_all_var.set(all_on)
