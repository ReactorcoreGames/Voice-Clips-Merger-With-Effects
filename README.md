# Voice Clips Merger With Effects (VCME)

Batch-process pre-recorded voice clips with FFMPEG audio effects and merge them into a finished audio file.

**Made by Reactorcore** — https://linktr.ee/reactorcore

---

## What You Need

**FFMPEG** — Required for all audio processing and merging.

- Automatic installer (recommended): https://reactorcore.itch.io/ffmpeg-to-path-installer
- Manual install: https://ffmpeg.org/download.html — add to system PATH after installing.

**Python 3.x** — Required to run from source (not needed if using the compiled .exe).
Run `pip install -r requirements.txt` once, then `python app.py`.

---

## What It Does

VCME takes a folder of pre-recorded audio clips, applies FFMPEG effect chains per speaker,
and produces merged output files. No text-to-speech — bring your own recordings.

- Applies per-speaker audio effects to each clip (Radio, Reverb, Distortion, and more).
- Saves effects-processed clips to `clips_effect/`.
- Merges all clips into a single audio file with configurable inter-clip pauses.
- Produces both a raw merge and a loudness-normalized merge.
- Generates a session log (`project_reference.txt`) listing every clip with its active effects.

---

## Quick Start

### 1. Prepare your clips folder (Tab 1)

Point VCME at a folder of audio files. Two modes:

**Grouped mode** — tag filenames with `_@SpeakerName` anywhere in the stem to assign clips to speakers.
Placing the tag mid-filename lets you sort by scene or number while still grouping by speaker:
```
001_intro_@Alice.wav
002_reply_@Bob.wav
003_retort_@Alice_1.5s.wav
```
Each speaker gets their own effects panel in Tab 2.

The legacy prefix format (`@Alice_line01.wav`) is still supported for existing clip sets.

**Global mode** — no `@` tags, all clips share a single effects panel.

**Supported formats:** `.mp3`, `.wav`, `.ogg`, `.flac`, `.m4a`, `.aiff`, `.aif`

**Per-clip pause suffix** — add `_Xs` or `_X.Xs` at the end of the filename stem (before the extension)
to set the gap after that clip in the merged output (e.g. `003_retort_@Alice_1.5s.wav`).
This overrides the default gap for that clip. Supports values up to 99999 s.

### 2. Set effects per speaker (Tab 2)

Each speaker panel has:

- **Level** — 5–100% relative volume in the mix.
- **Test Clip** — Pick any audio file and preview your settings immediately.
- **Audio Effects** — 14 effect slots. Most have Off / Mild / Medium / Strong levels;
  Alien and Cave use named variants; Inner Thoughts and Add Noise pick a character.
- **FMSU** — Brutal digital corruption toggle (applied last).
- **Reverse** — Flip the clip end-to-end toggle.

Effect settings auto-save to `character_profiles.json` on every change.

### 3. Generate (Tab 3)

1. Enter a **Project Name** (filename prefix, 20 chars max).
2. Choose an **Output Folder**.
3. Click **Generate All** and confirm.

Output structure:

```
output_folder/
├── clips_effect/                      ← Effects-processed clips
│   └── clipname.mp3
├── !project_merged_pure.mp3           ← Merged, no normalization
├── !project_merged_loudnorm.mp3       ← Merged, loudness-normalized
└── project_reference.txt             ← Clip list reference sheet
```

### 4. Settings (Tab 4)

- **Default gap** — Silence inserted after each clip in the merge (0–10000 ms, step 100 ms).
  Overridden per-clip by the `_Xs` filename suffix.
- **Silence trimming** — Optionally remove leading and/or trailing silence from each clip
  before processing. Off by default.
- **Output format** — MP3, OGG, FLAC, WAV, or M4A. Bitrate options for lossy formats.
- **Loudnorm target** — LUFS level for the normalized merge output (-23 / -16 / -14 / -11).
- **Effect tweaks** — Global sliders for Reverb room size, Distortion grit, and Noise intensity.

---

## Audio Effects Reference

