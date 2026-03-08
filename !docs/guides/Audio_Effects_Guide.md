# Audio Effects Guide — Voice Clips Merger With Effects (VCME)

## Overview

VCME includes 14 audio effects applied per speaker in **Tab 2**. Effects are set per speaker
panel and applied during generation. They can be freely combined.

Most effects have four levels: **Off, Mild, Medium, Strong.**
Three effects use named variants instead of intensity levels: **Alien Voice, Cave,** and **Inner Thoughts.**
**Add Noise** picks a noise character: White, Pink, or Brown.

There are also two boolean toggles — **FMSU** and **Reverse** — which are simply on or off,
applied after all other effects.

Global **Effect Tweaks** in Tab 4 let you adjust Reverb room size, Distortion grit, and Noise
intensity with a single slider that scales the relevant effect across all speaker panels at once.

**Note:** Cheap Mic defaults to Mild for new speakers, which adds a touch of lo-fi realism
without being obviously degraded.

---

## Available Effects

### 1. Radio Filter
**Description:** Walkie-talkie / comms radio effect
**Use case:** Military or tactical characters, space crews, dispatch operators

**Presets:**
- **Off:** No effect
- **Mild:** Frequency bandpass with phaser and light compression
- **Medium:** Clear walkie-talkie — phaser, heavier compression, bit crush
- **Strong:** Heavy military radio — maximum compression, distortion, further narrowing

**Pairs well with:**
- Radio + Reverb = Echoing transmission from a large facility
- Radio + Distortion = Damaged or emergency radio signal

---

### 2. Reverb
**Description:** Spatial depth and presence
**Use case:** Narrators, authority figures, large environments, ethereal characters

**Presets:**
- **Off:** No effect
- **Mild:** Subtle room presence (short single echo)
- **Medium:** Arena or large hall (double echo)
- **Strong:** Cathedral or otherworldly presence (long, layered echoes)

**Tab 4 tweak — Reverb room size:** Scales echo wetness across all reverb presets from
all speakers. Left = tighter/drier, Right = larger/wetter. Applies globally.

**Pairs well with:**
- Reverb + Distortion = Powerful, aggressive presence
- Reverb + Robot Voice = Massive mechanical entity

---

### 3. Distortion
**Description:** Aggressive, gritty, raw
**Use case:** Angry characters, monsters, corrupted voices, intense moments

**Presets:**
- **Off:** No effect
- **Mild:** Subtle compression and grit
- **Medium:** Clear aggression with overdrive and bit crush
- **Strong:** Heavy, destructive clipping

**Tab 4 tweak — Distortion grit:** Scales overdrive/bit crush intensity across all distortion
presets from all speakers. Left = lighter, Right = heavier.

**Pairs well with:**
- Distortion + Reverb = Powerful, dominating presence
- Distortion + Telephone = Broken or corrupted transmission
- Distortion + Robot Voice = Corrupted / damaged AI

---

### 4. Telephone
**Description:** Lo-fi, compressed, retro
**Use case:** Phone calls, old recordings, degraded comms

**Presets:**
- **Off:** No effect
- **Mild:** Slight bandpass filtering and compression
- **Medium:** Clear telephone / intercom effect
- **Strong:** Heavily compressed and crushed (emergency speaker, ancient intercom)

**Pairs well with:**
- Telephone + Reverb = PA system in a large building
- Telephone + Distortion = Damaged speaker or broken comms

---

### 5. Robot Voice
**Description:** Robotic, mechanical, synthetic
**Use case:** AI characters, cyborgs, robots, synthetic entities

**Presets:**
- **Off:** No effect
- **Mild:** 80 Hz ring modulator with metallic filtering — noticeable robotic character
  while maintaining clarity
- **Medium:** 40 Hz ring modulator — classic robotic sweet spot with good intelligibility
- **Strong:** 100 Hz ring modulator + 8 kHz sample crushing + 6-bit degradation —
  extreme crunchy digital / terminator voice

**Pairs well with:**
- Robot Voice + Reverb = Massive mechanical entity
- Robot Voice + Distortion = Corrupted or damaged AI
- Robot Voice + Telephone = Synthetic comms system
- Robot Voice + Radio = Robotic military transmissions

