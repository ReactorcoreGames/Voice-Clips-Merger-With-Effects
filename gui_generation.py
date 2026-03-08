"""
Audio generation orchestration for Voice Clips Merger With Effects (VCME).
Handles: apply effects per clip → clips_effect/, merge → merged outputs, reference sheet.
Runs in a background thread with progress callbacks to the GUI.
"""

import threading
import traceback
from datetime import datetime
from pathlib import Path

from audio_generator import AudioGenerator
from audio_merger import AudioMerger
from clip_manager import get_included_clips
from file_manager import FileManager
from gui_tab2 import _EFFECT_ORDER


_EFFECT_ABBREV = {
    "radio":          "RAD",
    "reverb":         "RVB",
    "distortion":     "DIST",
    "telephone":      "TEL",
    "robot_voice":    "ROBO",
    "cheap_mic":      "CHP",
    "underwater":     "UNDR",
    "megaphone":      "MEGA",
    "worn_tape":      "TAPE",
    "intercom":       "ICOM",
    "alien":          "ALN",
    "cave":           "CAVE",
    "inner_thoughts": "ITH",
    "add_noise":      "NOIS",
}

_VARIANT_REMAP = {
    "alien": {"insectoid": "insect", "dimensional": "dim.", "warble": "warble"},
    "inner_thoughts": {"Dissociated": "dissoc.", "Whisper": "whisper", "Dreamlike": "dreamlike"},
}


def _build_effect_tag_string(effect_settings):
    """
    Build a compact effect tag string for the reference sheet.
    e.g. "[RAD:medium, RVB:mild, FMSU]" or "" if no active effects.
    """
    parts = []
    for key, abbrev in _EFFECT_ABBREV.items():
        val = effect_settings.get(key, "off")
        if val == "off":
            continue
        remap = _VARIANT_REMAP.get(key, {})
        display = remap.get(val, val.lower())
        parts.append(f"{abbrev}:{display}")

    if effect_settings.get("fmsu", False):
        parts.append("FMSU")
    if effect_settings.get("reverse", False):
        parts.append("REV")

    return f"[{', '.join(parts)}]" if parts else ""


