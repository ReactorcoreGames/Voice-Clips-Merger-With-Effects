# CLAUDE.md — Voice Clips Merger With Effects (VCME)

A GUI desktop app that applies FFMPEG effects to pre-recorded audio clips and produces merged output files. Written in Python with tkinter/ttkbootstrap. Made by Reactorcore.

---

## Running the app

```
python app.py
```

Requirements: `pip install -r requirements.txt` (ttkbootstrap). FFMPEG must be on system PATH.

Build to exe: `build_exe.bat` (uses PyInstaller).

---

## File structure

| File | Purpose |
|------|---------|
| `app.py` | Entry point — calls `gui.main()` |
| `gui.py` | `VoiceClipsMergerGUI` class + `main()`. Assembles GUI from mixin classes |
| `gui_tab1.py` | Tab 1 builder — folder picker, clip list with checkboxes, speaker grouping detection, parse log |
| `gui_tab2.py` | Tab 2 builder — per-speaker (or global) effect panels, test clip button |
| `gui_tab3.py` | Tab 3 builder — project name, output folder, generate button, progress, log |
| `gui_tab4.py` | Tab 4 builder — inter-clip gap, silence trim, output format/bitrate, effect tweaks, loudnorm target |
| `gui_handlers.py` | Button click handlers (folder load, clip toggle, test clip, generate, etc.) |
| `gui_generation.py` | `GenerationMixin` — background generation thread, progress, cancel |
| `gui_theme.py` | ttkbootstrap theme application helpers |
| `clip_manager.py` | Folder scanning, speaker grouping detection, pause suffix parsing |
| `audio_generator.py` | FFMPEG audio effect chains applied to pre-recorded clips |
| `audio_merger.py` | Merges processed clips into final audio with configurable silence gaps |
| `file_manager.py` | Filename builders, folder creation, reference sheet writer |
| `character_profiles.py` | Load/save/update `character_profiles.json` |
| `config_manager.py` | Load/save/validate `config.json`, settings access |
| `config.py` | Constants: theme colors, effect filter chains, VCME defaults |
| `data_models.py` | Dataclasses: `ClipEntry`, `ClipList`, `SpeakerProfile` |

### Persistent data files (auto-created on first launch)

- `config.json` — UI state, gap settings, format/bitrate, trim flags, effect tweaks
- `character_profiles.json` — Per-speaker effect profiles, auto-saved on every change

### Output structure

```
output_folder/
├── clips_effect/                ← FFMPEG-processed copies of all included clips
├── !project_merged_pure.mp3     ← peak-normalized merge
├── !project_merged_loudnorm.mp3 ← loudnorm merge
└── project_reference.txt        ← clip list, speaker assignments, effect settings used
```

### Other folders

- `output_test/` — Test clip previews (written by Test button in Tab 2)

---

## Architecture

`VoiceClipsMergerGUI` inherits from five mixin classes:

```
VoiceClipsMergerGUI(Tab1Builder, Tab2Builder, Tab3Builder, Tab4Builder, GUIHandlers, GenerationMixin)
```

The GUI class holds all shared state (tkinter vars, config_manager, char_profiles, clip_list, etc.).

### Tab flow

1. **Tab 1 — Load Clips**: User picks a folder → `clip_manager.scan_folder()` scans it → clip list with checkboxes → `Continue →` advances to Tab 2
2. **Tab 2 — Effects**: Dynamic speaker panels (grouped: one per `@Speaker` prefix; global: one panel for all). Auto-saves to `character_profiles.json` on every change.
3. **Tab 3 — Generate**: User sets project name + output folder → clicks Generate All → background thread runs pipeline
4. **Tab 4 — Settings**: Inter-clip gap, silence trim, output format/bitrate, loudnorm target, effect tweaks

### Generation pipeline

1. `clip_manager.get_included_clips()` → ordered list of included `ClipEntry` objects
2. Per clip: `audio_generator.apply_audio_effects()` → FFMPEG effects → `clips_effect/`
3. `audio_merger.merge_clips()` → stitch with silence gaps → `merged_pure` + `merged_loudnorm`
4. `file_manager` → write `reference.txt`