**Technical note:** Uses ring modulation (mixing the voice with sine waves) combined with
sample rate reduction and bit crushing for the Strong preset. Creates authentic robotic
character without phasing artifacts.

---

### 6. Cheap Mic *(Default: Mild)*
**Description:** Degraded quality, poor recording
**Use case:** Adding natural character to recordings, retro audio, worn equipment

**Presets:**
- **Off:** Clean, unprocessed
- **Mild:** Subtle lo-fi character *(DEFAULT for new speakers)*
- **Medium:** Clear degradation with compression
- **Strong:** Heavily degraded, extreme lo-fi

**Pairs well with:**
- Cheap Mic + Radio = Old military radio transmission
- Cheap Mic + Telephone = Ancient intercom system
- Cheap Mic + Distortion = Broken or damaged speaker

**Why default Mild?** The mild preset adds a slight imperfection to otherwise very clean
recordings — gives them a more lived-in character without being obviously degraded.

---

### 7. Underwater
**Description:** Submerged, muffled, wet — voice heard through water
**Use case:** Underwater scenes, drowning, distant sounds through liquid

**Presets:**
- **Off:** No effect
- **Mild:** Gentle lowpass + soft flanger wobble
- **Medium:** Stronger muffling with deeper flange
- **Strong:** Heavily muffled, strong wet wobble with compression

**Pairs well with:**
- Underwater + Reverb = Vast submerged space
- Underwater + Robot Voice = Machine speaking from beneath the surface

---

### 8. Megaphone
**Description:** Projected bullhorn — punchy, bandpassed, no transmission shimmer
**Use case:** Crowd control, announcements, protest scenes, military loudspeaker

**Presets:**
- **Off:** No effect
- **Mild:** Treble boost with light saturation
- **Medium:** Compressed, narrowed, with bit crush bite
- **Strong:** Aggressive narrow band, heavy compression and saturation

**Pairs well with:**
- Megaphone + Reverb = Outdoor announcement in a large open space
- Megaphone + Distortion = Damaged or overdriven loudspeaker

---

### 9. Worn Tape
**Description:** VHS/cassette degradation — wow-flutter, lo-fi, analog warble
**Use case:** Flashback recordings, found footage, old home video feel

**Presets:**
- **Off:** No effect
- **Mild:** Subtle sample rate reduction with gentle phaser warble and light bit crush
- **Medium:** Noticeable tape warble, stronger crush and phaser
- **Strong:** Heavy degradation, extreme flutter and bit depth loss

**Pairs well with:**
- Worn Tape + Reverb = Distant old recording played in an empty room
- Worn Tape + Telephone = Ancient answering machine message

---

### 10. Intercom
**Description:** Hallway speaker box — boxy, compressed, confined
**Use case:** Building intercoms, security systems, facility announcements

**Presets:**
- **Off:** No effect
- **Mild:** Moderate frequency narrowing, compression, and soft saturation
- **Medium:** Tighter frequency range, heavier compression
- **Strong:** Narrow boxy sound with aggressive compression and saturation

**Pairs well with:**
- Intercom + Cheap Mic = Worn-out building speaker system
- Intercom + Distortion = Damaged or malfunctioning intercom

---

### 11. Alien Voice
**Description:** Inhuman, otherworldly, strange
**Use case:** Alien characters, eldritch entities, non-human voices

**Variants (named, not intensity levels):**
- **Off:** No effect
- **Insectoid:** Ring modulation against 250 Hz + high treble — chittering arthropod quality
- **Dimensional:** Tremolo + phaser sweep + vibrato — flickers in and out of existence
- **Warble:** Tremolo + 20 Hz ring mod — classic ayylmao alien tongue wobble

**Pairs well with:**
- Alien + Reverb = Vast presence from another dimension
- Alien + Distortion = Aggressive hostile entity

---

### 12. Cave
**Description:** Physical stone spaces — echo and space
**Use case:** Underground scenes, tunnels, cavernous spaces, enclosed stone rooms

