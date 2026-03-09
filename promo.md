# Promo — Voice Clips Merger With Effects (VCME)

---

## Title

Voice Clips Merger With Effects (VCME)

## Subtitle

Batch-process your recorded audio clips with FFMPEG effects and merge them into finished, loudness-normalized audio — right from your desktop.

## Description

VCME is a desktop tool for post-processing pre-recorded voice clips. Drop a folder of audio files in, set effects per speaker, hit Generate — out comes a finished merged audio file with all your clips processed, paced, and loudness-normalized.

Runs fully offline. Bring your own recordings — from voice actors, your own mic, AI voice generators, anywhere — and VCME handles the rest.

**Speaker grouping** — tag filenames with `_@SpeakerName` anywhere in the stem and each speaker gets their own independent effects panel. Place the tag mid-filename so clips sort naturally by scene or number while still grouping by speaker — no more alphabetic clumping. No tags? All clips share a single global panel.

**Per-clip pause control** — add `_1.5s` to the end of a filename stem and that clip gets 1.5 seconds of silence after it in the merged output. Supports values up to 99999 s. No timeline editing required.

**14 audio effects, fully combinable:**
Radio Filter, Reverb, Distortion, Telephone, Robot Voice, Cheap Mic, Underwater, Megaphone, Worn Tape, Intercom, Alien Voice, Cave — most with Off / Mild / Medium / Strong levels, some with named variants. Plus Inner Thoughts (Whisper / Dreamlike / Dissociated) and Add Noise (White / Pink / Brown). Top it off with FMSU (brutal digital corruption) and Reverse toggles.

Global effect tweaks let you dial in reverb room size, distortion grit, and noise intensity with a slider — without touching per-speaker settings.

**The generator produces:**
- Effects-processed individual clips (`clips_effect/`)
- A merged audio file, no normalization — truer to the original dynamics
- A merged audio file, loudness-normalized — even levels, better for podcasts and video
- A reference sheet listing every clip, its speaker panel, and its source filename

Output format is your choice: MP3, OGG, FLAC, WAV, or M4A, with bitrate options for lossy formats and a configurable loudnorm LUFS target.

**Features:**
- 14 FFMPEG audio effects with multiple levels — combinable
- FMSU (brutal digital corruption) and Reverse toggles
- Speaker grouping via `_@Speaker` tag anywhere in filename — one effects panel per speaker, natural sort order preserved
- Per-clip pause suffix system (`_Xs` at end of filename stem) — no manual timeline editing, up to 99999 s
- Global effect tweaks: reverb room size, distortion grit, noise intensity
- Optional leading/trailing silence trimming per clip
- Test Clip button — preview your settings on any file before generating
- Configurable output format, bitrate, and loudnorm LUFS target
- Per-speaker effect profiles saved automatically between sessions
- Raw and loudness-normalized merged outputs
- Reference sheet for every generated session

**Ideal for:**
- Post-processing AI TTS output (ElevenLabs, Edge-TTS, etc.)
- Game dialogue — character-consistent effect chains without manual DAW work
- Audio dramas and podcasts — quick processing pipeline for recorded clips
- Voice banks — batch effects across a whole category of lines at once
- Any project where you want to apply consistent audio effects to a batch of clips

---

Check out everything else I do: ✨🚀
https://linktr.ee/reactorcore

---

## Tags (itch.io — up to 10)

audio-tool, voice-processing, ffmpeg, batch-audio, game-audio, voice-effects, audio-merger, post-processing, dialogue, productivity
