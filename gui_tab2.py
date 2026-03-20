"""
Tab 2: Effects
Voice Clips Merger With Effects (VCME).
Per-speaker (or global) audio effect panels + Test clip button.
"""

import tkinter as tk
import ttkbootstrap as ttk
from tkinter import ttk as _tk_ttk
from ttkbootstrap.constants import *

from config import (
    APP_THEME, AUDIO_EFFECTS, EFFECT_LEVELS,
    ALIEN_VARIANTS, CAVE_VARIANTS,
    INNER_THOUGHTS_EFFECT_VARIANTS, ADD_NOISE_VARIANTS,
    PITCH_MULTIPLIER_MIN, PITCH_MULTIPLIER_MAX, PITCH_MULTIPLIER_DEFAULT,
)

try:
    from ttkbootstrap.tooltip import ToolTip
    _TOOLTIP_AVAILABLE = True
except ImportError:
    _TOOLTIP_AVAILABLE = False


def _tip(widget, text, position=None):
    if _TOOLTIP_AVAILABLE and widget:
        kwargs = {"text": text, "delay": 400}
        if position:
            kwargs["position"] = position
        ToolTip(widget, **kwargs)


# Effect display order for the 2-column grid
_EFFECT_ORDER = [
    "radio", "reverb", "distortion", "telephone",
    "robot_voice", "cheap_mic", "underwater", "megaphone",
    "worn_tape", "intercom", "cave", "alien",
    "inner_thoughts", "add_noise",
    # fmsu and reverse are boolean flags (checkboxes), handled separately
]

# Map effect_name → variant list (for effects with named presets)
_VARIANT_MAP = {
    "alien": ALIEN_VARIANTS,
    "cave": CAVE_VARIANTS,
    "inner_thoughts": INNER_THOUGHTS_EFFECT_VARIANTS,
    "add_noise": ADD_NOISE_VARIANTS,
}

# Short display labels for long variant names
_LEVEL_DISPLAY_LABELS = {
    "insectoid": "Insect",
    "dimensional": "Dim.",
    "Dissociated": "Dissoc.",
}