**Variants (named, not intensity levels):**
- **Off:** No effect
- **Tunnel:** Tight single echo — short reverberant space with high-frequency rolloff
- **Cave:** Multi-tap chamber — layered reflections with double echo chain
- **Abyss:** Impossibly long decay — echoes cascading into deep darkness

**Pairs well with:**
- Cave + Robot Voice = Massive mechanical entity in an underground facility
- Cave + Distortion = Creature lurking in the dark

---

### 13. Inner Thoughts
**Description:** Internal monologue filter — private, filtered, inward
**Use case:** Internal character voices, memory/flashback, dissociative moments, dreamy narration

Unlike most effects, Inner Thoughts is set per speaker panel and applies to all that speaker's
clips when enabled. It stacks on top of whatever other effects the speaker has.

**Variants:**
- **Off:** No effect
- **Whisper:** Heavily muffled with aggressive lowpass (~1100 Hz). Sounds like the voice is
  inside a helmet or behind a wall. Very occluded and private. Good for characters suppressing
  emotion or thinking in compressed, guarded bursts.
- **Dreamlike:** Warm frequency range with a dual-tap echo trail (150 ms + 280 ms). The voice
  dissolves into space. Good for meditation, surreal scenes, and characters drifting in and out
  of consciousness.
- **Dissociated:** Cold, mildly narrowed frequency range with a tight single echo. Intelligible
  but detached — like a thought surfacing in a noisy environment. Good general-purpose default
  for internal monologue.

**Creative uses beyond literal inner thoughts:**
- Flashback / memory: Apply Inner Thoughts to give recalled audio a filtered, distant quality
  distinct from present-tense speech.
- Environmental filtering: Stack Whisper on top of Telephone or Radio for extreme lo-fi intimacy.
- Ambient narration: Dreamlike applied to a whole panel creates a sustained dissolved quality.

**Pairs well with:**
- Radio + Inner Thoughts (Dissociated) = Fragmented transmission with a cold, haunted quality
- Reverb + Inner Thoughts (Dreamlike) = Massive echoing space dissolving into the void
- Telephone + Inner Thoughts (Whisper) = Muffled signal within an already degraded channel

---

### 14. Add Noise
**Description:** Additive background noise mixed into the clip
**Use case:** Room ambience, hiss, rumble, lo-fi texture

Intensity is controlled by the **Noise intensity** slider in Tab 4, which scales the amplitude
of the generated noise source globally across all speakers.

**Variants:**
- **Off:** No effect
- **White:** Broadband hiss — equal energy at all frequencies. Sharp, present.
- **Pink:** Warmer, rolled-off hiss — more natural-sounding room ambience.
- **Brown:** Low-frequency rumble. Deep, thick, almost subterranean.

**Tab 4 tweak — Noise intensity:** Left = barely audible texture, Right = noise competes with
the voice. Start subtle.

**Pairs well with:**
- Add Noise (White) + Radio = Hissy transmission static
- Add Noise (Pink) + Cheap Mic = Warm room ambience from a recording space
- Add Noise (Brown) + Cave = Underground rumble beneath the voice

---

### FMSU *(Toggle — On/Off)*
**Description:** F*** My Sh** Up — brutal digital corruption
**Use case:** Glitched voices, corrupted transmissions, damaged AI, horror distortion

**What it does:** Applies a two-stage bit-crush and hard-clip cycle. 2-bit quantization in
both log and linear modes, with overdrive before each stage and waveform fold-over clipping.
The result is harsh, artifact-heavy, and genuinely corrupted — speech rhythms survive but
the voice is clearly destroyed.

**Note:** Applied as the very last processing stage, after all other effects. A safety limiter
fires after FMSU to prevent encoder overflow.

**Pairs well with:**
- FMSU + Robot Voice = Catastrophically malfunctioning AI
- FMSU + Distortion = Complete signal breakdown
- FMSU + Telephone = Dying transmission on its last legs

---

### Reverse *(Toggle — On/Off)*
**Description:** Plays the fully processed clip backwards
**Use case:** Dream sequences, supernatural voices, creative sound design

