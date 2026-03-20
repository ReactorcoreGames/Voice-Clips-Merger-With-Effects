"""
Event handlers for Voice Clips Merger With Effects (VCME).
Tab 1: folder loading, clip toggling, navigation.
Tab 2: test clip picking/running, navigation.
Tab 3: output folder, generate/cancel/open.
"""

import os
import subprocess
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

import ttkbootstrap as ttk

import re

from config import INVALID_FILENAME_CHARS
from clip_manager import scan_folder


class GUIHandlers:
    """Mixin class containing event handlers."""

    # ── Tab 1 handlers ───────────────────────────────────────────────────────

    def on_load_folder(self):
        """Handle 'Open Clips Folder' button click."""
        initial_dir = self.config_manager.get_ui("last_clips_folder")
        if not initial_dir or not os.path.isdir(initial_dir):
            initial_dir = os.getcwd()

        folder = filedialog.askdirectory(
            title="Select Clips Folder",
            initialdir=initial_dir,
        )
        if not folder:
            return

        self.config_manager.set_ui("last_clips_folder", folder)
        self._current_clips_folder = folder
        self._run_folder_scan(folder)

    def on_reload_folder(self):
        """Handle 'Reload Folder' button click."""
        folder = getattr(self, '_current_clips_folder', None)
        if folder:
            self._run_folder_scan(folder)
        else:
            messagebox.showinfo("No Folder", "No clips folder has been loaded yet.")

    def _run_folder_scan(self, folder_path):
        """Scan the folder and update the UI."""
        self.clear_log()

        self._clips_folder_var.set(folder_path)
        self.log_message(f"Scanning: {folder_path}", "header")
        self.log_message("-" * 60)

        default_gap_s = self.config_manager.get_setting("default_gap_ms") / 1000.0
        clip_list = scan_folder(folder_path, default_gap_s=default_gap_s)
        self._current_clip_list = clip_list

        # Log results
        total = len(clip_list.clips)
        if total == 0:
            self.log_message("No supported audio files found in this folder.", "warning")
        else:
            self.log_message(f"Found {total} audio clip(s).", "success")

        if clip_list.is_grouped:
            self.log_message(
                f"Grouped mode: {len(clip_list.speakers)} speaker(s) detected: "
                f"{', '.join(clip_list.speakers)}",
                "info"
            )
            has_ungrouped = any(c.speaker_id == "" for c in clip_list.clips)
            if has_ungrouped:
                self.log_message("  + Ungrouped (files without @Speaker_ prefix)", "info")
        else:
            self.log_message("Global mode: no @Speaker_ prefixes detected. "
                             "A single effect panel will apply to all clips.", "info")

        if clip_list.skipped_files:
            self.log_message(
                f"{len(clip_list.skipped_files)} file(s) skipped (unsupported format): "
                + ", ".join(clip_list.skipped_files[:5])
                + (" ..." if len(clip_list.skipped_files) > 5 else ""),
                "warning"
            )

        # Parse pause suffixes
        suffix_clips = [c for c in clip_list.clips if c.pause_after_s > 0]
        if suffix_clips and default_gap_s == 0:
            self.log_message(
                f"{len(suffix_clips)} clip(s) have pause suffix overrides.", "info"
            )

        # Populate clip list and Tab 2
        self.populate_clip_list(clip_list)
        self.populate_tab2_speakers(clip_list)

        # Enable buttons
        self.btn_reload_folder.config(state="normal")
        if total > 0:
            self.btn_continue_to_tab2.config(state="normal")

        # Prefill project name from folder name
        folder_name = Path(folder_path).name
        sanitized = re.sub(
            f"[{''.join(re.escape(c) for c in INVALID_FILENAME_CHARS)}]", "_", folder_name
        )
        sanitized = re.sub(r"[\s_]+", "_", sanitized).strip("_")[:20]
        if sanitized and not self._gen_project_name_var.get():
            self._gen_project_name_var.set(sanitized)

    def on_continue_to_tab2(self):
        """Navigate to Tab 2."""
        self.notebook.select(1)

    def on_help(self):
        """Open README in the system default editor."""
        if getattr(sys, 'frozen', False):
            app_path = Path(sys.executable).parent
        else:
            app_path = Path(__file__).parent
        readme_path = app_path / "README.md"
        if not readme_path.exists():
            messagebox.showinfo("Help",
                                "README.md not found.\n\n"
                                "Quick start:\n"
                                "  1. Tab 1 — Open a folder of audio clips\n"
                                "  2. Tab 2 — Set effects per speaker\n"
                                "  3. Tab 3 — Generate processed clips and merged output")
            return
        try:
            if sys.platform == 'win32':
                os.startfile(str(readme_path))
            elif sys.platform == 'darwin':
                subprocess.run(["open", str(readme_path)])
            else:
                subprocess.run(["xdg-open", str(readme_path)])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open README: {e}")

    # ── Tab 2 handlers ───────────────────────────────────────────────────────

    def on_pick_test_clip(self, speaker_id):
        """Pick a test clip for a speaker panel."""
        initial_dir = getattr(self, '_current_clips_folder', None) or os.getcwd()

        filepath = filedialog.askopenfilename(
            title="Select Test Clip",
            initialdir=initial_dir,
            filetypes=[
                ("Audio files", "*.mp3 *.wav *.ogg *.flac *.m4a *.aiff *.aif"),
                ("All files", "*.*"),
            ]
        )
        if not filepath:
            return

        widgets = self._speaker_widgets.get(speaker_id, {})
        test_clip_var = widgets.get("test_clip_var")
        if test_clip_var:
            test_clip_var.set(Path(filepath).name)
            # Store full path in _test_clip_paths dict
            if not hasattr(self, '_test_clip_paths'):
                self._test_clip_paths = {}
            self._test_clip_paths[speaker_id] = filepath

    def on_test_clip(self, speaker_id):
        """Process and play the selected test clip with current effects."""
        if not hasattr(self, '_test_clip_paths') or speaker_id not in self._test_clip_paths:
            messagebox.showwarning("No Test Clip",
                                   f"Pick a test clip for {speaker_id} first.")
            return

        clip_path = self._test_clip_paths[speaker_id]
        if not Path(clip_path).exists():
            messagebox.showwarning("File Not Found",
                                   f"Test clip not found:\n{clip_path}")
            return

        vars_dict = self._speaker_vars.get(speaker_id, {})
        if not vars_dict:
            return

        # Gather effect settings
        from gui_tab2 import _EFFECT_ORDER
        effect_settings = {}
        for effect_name in _EFFECT_ORDER:
            effect_settings[effect_name] = vars_dict.get(effect_name, tk.StringVar()).get() if effect_name in vars_dict else "off"
        effect_settings["fmsu"] = vars_dict["fmsu"].get()
        effect_settings["reverse"] = vars_dict["reverse"].get()
        effect_settings["pitch_shift"] = vars_dict["pitch_multiplier"].get() / 100.0

        # Inject tweak settings
        effect_settings["_reverb_room_size"] = self.config_manager.get_setting("reverb_room_size")
        effect_settings["_distortion_drive"] = self.config_manager.get_setting("distortion_drive")
        effect_settings["_noise_intensity"] = self.config_manager.get_setting("noise_intensity")

        output_format = self.config_manager.get_setting("output_format")
        output_bitrate = self.config_manager.get_setting("output_bitrate")
        silence_trim_mode = self.config_manager.get_silence_trim("mode") or "off"

        if hasattr(self, 'status_label'):
            self.status_label.config(text=f"Processing test clip for {speaker_id}...")

        def process():
            try:
                from audio_generator import AudioGenerator
                from file_manager import FileManager

                audio_gen = AudioGenerator()
                test_dir = FileManager.get_test_output_dir()
                ext = "." + output_format
                out_path = test_dir / f"test_{speaker_id}{ext}"

                if out_path.exists():
                    try:
                        out_path.rename(out_path)
                    except PermissionError:
                        self.root.after(0, lambda: messagebox.showwarning(
                            "File In Use",
                            "The previous test clip is still open in your media player.\n\n"
                            "Close or stop it, then click Test again."))
                        return

                success, error = audio_gen.apply_audio_effects(
                    clip_path, str(out_path),
                    effect_settings,
                    config_manager=self.config_manager,
                    silence_trim_mode=silence_trim_mode,
                    output_format=output_format,
                    output_bitrate=output_bitrate,
                )

                if success:
                    success, error = audio_gen.apply_peak_normalize(str(out_path), str(out_path))

                if success:
                    self.root.after(0, lambda p=str(out_path): self._on_test_clip_done(speaker_id, p, None))
                else:
                    self.root.after(0, lambda: self._on_test_clip_done(speaker_id, None, error))

            except Exception as e:
                self.root.after(0, lambda: self._on_test_clip_done(speaker_id, None, str(e)))

        threading.Thread(target=process, daemon=True).start()

    def _on_test_clip_done(self, speaker_id, filepath, error):
        """Callback when test clip processing completes."""
        if error:
            messagebox.showerror("Test Clip Error",
                                 f"Failed to process test clip for {speaker_id}:\n\n{error}")
            if hasattr(self, 'status_label'):
                self.status_label.config(text=f"Test clip failed for {speaker_id}.")
        else:
            if hasattr(self, 'status_label'):
                self.status_label.config(text=f"Test clip ready: {filepath}")
            try:
                if sys.platform == 'win32':
                    os.startfile(filepath)
                elif sys.platform == 'darwin':
                    subprocess.run(["open", filepath])
                else:
                    subprocess.run(["xdg-open", filepath])
            except Exception:
                pass

    def on_continue_to_tab3(self):
        """Navigate to Tab 3."""
        self.notebook.select(2)

    # ── Tab 3 handlers ───────────────────────────────────────────────────────

    def _on_pick_output_folder(self):
        """Handle output folder selection for generation."""
        initial_dir = self.config_manager.get_ui("last_output_folder")
        if not initial_dir or not os.path.isdir(initial_dir):
            initial_dir = os.getcwd()

        folder = filedialog.askdirectory(
            title="Select Output Folder",
            initialdir=initial_dir,
        )
        if folder:
            self._gen_output_folder_var.set(folder)
            self.config_manager.set_ui("last_output_folder", folder)

    def _on_generate_clicked(self):
        """Handle 'Generate All' button click."""
        from config import MAX_PROJECT_NAME_LENGTH

        clip_list = getattr(self, '_current_clip_list', None)
        included = [c for c in clip_list.clips if c.included] if clip_list else []
        if not included:
            messagebox.showwarning("No Clips",
                                   "No clips are included.\n"
                                   "Load a folder in Tab 1 and enable at least one clip.")
            return

        project_name = self._gen_project_name_var.get().strip()
        if not project_name:
            messagebox.showwarning("Project Name", "Enter a project name before generating.")
            return

        if len(project_name) > MAX_PROJECT_NAME_LENGTH:
            messagebox.showwarning("Project Name",
                                   f"Project name exceeds {MAX_PROJECT_NAME_LENGTH} characters.")
            return

        bad_chars = [ch for ch in project_name if ch in INVALID_FILENAME_CHARS]
        if bad_chars:
            messagebox.showwarning("Project Name",
                                   f"Project name contains invalid characters: "
                                   f"{', '.join(repr(c) for c in bad_chars)}")
            return

        output_folder = self._gen_output_folder_var.get().strip()
        if not output_folder:
            messagebox.showwarning("Output Folder", "Select an output folder before generating.")
            return

        confirm = messagebox.askyesno(
            "Start Generation",
            f"Process {len(included)} clip(s) and merge them?\n\n"
            f"Project: {project_name}\n"
            f"Output: {output_folder}\n\n"
            f"This may take a moment."
        )
        if not confirm:
            return

        self.run_generation()

    def _on_cancel_clicked(self):
        """Handle 'Cancel' button click during generation."""
        self._gen_cancel_requested = True
        self._btn_cancel.config(state="disabled")
        self.gen_log("Cancellation requested... finishing current clip.", "warning")

    def _on_open_output_folder(self):
        """Open the output folder in the system file manager."""
        folder = getattr(self, '_last_resolved_output_folder', None) or \
                 self._gen_output_folder_var.get().strip()
        if not folder or not os.path.isdir(folder):
            messagebox.showinfo("No Folder", "Output folder does not exist yet.")
            return

        try:
            if sys.platform == 'win32':
                os.startfile(folder)
            elif sys.platform == 'darwin':
                subprocess.run(["open", folder])
            else:
                subprocess.run(["xdg-open", folder])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open folder: {e}")