class Tab2Builder:
    """Mixin class for building Tab 2 (Effects) UI."""

    def build_tab2(self, parent):
        """Build the complete Tab 2 interface."""
        self._speaker_vars = {}
        self._speaker_widgets = {}

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

        def bind_mousewheel_tab2(widget):
            widget.bind("<MouseWheel>", on_mousewheel)
            for child in widget.winfo_children():
                bind_mousewheel_tab2(child)

        canvas.bind("<MouseWheel>", on_mousewheel)
        scrollable.bind("<MouseWheel>", on_mousewheel)

        self._tab2_canvas = canvas
        self._tab2_scrollable = scrollable
        self._tab2_bind_mousewheel = bind_mousewheel_tab2

        ttk.Label(scrollable, text="Audio Effects",
                  font=("Segoe UI", 18, "bold")).pack(pady=(0, 5))
        ttk.Label(scrollable,
                  text="Assign FFMPEG effects per speaker. In grouped mode one panel per speaker. "
                       "In global mode a single panel applies to all clips.",
                  font=("Segoe UI", 10), wraplength=900, justify="center").pack(pady=(0, 15))

        self._speaker_panels_frame = ttk.Frame(scrollable)
        self._speaker_panels_frame.pack(fill=X, pady=(0, 10))

        self._no_speakers_label = ttk.Label(
            self._speaker_panels_frame,
            text="Load a clips folder in Tab 1 to see effect panels here.",
            font=("Segoe UI", 11, "italic"),
            foreground="#A870A0"
        )
        self._no_speakers_label.pack(pady=30)

        bottom_frame = ttk.Frame(scrollable)
        bottom_frame.pack(fill=X, pady=(10, 10))

        self.btn_continue_to_tab3 = ttk.Button(
            bottom_frame, text="Continue to Generate  >>",
            command=self.on_continue_to_tab3,
            bootstyle=SUCCESS, width=28,
            state="disabled"
        )
        self.btn_continue_to_tab3.pack(side=RIGHT)

        bind_mousewheel_tab2(scrollable)

    def populate_tab2_speakers(self, clip_list):
        """
        Populate Tab 2 with speaker panels from a ClipList.
        Grouped mode: one panel per detected speaker + Ungrouped bucket.
        Global mode: single "All Clips" panel.
        """
        for widget in self._speaker_panels_frame.winfo_children():
            widget.destroy()
        self._speaker_vars = {}
        self._speaker_widgets = {}

        if clip_list is None or not clip_list.clips:
            ttk.Label(self._speaker_panels_frame,
                      text="No clips found.",
                      font=("Segoe UI", 11, "italic"),
                      foreground="#A870A0").pack(pady=30)
            self.btn_continue_to_tab3.config(state="disabled")
            return

        if clip_list.is_grouped:
            for speaker_id in clip_list.speakers:
                profile = self.char_profiles.get_or_create_profile(speaker_id)
                self._build_speaker_panel(self._speaker_panels_frame, speaker_id, profile)

            has_ungrouped = any(c.speaker_id == "" for c in clip_list.clips)
            if has_ungrouped:
                profile = self.char_profiles.get_or_create_profile("Ungrouped")
                self._build_speaker_panel(self._speaker_panels_frame, "Ungrouped", profile)
        else:
            profile = self.char_profiles.get_or_create_profile("Global")
            self._build_speaker_panel(self._speaker_panels_frame, "Global", profile,
                                      panel_label="All Clips (Global Effects)")

        self.btn_continue_to_tab3.config(state="normal")

        if hasattr(self, '_tab2_bind_mousewheel'):
            self._tab2_bind_mousewheel(self._tab2_scrollable)

    def _build_speaker_panel(self, parent, speaker_id, profile, panel_label=None):
        """Build a single speaker effect configuration panel."""
        label_text = panel_label or f"  {speaker_id}  "
        frame = _tk_ttk.LabelFrame(parent, text=label_text, padding=10)
        frame.pack(fill=X, pady=(0, 8))

        vars_dict = self._create_speaker_vars(speaker_id, profile)
        self._speaker_vars[speaker_id] = vars_dict
        widgets_dict = {}
        self._speaker_widgets[speaker_id] = widgets_dict

        # --- Test clip row ---
        top_row = ttk.Frame(frame)
        top_row.pack(fill=X, pady=(0, 8))

        # Test clip section
        test_clip_lbl = ttk.Label(top_row, text="Currently active test clip:",
                                  font=("Segoe UI", 9))
        test_clip_lbl.pack(side=LEFT, padx=(0, 4))
        _tip(test_clip_lbl,
             "Preview effects on a single clip without generating the full output.\n"
             "Pick a clip file, then click Test to process it with current effects and play it back.")

        test_clip_var = tk.StringVar(value="(none)")
        widgets_dict["test_clip_var"] = test_clip_var
        ttk.Entry(top_row, textvariable=test_clip_var,
                  width=50, state="readonly",
                  font=("Consolas", 8)).pack(side=LEFT, padx=(0, 4))

        pick_btn = ttk.Button(top_row, text="Pick",
                              command=lambda sid=speaker_id: self.on_pick_test_clip(sid),
                              bootstyle=INFO, width=6)
        pick_btn.pack(side=LEFT, padx=(0, 4))
        _tip(pick_btn, "Select a clip file to use for the test preview.")

        test_btn = ttk.Button(top_row, text="Test",
                              command=lambda sid=speaker_id: self.on_test_clip(sid),
                              bootstyle=WARNING, width=6)
        test_btn.pack(side=LEFT)
        _tip(test_btn, "Process the selected clip with the current effects and play it back.")

        # --- Effect grid (2-column) ---
        ttk.Separator(frame, orient=HORIZONTAL).pack(fill=X, pady=5)
        ttk.Label(frame, text="Audio Effects",
                  font=("Segoe UI", 9, "bold")).pack(anchor=W, pady=(0, 4))

        effects_container = ttk.Frame(frame)
        effects_container.pack(fill=X)

        left_col = ttk.Frame(effects_container)
        left_col.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 10))

        ttk.Separator(effects_container, orient=VERTICAL).pack(side=LEFT, fill=Y, padx=5)

        right_col = ttk.Frame(effects_container)
        right_col.pack(side=LEFT, fill=BOTH, expand=True, padx=(10, 0))

        half = (len(_EFFECT_ORDER) + 1) // 2
        for i, effect_name in enumerate(_EFFECT_ORDER):
            col = left_col if i < half else right_col
            levels = _VARIANT_MAP.get(effect_name)
            effect_data = AUDIO_EFFECTS.get(effect_name, {
                "name": effect_name.replace("_", " ").title(),
                "description": "",
            })
            self._build_effect_row(col, effect_name, effect_data,
                                   vars_dict[effect_name], levels=levels)

        # --- Flags row (FMSU, Reverse, Pitch ×) ---
        flags_row = ttk.Frame(frame)
        flags_row.pack(fill=X, pady=(6, 0))

        fmsu_cb = ttk.Checkbutton(flags_row, text="FMSU", variable=vars_dict["fmsu"])
        fmsu_cb.pack(side=LEFT, padx=(0, 20))
        _tip(fmsu_cb, "F*** My Sh** Up — brutal digital corruption applied last.")

        reverse_cb = ttk.Checkbutton(flags_row, text="Reverse", variable=vars_dict["reverse"])
        reverse_cb.pack(side=LEFT, padx=(0, 30))
        _tip(reverse_cb, "Reverse the clip. Applied last, after all other effects.")

        # Pitch × slider (rubberband multiplier, stored as int*100)
        pitch_lbl = ttk.Label(flags_row, text="Pitch \u00d7:",
                              font=("Consolas", 9, "bold"))
        pitch_lbl.pack(side=LEFT, padx=(0, 4))
        _tip(pitch_lbl,
             "Pitch shift via FFMPEG rubberband. Multiplier \u00d70.5\u2013\u00d72.0 (default \u00d71.0 = no shift).\n"
             "<1.0 = lower pitch. >1.0 = higher pitch. Applied independently of speed.")

        pitch_disp_var = tk.StringVar(
            value=f"\u00d7{vars_dict['pitch_multiplier'].get() / 100:.2f}")
        widgets_dict["pitch_disp_var"] = pitch_disp_var

        def _fmt_pitch(v, pv=vars_dict["pitch_multiplier"]):
            pv.set(int(round(float(v))))

        pitch_slider = ttk.Scale(
            flags_row,
            from_=int(PITCH_MULTIPLIER_MIN * 100),
            to=int(PITCH_MULTIPLIER_MAX * 100),
            variable=vars_dict["pitch_multiplier"],
            orient=HORIZONTAL, length=140,
            command=_fmt_pitch,
        )
        pitch_slider.pack(side=LEFT, padx=(0, 4))

        pitch_disp = ttk.Label(flags_row, textvariable=pitch_disp_var,
                               font=("Consolas", 9), width=6)
        pitch_disp.pack(side=LEFT)

        def _update_pitch_disp(*_, pv=vars_dict["pitch_multiplier"], dv=pitch_disp_var):
            dv.set(f"\u00d7{pv.get() / 100:.2f}")
        vars_dict["pitch_multiplier"].trace_add("write", _update_pitch_disp)

    def _build_effect_row(self, parent, effect_name, effect_data, var, levels=None):
        """Build a single effect control row with radio buttons."""
        if levels is None:
            levels = EFFECT_LEVELS

        row = ttk.Frame(parent)
        row.pack(fill=X, pady=2)

        label = ttk.Label(row, text=f"{effect_data['name']}:",
                          font=("Segoe UI", 9), width=15, anchor=W)
        label.pack(side=LEFT, padx=(0, 3))
        _tip(label, effect_data.get("description", ""))

        for level in levels:
            label_text = _LEVEL_DISPLAY_LABELS.get(level, level.capitalize())
            ttk.Radiobutton(row, text=label_text, value=level,
                            variable=var).pack(side=LEFT, padx=2)

    # ── Speaker var management ────────────────────────────────────────────────

    def _create_speaker_vars(self, speaker_id, profile):
        """Create tkinter variables for a speaker, initialized from profile."""
        vars_dict = {}

        for effect_name in _EFFECT_ORDER:
            default = getattr(profile, effect_name, "off")
            vars_dict[effect_name] = tk.StringVar(value=default)

        vars_dict["fmsu"] = tk.BooleanVar(value=profile.fmsu)
        vars_dict["reverse"] = tk.BooleanVar(value=profile.reverse)
        vars_dict["pitch_multiplier"] = tk.IntVar(value=getattr(profile, "pitch_multiplier", 100))

        for var in vars_dict.values():
            var.trace_add("write",
                          lambda *args, sid=speaker_id: self._on_speaker_var_changed(sid))

        return vars_dict

    def _on_speaker_var_changed(self, speaker_id):
        """Auto-save speaker settings to character profiles on any change."""
        if speaker_id not in self._speaker_vars:
            return

        vars_dict = self._speaker_vars[speaker_id]
        profile = self.char_profiles.get_or_create_profile(speaker_id)


        for effect_name in _EFFECT_ORDER:
            if effect_name in vars_dict:
                setattr(profile, effect_name, vars_dict[effect_name].get())

        profile.fmsu = vars_dict["fmsu"].get()
        profile.reverse = vars_dict["reverse"].get()
        profile.pitch_multiplier = vars_dict["pitch_multiplier"].get()

        self.char_profiles.update_profile(speaker_id, profile)