**Note:** Applied absolutely last — reversal is the final state of the clip.

---

## How Effects Are Applied

### Processing Pipeline

Most effects run through a single optimised FFMPEG pass. Add Noise and Intercom use a
`filter_complex` mixing path when active (see note below).

```
0. Optional Silence Trim (leading / trailing — off by default, set in Tab 4)
   ↓
1. Frequency Effects  (Radio, Telephone, Cheap Mic, Underwater, Megaphone, Worn Tape, Intercom)
   ↓
2. Ring Modulation / Pitch Effects  (Robot Voice, Alien)
   ↓
3. Spatial / Echo Effects  (Reverb, Cave)
   ↓
4. Distortion
   ↓
5. Inner Thoughts filter  (if not Off)
   ↓
6. Soft Limiter  (always active — prevents encoder clipping)
   ↓
7. Final Volume Adjustment  (5–100%)
   ↓
8. FMSU  (if enabled) + safety limiter
   ↓
9. Reverse  (if enabled)
   ↓
Peak Normalise  (separate pass — brings clip peak to 0 dBFS, preserving dynamics)
```

**Add Noise** is handled via a `filter_complex` path: the voice goes through all stages above,
then a generated noise source is mixed in at the output. The noise type and amplitude are set
by the Add Noise variant and the Tab 4 Noise intensity slider.

**Intercom** uses the standard single-pass chain — no noise mixing. Unlike the old STVG
version, Intercom in VCME is a pure filter effect.

**Per-clip peak normalisation** runs after the effect pass. Each `clips_effect` file is
brought to 0 dBFS using a two-pass linear gain (measure peak, apply exact gain). This
preserves all dynamics and relative loudness within the clip — purely a ceiling adjustment,
not compression or loudness targeting. Effects that remove frequency content (Radio, Telephone,
Cheap Mic) will naturally sound quieter than fullband audio at the same peak level — this is
correct and realistic behaviour, not a bug.

---

## Recommended Combinations by Character Type

### Narrator / Announcer
- Reverb: Medium or Strong
- Cheap Mic: Off or Mild
- Result: Booming, authoritative presence

### Space Marine / Tactical Soldier
- Radio: Medium
- Reverb: Off or Mild
- Cheap Mic: Mild
- Result: Clear tactical comms with authority

### Gruff Fighter / Veteran
- Distortion: Mild
- Cheap Mic: Mild or Medium
- Result: Gritty, experienced voice

### Robot / AI / Cyborg
- Robot Voice: Medium or Strong
- Reverb: Off or Mild
- Result: Clear synthetic character

### Corrupted / Damaged AI
- Robot Voice: Strong
- Distortion: Mild or Medium
- Telephone: Mild
- Result: Glitchy, malfunctioning mechanical voice

### Ethereal / Supernatural Entity
- Reverb: Strong
- Telephone: Mild
- Cheap Mic: Off
- Result: Distant, otherworldly presence

### Internal Monologue / Memory Voice
- Inner Thoughts: Dissociated or Dreamlike
- Cheap Mic: Off
- Result: Detached, filtered, private-sounding voice

### Ambient / Environmental Character
- Add Noise: Pink or Brown
- Reverb: Mild
- Result: Voice with room presence and natural texture

### Emergency Broadcast
- Telephone: Strong
- Radio: Medium
- Distortion: Mild
- Result: Damaged emergency speaker system

---

## Tips for Best Results

1. **Start with Mild** — test effects at low levels before going stronger.
2. **Use Test Clip** in Tab 2 to audition your settings on a real file before a full run.
3. **Don't over-combine** — all effects at maximum usually creates mud.
4. **Cheap Mic is already on** — Mild is the default for new speakers. Turn it Off if you
   want a clean, unprocessed sound.
5. **Volume range is 5–100%** — default 100% is full normalized output. Reduce a speaker's
   level to make them quieter relative to others in the merged output.
6. **Use effect tweaks in Tab 4** — instead of rebuilding all your speaker panels, dial
   in reverb size, distortion grit, and noise intensity globally to find the sweet spot.
