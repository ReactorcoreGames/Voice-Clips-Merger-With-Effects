"""
Main GUI module for Voice Clips Merger With Effects (VCME).
Sets up ttkbootstrap window with 4-tab notebook layout.
"""

import sys
import webbrowser
from pathlib import Path
import ttkbootstrap as ttk

from config import APP_TITLE, APP_GEOMETRY, ICON_FILENAME
from config_manager import ConfigManager
from character_profiles import CharacterProfilesManager
from audio_generator import AudioGenerator
from gui_theme import apply_app_theme
from gui_tab1 import Tab1Builder
from gui_tab2 import Tab2Builder
from gui_tab3 import Tab3Builder
from gui_tab4 import Tab4Builder
from gui_handlers import GUIHandlers
from gui_generation import GenerationMixin


class VoiceClipsMergerGUI(Tab1Builder, Tab2Builder, Tab3Builder, Tab4Builder, GUIHandlers, GenerationMixin):
    """Main GUI application — 4-tab layout via multiple inheritance mixins."""

    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry(APP_GEOMETRY)
        self.root.state('zoomed')

        self._setup_icon()
        self._setup_window_theme()

        # Initialize backend components
        self.config_manager = ConfigManager()
        self.char_profiles = CharacterProfilesManager()
        self.audio_gen = AudioGenerator()

        # State
        self._current_clips_folder = None
        self._current_clip_list = None
        self._test_clip_paths = {}

        # Build UI
        self._build_ui()
        self._prefill_persisted_folders()

    def _setup_icon(self):
        """Setup application icon."""
        try:
            if getattr(sys, 'frozen', False):
                app_path = Path(sys.executable).parent
            else:
                app_path = Path(__file__).parent
            icon_path = app_path / ICON_FILENAME
            if icon_path.exists():
                self.root.iconbitmap(str(icon_path))
        except Exception as e:
            print(f"Could not load icon: {e}")

    def _setup_window_theme(self):
        """Setup dark title bar on Windows."""
        try:
            import ctypes
            HWND = ctypes.windll.user32.GetParent(self.root.winfo_id())
            DWMWA_USE_IMMERSIVE_DARK_MODE = 20
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                HWND, DWMWA_USE_IMMERSIVE_DARK_MODE,
                ctypes.byref(ctypes.c_int(1)), ctypes.sizeof(ctypes.c_int)
            )
        except Exception:
            pass

    def _prefill_persisted_folders(self):
        """Prefill output folder from last-used config values."""
        import os
        saved_output = self.config_manager.get_ui("last_output_folder")
        if saved_output and os.path.isdir(saved_output) and not self._gen_output_folder_var.get():
            self._gen_output_folder_var.set(saved_output)

        saved_name = self.config_manager.get_ui("last_project_name")
        if saved_name and not self._gen_project_name_var.get():
            self._gen_project_name_var.set(saved_name)

    def _build_ui(self):
        """Build the 4-tab notebook interface."""
        # Status bar at the bottom
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill="x", side="bottom", padx=5, pady=(0, 5))

        self.status_label = ttk.Label(status_frame, text="Ready",
                                      font=("Segoe UI", 9),
                                      foreground="#C090B8")
        self.status_label.pack(side="left")

        author_link = ttk.Label(status_frame,
                                text="Made by Reactorcore",
                                font=("Segoe UI", 9, "underline"),
                                foreground="#B040A0",
                                cursor="hand2")
        author_link.pack(side="right", padx=(0, 5))
        author_link.bind("<Button-1>",
                         lambda e: webbrowser.open("https://linktr.ee/reactorcore"))

        # Notebook container
        notebook_frame = ttk.Frame(self.root)
        notebook_frame.pack(fill="both", expand=True, padx=5, pady=(5, 0))

        self.notebook = ttk.Notebook(notebook_frame)
        self.notebook.pack(fill="both", expand=True)

        # Help button
        self._btn_help = ttk.Button(notebook_frame, text="Help",
                                    command=self.on_help,
                                    bootstyle="info-outline", width=8)
        self._btn_help.place(relx=1.0, rely=0.0, anchor="ne", x=-2, y=2)

        # Tab 1: Load Clips
        tab1_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab1_frame, text="  1. Load Clips  ")
        self.build_tab1(tab1_frame)

        # Tab 2: Effects
        tab2_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab2_frame, text="  2. Effects  ")
        self.build_tab2(tab2_frame)

        # Tab 3: Generate
        tab3_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab3_frame, text="  3. Generate  ")
        self.build_tab3(tab3_frame)

        # Tab 4: Settings
        tab4_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab4_frame, text="  4. Settings  ")
        self.build_tab4(tab4_frame)


def main():
    """Main entry point."""
    root = ttk.Window(themename="darkly")
    apply_app_theme(root)
    app = VoiceClipsMergerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