### Thread safety

Generation runs in `threading.Thread(daemon=True)`. All UI updates from the thread go through `root.after(0, callback)`. Generation settings are gathered into a plain dict on the main thread before the thread starts — the background thread never touches tkinter vars directly.

---

## Speaker grouping

- If **any** file in the loaded folder contains a `_@Speaker` tag, grouped mode activates.
- Speaker tag: `_@SpeakerID` anywhere in the stem (before the pause suffix). e.g. `001_hello_@Alice_1.5s.wav` → speaker "Alice"
- Legacy format still supported: `@Alice_line01.wav` (tag at start, no leading `_`).
- Using `_@Speaker` mid-filename lets you sort files by scene/number while still grouping by speaker.
- Files without any `@` tag → "Ungrouped" bucket with its own panel
- Non-grouped mode → single "Global" panel applied to all clips

---

## Pause system

- **Default inter-clip gap**: `config.json` → `settings.default_gap_ms` (0–10000 ms, step 100 ms)
- **Per-clip override**: `_Xs` or `_X.Xs` suffix at the very end of the filename stem, e.g. `001_hello_@Alice_1.5s.wav` → 1.5 s pause after that clip (up to 99999 s). Suffix replaces (not adds to) the default gap.

---

## Effect system

### Standard effects (off / mild / medium / strong)
`radio`, `reverb`, `distortion`, `telephone`, `robot_voice`, `cheap_mic`, `underwater`, `megaphone`, `worn_tape`, `intercom`

### Named variant effects
- `alien`: off / insectoid / dimensional / warble
- `cave`: off / tunnel / cave / abyss
- `inner_thoughts`: off / Whisper / Dreamlike / Dissociated
- `add_noise`: off / White / Pink / Brown

### Boolean flags
- `fmsu`: brutal digital corruption pass (last)
- `reverse`: flip clip end-to-end (absolutely last)

### Effect tweaks (Tab 4)
Global sliders that modify preset behavior:
- `reverb_room_size` (0.0–1.0): scales reverb wetness
- `distortion_drive` (0.0–1.0): scales distortion overdrive
- `noise_intensity` (0.0–1.0): scales Add Noise amplitude

---

## Key constants (config.py)

- `MAX_PROJECT_NAME_LENGTH = 20`
- `APP_TITLE = "Voice Clips Merger With Effects"`
- `VCME_SETTINGS_DEFAULTS`: default values for all Tab 4 settings
- `AUDIO_EFFECTS`: FFMPEG filter chains for all effects, including `inner_thoughts` and `add_noise` (sentinel strings; actual filters built at runtime)
- `INNER_THOUGHTS_PRESETS`: filter parameter dicts for Whisper / Dreamlike / Dissociated

---

## Key behaviors to know

- **Intercom effect**: uses `filter_complex` to mix generated `anoisesrc` noise into the voice chain. Handled as a special path in `audio_generator.apply_audio_effects()`.
- **Add Noise effect**: same `filter_complex` path as Intercom. Amplitude scaled by `noise_intensity` setting.
- **Inner Thoughts effect**: filter built at runtime from `config_manager.get_inner_thoughts_filter(preset_name)`. Sentinel string in `AUDIO_EFFECTS` triggers the runtime builder.
- **Reverb / Distortion tweaks**: applied by scaling wet/gain values in the preset filter string at processing time.
- **Peak normalize**: always run per-clip after effects (`apply_peak_normalize()`), and run on the merged pure output before loudnorm.
- **Cancel**: cooperative — sets `_gen_cancel_requested = True`, checked between clips. Current clip always completes.
- **clip_list stored on GUI**: `self._current_clip_list` holds the active `ClipList`. `ClipEntry.included` is modified live as checkboxes are toggled.

---

## Docs

- [README.md](README.md) — User-facing quick start guide