| Effect | Description |
|--------|-------------|
| Radio Filter | Walkie-talkie / comms radio. Bandpass + phaser + compression. |
| Reverb | Spatial depth. Configurable echo chains. |
| Distortion | Aggressive clipping and bit crushing. |
| Telephone | Lo-fi compressed sound. Narrow bandpass + bit crushing. |
| Robot Voice | Ring modulator. Mechanical / robotic character. |
| Cheap Mic | Degraded quality, poor recording simulation. |
| Underwater | Muffled, wet, submerged. Lowpass + flanger. |
| Megaphone | Projected bullhorn. Treble-boosted, punchy. |
| Worn Tape | VHS/cassette degradation. Wow-flutter, analog warble. |
| Intercom | Hallway speaker box. Flat, compressed, confined. |
| Alien Voice | Non-human vocal quality. Variants: Insectoid, Dimensional, Warble. |
| Cave | Physical stone space reverb. Variants: Tunnel, Cave, Abyss. |
| Inner Thoughts | Internal monologue filter. Variants: Whisper, Dreamlike, Dissociated. |
| Add Noise | Additive background noise. Variants: White, Pink, Brown. |

Effects are fully combinable. FMSU and Reverse are applied after all effects.

---

## Reference Sheet (`project_reference.txt`)

Each generation run writes a session log to the output folder. Example:

```
================================================================================
VCME Session Record — my_scene — 2026-03-08 14:32:07
Format: mp3 / 192k  |  Loudnorm: -16 LUFS  |  Gap: 500 ms
Speakers: alice, bob, Ungrouped
Clips (7 included / 9 total)
================================================================================

0001. 001_intro_@alice.wav  [RAD:medium, RVB:mild]
0002. 002_reply_@bob.wav  [TEL:strong, FMSU]
0003. 003_ambient.wav
```

Each clip line shows the source filename followed by active effects in brackets.
Effects with no active settings have no bracket. The abbreviations are:

| Abbreviation | Effect | Variants |
|---|---|---|
| RAD | Radio Filter | mild / medium / strong |
| RVB | Reverb | mild / medium / strong |
| DIST | Distortion | mild / medium / strong |
| TEL | Telephone | mild / medium / strong |
| ROBO | Robot Voice | mild / medium / strong |
| CHP | Cheap Mic | mild / medium / strong |
| UNDR | Underwater | mild / medium / strong |
| MEGA | Megaphone | mild / medium / strong |
| TAPE | Worn Tape | mild / medium / strong |
| ICOM | Intercom | mild / medium / strong |
| ALN | Alien Voice | insect / dim. / warble |
| CAVE | Cave | tunnel / cave / abyss |
| ITH | Inner Thoughts | whisper / dreamlike / dissoc. |
| NOIS | Add Noise | white / pink / brown |
| FMSU | FMSU | (flag — no value) |
| REV | Reverse | (flag — no value) |

---

## Troubleshooting

**FFMPEG not found** — Install FFMPEG and make sure it is in your system PATH.
Use the automatic installer at https://reactorcore.itch.io/ffmpeg-to-path-installer
then restart the program.

**No clips loading** — The folder must contain at least one supported audio file
(`.mp3`, `.wav`, `.ogg`, `.flac`, `.m4a`, `.aiff`, `.aif`). Other formats are skipped
and listed in the scan log.

**Effects not applying** — Check that the clip panel in Tab 2 has at least one effect set
to something other than Off. Effects that are all Off still pass the clip through
(volume + peak normalize only).

**Merged output sounds wrong** — Check the generation log in Tab 3 for per-clip errors.
The reference sheet in the output folder lists every clip with the effects that were applied.

**Test clip file in use** — If the test output file is open in your media player, VCME
cannot overwrite it. Stop playback first, then click Test again.

**Stale speaker profiles causing unexpected effects** — Effect settings for each speaker name
are saved automatically to `character_profiles.json` in the program folder and reloaded on
the next session. If you rename speakers or start a new project, old entries from previous
sessions may still be stored there. If a speaker panel loads with effects already enabled
and you weren't expecting it, those settings are being recalled from a past session.
To reset: open `character_profiles.json` in any text editor and delete the entries you no
longer need, or delete the file entirely to start fresh (it will be recreated automatically).
Reviewing the reference sheet after each run is a good way to catch any stale effects that
were applied unintentionally.

---

## Credits

- **ttkbootstrap** — Modern themed tkinter UI
- **FFMPEG** — Audio processing and merging
- **Voice Clips Merger With Effects** — By Reactorcore

---

## Links

Check out everything else I do: ✨🚀
https://linktr.ee/reactorcore
