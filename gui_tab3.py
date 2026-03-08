"""
Tab 3: Generate
Voice Clips Merger With Effects (VCME).
Project name, output folder, generate button, progress, log.
"""

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from config import APP_THEME, MAX_PROJECT_NAME_LENGTH, INVALID_FILENAME_CHARS


class Tab3Builder:
    """Mixin class for building Tab 3 (Generate) UI."""

    def build_tab3(self, parent):
        """Build the complete Tab 3 interface."""
        self._gen_project_name_var = tk.StringVar(value="")
        self._gen_output_folder_var = tk.StringVar(value="")
        self._gen_progress_var = tk.DoubleVar(value=0.0)
        self._gen_running = False
        self._gen_cancel_requested = False

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

        def bind_mousewheel_tab3(widget):
            widget.bind("<MouseWheel>", on_mousewheel)
            for child in widget.winfo_children():
                bind_mousewheel_tab3(child)

        canvas.bind("<MouseWheel>", on_mousewheel)
        scrollable.bind("<MouseWheel>", on_mousewheel)
        self._tab3_bind_mousewheel = bind_mousewheel_tab3

        ttk.Label(scrollable, text="Generate Output",
                  font=("Segoe UI", 18, "bold")).pack(pady=(0, 5))
        ttk.Label(scrollable,
                  text="Set a project name and output folder, then generate.",
                  font=("Segoe UI", 10), wraplength=900, justify="center").pack(pady=(0, 15))

        self._build_project_config_section(scrollable)
        self._build_generation_controls(scrollable)
        self._build_generation_log(scrollable)

        bind_mousewheel_tab3(scrollable)

    def _build_project_config_section(self, parent):
        """Build project name and output folder configuration."""
        frame = ttk.LabelFrame(parent, text="Project Configuration", padding=10)
        frame.pack(fill=X, pady=(0, 10))

        name_row = ttk.Frame(frame)
        name_row.pack(fill=X, pady=(0, 8))

        ttk.Label(name_row, text="Project Name:",
                  font=("Segoe UI", 10, "bold")).pack(side=LEFT, padx=(0, 5))

        name_entry = ttk.Entry(name_row, textvariable=self._gen_project_name_var,
                               width=30, font=("Consolas", 10))
        name_entry.pack(side=LEFT, padx=(0, 5))

        self._project_name_status = ttk.Label(name_row, text="",
                                              font=("Segoe UI", 9))
        self._project_name_status.pack(side=LEFT, padx=(5, 0))

        ttk.Label(name_row, text=f"(max {MAX_PROJECT_NAME_LENGTH} chars)",
                  font=("Segoe UI", 9), foreground="#C090B8").pack(side=LEFT, padx=(10, 0))

        self._gen_project_name_var.trace_add("write", self._on_project_name_changed)

        folder_row = ttk.Frame(frame)
        folder_row.pack(fill=X)

        ttk.Label(folder_row, text="Output Folder:",
                  font=("Segoe UI", 10, "bold")).pack(side=LEFT, padx=(0, 5))

        ttk.Entry(folder_row, textvariable=self._gen_output_folder_var,
                  width=50, state="readonly",
                  font=("Consolas", 9)).pack(side=LEFT, fill=X, expand=True, padx=(0, 5))

        ttk.Button(folder_row, text="Browse...",
                   command=self._on_pick_output_folder,
                   bootstyle=INFO, width=10).pack(side=LEFT)

    def _build_generation_controls(self, parent):
        """Build generate/cancel buttons and progress bar."""
        frame = ttk.LabelFrame(parent, text="Generation", padding=10)
        frame.pack(fill=X, pady=(0, 10))

        btn_row = ttk.Frame(frame)
        btn_row.pack(fill=X, pady=(0, 8))

        self._btn_generate = ttk.Button(btn_row, text="Generate All",
                                        command=self._on_generate_clicked,
                                        bootstyle=SUCCESS, width=20)
        self._btn_generate.pack(side=LEFT, padx=(0, 10))

        self._btn_cancel = ttk.Button(btn_row, text="Cancel",
                                      command=self._on_cancel_clicked,
                                      bootstyle=DANGER, width=12,
                                      state="disabled")
        self._btn_cancel.pack(side=LEFT, padx=(0, 10))

        self._btn_open_output = ttk.Button(btn_row, text="Open Output Folder",
                                           command=self._on_open_output_folder,
                                           bootstyle=INFO, width=20,
                                           state="disabled")
        self._btn_open_output.pack(side=RIGHT)

        self._progress_bar = ttk.Progressbar(frame, variable=self._gen_progress_var,
                                             maximum=100, mode="determinate",
                                             bootstyle=SUCCESS)
        self._progress_bar.pack(fill=X, pady=(0, 3))

        self._progress_label = ttk.Label(frame, text="Ready",
                                         font=("Segoe UI", 9),
                                         foreground="#C090B8")
        self._progress_label.pack(anchor=W)

    def _build_generation_log(self, parent):
        """Build the scrolling generation log."""
        frame = ttk.LabelFrame(parent, text="Generation Log", padding=10)
        frame.pack(fill=BOTH, expand=True, pady=(0, 10))

        log_container = ttk.Frame(frame)
        log_container.pack(fill=BOTH, expand=True)

        log_scrollbar = ttk.Scrollbar(log_container, orient="vertical")
        self._gen_log = tk.Text(log_container, height=18, wrap="word",
                                font=("Consolas", 9),
                                bg=APP_THEME["colors"]["inputbg"],
                                fg=APP_THEME["colors"]["inputfg"],
                                relief="flat", borderwidth=1,
                                state="disabled",
                                yscrollcommand=log_scrollbar.set,
                                selectbackground=APP_THEME["colors"]["selectbg"])
        log_scrollbar.config(command=self._gen_log.yview)

        self._gen_log.pack(side=LEFT, fill=BOTH, expand=True)
        log_scrollbar.pack(side=RIGHT, fill=Y)

        self._gen_log.tag_configure("error", foreground="#FF6B6B")
        self._gen_log.tag_configure("success", foreground="#69DB7C")
        self._gen_log.tag_configure("info", foreground="#74C0FC")
        self._gen_log.tag_configure("warning", foreground="#FFD43B")
        self._gen_log.tag_configure("header", foreground="#A0C8FF",
                                    font=("Consolas", 9, "bold"))

    # ── Project name validation ─────────────────────────────────────────────

    def _on_project_name_changed(self, *args):
        """Validate project name in real-time."""
        name = self._gen_project_name_var.get()
        if not name:
            self._project_name_status.config(text="", foreground="#C090B8")
            return
        if len(name) > MAX_PROJECT_NAME_LENGTH:
            self._project_name_status.config(
                text=f"Too long ({len(name)}/{MAX_PROJECT_NAME_LENGTH})",
                foreground="#FF6B6B")
            return
        bad_chars = [ch for ch in name if ch in INVALID_FILENAME_CHARS]
        if bad_chars:
            self._project_name_status.config(
                text=f"Invalid chars: {', '.join(repr(c) for c in bad_chars)}",
                foreground="#FF6B6B")
            return
        self._project_name_status.config(
            text=f"OK ({len(name)}/{MAX_PROJECT_NAME_LENGTH})",
            foreground="#69DB7C")

    # ── Generation log helpers ──────────────────────────────────────────────

    def gen_log(self, message, tag=None):
        """Append a message to the generation log."""
        self._gen_log.config(state="normal")
        if tag:
            self._gen_log.insert("end", message + "\n", tag)
        else:
            self._gen_log.insert("end", message + "\n")
        self._gen_log.see("end")
        self._gen_log.config(state="disabled")
        self.root.update_idletasks()

    def gen_log_clear(self):
        """Clear the generation log."""
        self._gen_log.config(state="normal")
        self._gen_log.delete("1.0", "end")
        self._gen_log.config(state="disabled")

    def gen_progress(self, value, label_text=None):
        """Update generation progress bar and label."""
        self._gen_progress_var.set(value)
        if label_text:
            self._progress_label.config(text=label_text)
        self.root.update_idletasks()