class GenerationMixin:
    """Mixin class for full audio generation pipeline."""

    def run_generation(self):
        """Start the generation process in a background thread."""
        if self._gen_running:
            return

        self._gen_running = True
        self._gen_cancel_requested = False

        self._btn_generate.config(state="disabled")
        self._btn_cancel.config(state="normal")
        self._btn_open_output.config(state="disabled")

        self.gen_log_clear()
        self.gen_progress(0, "Starting generation...")

        settings = self._gather_generation_settings()

        threading.Thread(target=self._generation_worker, args=(settings,), daemon=True).start()

    def _gather_generation_settings(self):
        """Read all GUI state needed for generation into a plain dict."""
        clip_list = self._current_clip_list
        project_name = self._gen_project_name_var.get().strip()
        output_folder = self._gen_output_folder_var.get().strip()

        # Per-speaker effect settings
        speakers = {}
        speaker_ids = clip_list.speakers + (["Ungrouped"] if any(c.speaker_id == "" for c in clip_list.clips) else [])
        if not clip_list.is_grouped:
            speaker_ids = ["Global"]

        for speaker_id in speaker_ids:
            vars_dict = self._speaker_vars.get(speaker_id, {})
            if not vars_dict:
                continue
            effects = {}
            for eff_name in _EFFECT_ORDER:
                effects[eff_name] = vars_dict[eff_name].get() if eff_name in vars_dict else "off"
            effects["fmsu"] = vars_dict["fmsu"].get()
            effects["reverse"] = vars_dict["reverse"].get()
            speakers[speaker_id] = {
                "effects": effects,
            }

        # Global tweak settings from Tab 4
        reverb_room_size = self.config_manager.get_setting("reverb_room_size")
        distortion_drive = self.config_manager.get_setting("distortion_drive")
        noise_intensity = self.config_manager.get_setting("noise_intensity")

        return {
            "project_name": project_name,
            "output_folder": output_folder,
            "clip_list": clip_list,
            "is_grouped": clip_list.is_grouped,
            "speakers": speakers,
            "config_manager": self.config_manager,
            "output_format": self.config_manager.get_setting("output_format"),
            "output_bitrate": self.config_manager.get_setting("output_bitrate"),
            "loudnorm_lufs": self.config_manager.get_setting("loudnorm_lufs"),
            "trim_leading": self.config_manager.get_setting("trim_leading"),
            "trim_trailing": self.config_manager.get_setting("trim_trailing"),
            "reverb_room_size": reverb_room_size,
            "distortion_drive": distortion_drive,
            "noise_intensity": noise_intensity,
        }

    def _generation_worker(self, settings):
        """Background thread: run the full generation pipeline."""
        try:
            self._do_generation(settings)
        except Exception as e:
            tb = traceback.format_exc()
            self.root.after(0, lambda: self._on_generation_error(str(e), tb))

    def _do_generation(self, settings):
        """Core generation logic. Runs in background thread."""
        project_name = settings["project_name"]
        output_folder = Path(settings["output_folder"])
        clip_list = settings["clip_list"]
        is_grouped = settings["is_grouped"]
        speaker_settings = settings["speakers"]
        config_manager = settings["config_manager"]
        output_format = settings["output_format"]
        output_bitrate = settings["output_bitrate"]
        loudnorm_lufs = settings["loudnorm_lufs"]
        trim_leading = settings["trim_leading"]
        trim_trailing = settings["trim_trailing"]

        # Inject tweak settings into effect dicts
        tweaks = {
            "_reverb_room_size": settings["reverb_room_size"],
            "_distortion_drive": settings["distortion_drive"],
            "_noise_intensity": settings["noise_intensity"],
        }

        included_clips = get_included_clips(clip_list)
        total = len(included_clips)
        total_all = len(clip_list.clips)

        if total == 0:
            self.root.after(0, lambda: self._on_generation_error("No clips included.", ""))
            return

        # Place all output inside a project-named subfolder
        output_folder = output_folder / FileManager.sanitize_filename(project_name)
        output_folder.mkdir(parents=True, exist_ok=True)
        clips_effect_folder = output_folder / "clips_effect"
        clips_effect_folder.mkdir(exist_ok=True)

        ext = "." + output_format

        self._log_from_thread(f"Processing {total} clip(s)...", "header")
        self._log_from_thread(f"Project: {project_name}")
        self._log_from_thread(f"Output: {output_folder}")
        self._log_from_thread("-" * 50)

        audio_gen = AudioGenerator()
        processed_clips = []  # ClipEntry-like objects pointing to clips_effect/
        ref_entries = []
        errors = []

        # --- Phase 1: Apply effects to each clip ---
        self._log_from_thread("Phase 1: Applying effects to clips...", "header")

        for i, clip in enumerate(included_clips):
            if self._gen_cancel_requested:
                self._log_from_thread("Generation cancelled by user.", "warning")
                self.root.after(0, self._on_generation_cancelled)
                return

            # Determine which speaker panel applies
            if is_grouped:
                panel_id = clip.speaker_id if clip.speaker_id else "Ungrouped"
            else:
                panel_id = "Global"

            sp = speaker_settings.get(panel_id)
            if not sp:
                errors.append(f"{clip.filename}: No settings for panel '{panel_id}'")
                self._log_from_thread(f"  SKIP {clip.filename}: no settings for '{panel_id}'", "warning")
                continue

            # Build output path in clips_effect/
            out_name = Path(clip.filename).stem + ext
            effect_path = clips_effect_folder / out_name

            effect_settings = dict(sp["effects"])
            effect_settings.update(tweaks)

            success, error_msg = audio_gen.apply_audio_effects(
                clip.full_path, str(effect_path),
                effect_settings,
                config_manager=config_manager,
                trim_leading=trim_leading,
                trim_trailing=trim_trailing,
                output_format=output_format,
                output_bitrate=output_bitrate,
            )

            if not success:
                errors.append(f"{clip.filename}: effects failed: {error_msg}")
                self._log_from_thread(f"  ERROR {clip.filename}: {error_msg}", "error")
                continue

            # Peak-normalize in-place
            success, error_msg = audio_gen.apply_peak_normalize(str(effect_path), str(effect_path))
            if not success:
                errors.append(f"{clip.filename}: peak normalize failed: {error_msg}")
                self._log_from_thread(f"  WARN {clip.filename}: peak normalize failed: {error_msg}", "warning")
                # Don't skip — the clip file still exists, use it

            # Build a ClipEntry pointing to the processed file
            from data_models import ClipEntry
            processed = ClipEntry(
                filename=out_name,
                full_path=str(effect_path),
                speaker_id=clip.speaker_id,
                pause_after_s=clip.pause_after_s,
                included=True,
            )
            processed_clips.append(processed)
            ref_entries.append((out_name, panel_id, clip.filename))

            pct = ((i + 1) / total) * 70
            self._progress_from_thread(pct,
                                       f"Processing {i+1}/{total}: {clip.filename}")

            if (i + 1) % 5 == 0 or (i + 1) == total:
                self._log_from_thread(f"  Processed {i+1}/{total}", "info")

        if self._gen_cancel_requested:
            self._log_from_thread("Generation cancelled by user.", "warning")
            self.root.after(0, self._on_generation_cancelled)
            return

        clips_ok = len(processed_clips)
        self._log_from_thread(
            f"Phase 1 complete: {clips_ok}/{total} clips processed into clips_effect/", "success")

        if clips_ok == 0:
            self.root.after(0, lambda: self._on_generation_error(
                "No clips were processed successfully.", "\n".join(errors)))
            return

        self._progress_from_thread(75, "Merging clips...")

        # --- Phase 2: Merge ---
        self._log_from_thread("\nPhase 2: Building merged audio...", "header")

        merger = AudioMerger()

        pure_name = FileManager.build_merged_filename(project_name, "pure", "." + output_format)
        loudnorm_name = FileManager.build_merged_filename(project_name, "loudnorm", "." + output_format)
        pure_path = output_folder / pure_name
        loudnorm_path = output_folder / loudnorm_name

        self._progress_from_thread(80, "Merging (this may take a moment)...")

        success, merge_error = merger.merge_clips(
            processed_clips, str(pure_path), str(loudnorm_path),
            loudnorm_lufs=loudnorm_lufs,
            output_format=output_format,
            output_bitrate=output_bitrate,
        )

        if success:
            self._log_from_thread(f"  Merged pure: {pure_name}", "success")
            self._log_from_thread(f"  Merged loudnorm: {loudnorm_name}", "success")
        else:
            self._log_from_thread(f"  Merge failed: {merge_error}", "error")
            errors.append(f"Merge failed: {merge_error}")

        self._progress_from_thread(90, "Writing reference sheet...")

        # --- Phase 3: Reference sheet ---
        self._log_from_thread("\nPhase 3: Reference sheet...", "header")
        ref_filename = f"{FileManager.sanitize_filename(project_name)}_reference.txt"
        ref_path = output_folder / ref_filename

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        default_gap_ms = config_manager.get_setting("default_gap_ms")
        speakers_sorted = sorted(speaker_settings.keys())
        sep = "=" * 80

        # Build per-panel effect tag strings (computed once per panel)
        panel_tags = {
            panel_id: _build_effect_tag_string(sp["effects"])
            for panel_id, sp in speaker_settings.items()
        }

        with open(ref_path, 'w', encoding='utf-8') as f:
            f.write(f"{sep}\n")
            f.write(f"VCME Session Record — {project_name} — {timestamp}\n")
            f.write(f"Format: {output_format} / {output_bitrate}  |  Loudnorm: {loudnorm_lufs} LUFS  |  Gap: {default_gap_ms} ms\n")
            f.write(f"Speakers: {', '.join(speakers_sorted)}\n")
            f.write(f"Clips ({clips_ok} included / {total_all} total)\n")
            f.write(f"{sep}\n\n")

            for i, (out_name, panel_id, orig_name) in enumerate(ref_entries, 1):
                tag = panel_tags.get(panel_id, "")
                suffix = f"  {tag}" if tag else ""
                f.write(f"{i:04d}. {orig_name}{suffix}\n")

        self._log_from_thread(f"  Reference: {ref_filename}", "success")

        # --- Done ---
        self._progress_from_thread(100, "Generation complete!")
        self._log_from_thread("\n" + "=" * 50)

        if errors:
            self._log_from_thread(f"\nCompleted with {len(errors)} error(s):", "warning")
            for err in errors:
                self._log_from_thread(f"  - {err}", "warning")
        else:
            self._log_from_thread("\nAll files generated successfully!", "success")

        self._log_from_thread(
            f"\nOutput folder: {output_folder}\n"
            f"Effects clips: clips_effect/ ({clips_ok} files)\n"
            f"Merged files: {'2' if success else '0 (failed)'}\n"
            f"Reference: {ref_filename}",
            "info"
        )

        self.root.after(0, lambda: self._on_generation_done(
            str(output_folder), clips_ok, bool(success), len(errors)))

    # ── Thread-safe UI callbacks ──────────────────────────────────────────────

    def _log_from_thread(self, message, tag=None):
        self.root.after(0, lambda: self.gen_log(message, tag))

    def _progress_from_thread(self, value, label=None):
        self.root.after(0, lambda: self.gen_progress(value, label))

    def _on_generation_done(self, output_folder, clips_count, merge_ok, error_count):
        self._gen_running = False
        self._btn_generate.config(state="normal")
        self._btn_cancel.config(state="disabled")
        self._btn_open_output.config(state="normal")

        self._last_resolved_output_folder = output_folder

        self.config_manager.set_ui("last_project_name",
                                   self._gen_project_name_var.get().strip())
        self.config_manager.set_ui("last_output_folder",
                                   self._gen_output_folder_var.get().strip())

        if hasattr(self, 'status_label'):
            self.status_label.config(
                text=f"Done! {clips_count} clips"
                     f"{', merged' if merge_ok else ''}"
                     f"{f', {error_count} errors' if error_count else ''}")

    def _on_generation_error(self, message, tb):
        self._gen_running = False
        self._btn_generate.config(state="normal")
        self._btn_cancel.config(state="disabled")

        self.gen_log(f"\nFATAL ERROR: {message}", "error")
        if tb:
            self.gen_log(tb, "error")
        self.gen_progress(0, "Generation failed.")

        if hasattr(self, 'status_label'):
            self.status_label.config(text="Generation failed.")

    def _on_generation_cancelled(self):
        self._gen_running = False
        self._btn_generate.config(state="normal")
        self._btn_cancel.config(state="disabled")
        self.gen_progress(0, "Cancelled.")

        if hasattr(self, 'status_label'):
            self.status_label.config(text="Generation cancelled.")