7. **The pipeline prevents clipping** — the soft limiter and per-clip peak normalisation
   handle safety. Experiment freely.

---

## Configuring Effects (`config.py`)

Effects and their FFMPEG filter chains are defined in `config.py` under `AUDIO_EFFECTS`:

```python
AUDIO_EFFECTS = {
    "effect_name": {
        "name": "Display Name",
        "description": "Effect description",
        "presets": {
            "off": "",
            "mild": "ffmpeg_filter_chain",
            "medium": "ffmpeg_filter_chain",
            "strong": "ffmpeg_filter_chain",
        }
    }
}
```

To add new effects or modify existing ones, edit the FFMPEG filter chains in `config.py`.
Test any modified filter chain with a single clip before doing a full generation run.

---

## FFMPEG Filters Reference

| Filter       | Purpose                                              |
|--------------|------------------------------------------------------|
| `loudnorm`   | Loudness normalisation (EBU R128)                   |
| `highpass`   | Removes frequencies below cutoff                     |
| `lowpass`    | Removes frequencies above cutoff                     |
| `bandpass`   | Passes only a specific frequency range               |
| `aphaser`    | Phaser effect (cyclic comb filtering / warble)       |
| `flanger`    | Flanger effect (short delay + feedback sweep)        |
| `aecho`      | Echo and reverb                                      |
| `acompressor`| Dynamic range compression                            |
| `acrusher`   | Bit crushing / sample rate reduction (lo-fi)         |
| `aresample`  | Sample rate conversion                               |
| `asoftclip`  | Soft or hard clipping for distortion / fold-over    |
| `alimiter`   | Soft limiter to prevent clipping                     |
| `anoisesrc`  | Generated noise source (white, pink, brown, etc.)   |
| `amix`       | Mixes multiple audio streams together                |
| `areverse`   | Reverses the audio clip                              |
| `tremolo`    | Tremolo (amplitude modulation)                       |
| `vibrato`    | Vibrato (pitch modulation)                           |
| `volume`     | Volume multiplication                                |
| `treble`     | High-frequency boost/cut                             |
| `bass`       | Low-frequency boost/cut                              |
| `aeval`      | Mathematical audio expression (used for ring mod)   |

Full FFMPEG audio filter documentation: https://ffmpeg.org/ffmpeg-filters.html#Audio-Filters

---

## Troubleshooting

**Effects sound too extreme?**
- Try a lower preset level (Mild instead of Strong).
- Remember: Cheap Mic is already enabled at Mild by default.
- Use the Tab 4 effect tweaks to pull back reverb size or distortion grit globally.

**No audible difference?**
- Ensure FFMPEG is installed (`ffmpeg -version` in a terminal).
- Confirm the effect is not set to Off.
- Try Test Clip to audition the current settings directly.

**Audio clipping or artifacts?**
- Should be rare due to the always-active soft limiter and per-clip peak normalisation.
  If it occurs, use milder presets.

**Audio too quiet after effects?**
- Frequency-stripping effects (Radio, Telephone, Cheap Mic, Megaphone) remove parts of the
  signal so they naturally have less energy than fullband audio at the same peak level. This
  is realistic — a telephone filter is supposed to sound smaller.
- The `merged_loudnorm` output applies broadcast-standard loudness normalisation across the
  whole file, bringing quieter-sounding clips up to a consistent perceived level.
- If individual clips feel too distant, try a milder preset level.

**Short clips sound quieter than long clips with Radio active?**
- The phaser component sweeps through a volume cycle over time. Short clips under ~1 second
  may catch a narrow slice of the quiet phase and sound subdued.
- Use Radio at Medium or Strong (which add compression that partially counteracts the sweep),
  or accept it as natural effect character.

**Add Noise is too loud / too quiet?**
- Adjust the Noise intensity slider in Tab 4. It scales amplitude globally across all speakers
  using Add Noise. Start with the slider around 30–40% for subtle texture.

**Generation taking a while?**
- Each clip goes through a full FFMPEG effect pass plus a peak normalise pass. This is expected.
  A large batch of clips with heavy effects (especially Add Noise, which requires filter_complex)
  will take proportionally longer.
