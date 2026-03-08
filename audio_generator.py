"""
Audio processing for Voice Clips Merger With Effects (VCME).
Applies FFMPEG effect chains to pre-recorded audio clips.
No TTS — clips are provided by the user.
"""

import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path


def _get_subprocess_startupinfo():
    """Get subprocess startup info to hide console windows on Windows."""
    if sys.platform == 'win32':
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        return startupinfo
    return None


class AudioGenerator:
    """Applies audio effects to pre-recorded clips using FFMPEG."""

    def _get_subprocess_startupinfo(self):
        return _get_subprocess_startupinfo()

    def apply_audio_effects(self, input_path, output_path, effect_settings,
                            config_manager=None,
                            trim_leading=False,
                            trim_trailing=False,
                            output_format="mp3",
                            output_bitrate="128k"):
        """
        Apply audio effects to a clip using FFMPEG.

        Pipeline:
        0.  (optional) Trim leading silence
        0b. (optional) Trim trailing silence
        1.  Frequency-based effects (radio, telephone, cheap_mic, underwater, megaphone, worn_tape)
        2.  Ring-mod / pitch character effects (robot_voice, alien)
        3.  Spatial / echo effects (reverb, cave)
        4.  Distortion (applied last — needs hot signal)
        5.  Inner Thoughts filter (if active)
        5b. Soft limiting
        6.  FMSU (if active)
        7.  Reverse (if active)
        Add Noise is handled via filter_complex (mixed in alongside voice chain).

        Args:
            input_path: Path to source audio clip.
            output_path: Path for processed output.
            effect_settings: Dict mapping effect names to preset values.
            config_manager: ConfigManager instance (for inner thoughts filter building).
            trim_leading: If True, remove head silence.
            trim_trailing: If True, remove tail silence.
            output_format: Output file format (mp3/ogg/flac/wav/m4a).
            output_bitrate: Bitrate string for lossy formats (e.g. "128k").

        Returns:
            tuple: (success: bool, error_message: str or None)
        """
        from config import AUDIO_EFFECTS, FMSU_FILTER

        try:
            filters = []

            # STAGE 0: Optional silence trimming
            if trim_leading:
                filters.append(
                    "silenceremove="
                    "start_periods=1:start_silence=0:start_threshold=-50dB"
                )
            if trim_trailing:
                filters.append(
                    "silenceremove="
                    "stop_periods=1:stop_silence=0.1:stop_threshold=-50dB"
                )

            # STAGE 1: Frequency-based effects
            for effect_name in ["radio", "telephone", "cheap_mic",
                                 "underwater", "megaphone", "worn_tape"]:
                level = effect_settings.get(effect_name, "off")
                if level != "off" and effect_name in AUDIO_EFFECTS:
                    f = AUDIO_EFFECTS[effect_name]["presets"].get(level, "")
                    if f:
                        filters.append(f)

            # STAGE 2: Ring-mod / pitch character effects
            for effect_name in ["robot_voice", "alien"]:
                level = effect_settings.get(effect_name, "off")
                if level != "off" and effect_name in AUDIO_EFFECTS:
                    f = AUDIO_EFFECTS[effect_name]["presets"].get(level, "")
                    if f:
                        filters.append(f)

            # STAGE 3: Spatial / echo effects
            # Reverb and Cave support room_size / tweak overrides
            reverb_level = effect_settings.get("reverb", "off")
            if reverb_level != "off":
                reverb_filter = _build_reverb_filter(
                    reverb_level,
                    effect_settings.get("_reverb_room_size", 0.5)
                )
                if reverb_filter:
                    filters.append(reverb_filter)

            cave_level = effect_settings.get("cave", "off")
            if cave_level != "off" and "cave" in AUDIO_EFFECTS:
                f = AUDIO_EFFECTS["cave"]["presets"].get(cave_level, "")
                if f:
                    filters.append(f)

            # STAGE 4: Distortion (hot signal needed)
            dist_level = effect_settings.get("distortion", "off")
            if dist_level != "off":
                dist_filter = _build_distortion_filter(
                    dist_level,
                    effect_settings.get("_distortion_drive", 0.5)
                )
                if dist_filter:
                    filters.append(dist_filter)

            # STAGE 5: Inner Thoughts filter
            inner_thoughts_variant = effect_settings.get("inner_thoughts", "off")
            if inner_thoughts_variant != "off" and config_manager is not None:
                it_filter = config_manager.get_inner_thoughts_filter(inner_thoughts_variant)
                if it_filter:
                    filters.append(it_filter)

            # STAGE 5b: Soft limiting
            filters.append("alimiter=level=1:attack=1:release=100")

            # STAGE 6: FMSU
            if effect_settings.get("fmsu", False):
                filters.append(FMSU_FILTER)
                filters.append("alimiter=level=1:attack=7:release=100")

            # STAGE 7: Reverse
            if effect_settings.get("reverse", False):
                filters.append("areverse")

            filter_chain = ",".join(filters)

            # Build codec args for output format
            codec_args = _build_codec_args(output_format, output_bitrate)

            # Intercom noise (filter_complex path — mix generated noise into voice)
            intercom_level = effect_settings.get("intercom", "off")
            intercom_noise_params = {
                "mild":   "anoisesrc=amplitude=0.10:color=brown,highpass=f=300,lowpass=f=3500,acrusher=bits=6:mode=log:aa=0",
                "medium": "anoisesrc=amplitude=0.22:color=brown,highpass=f=200,lowpass=f=3000,acrusher=bits=4:mode=log:aa=0",
                "strong": "anoisesrc=amplitude=0.28:color=brown,highpass=f=150,lowpass=f=2800,acrusher=bits=3:mode=log:aa=0",
            }.get(intercom_level)

            # Add Noise (filter_complex path — mix generated noise into voice)
            add_noise_variant = effect_settings.get("add_noise", "off")
            noise_intensity = effect_settings.get("_noise_intensity", 0.5)
            add_noise_filter = _build_add_noise_filter(add_noise_variant, noise_intensity)

            # Decide which path to take
            has_intercom = intercom_noise_params is not None
            has_add_noise = add_noise_filter is not None

            if has_intercom or has_add_noise:
                # Build filter_complex graph with noise mixing
                noise_inputs = []
                noise_labels = []
                noise_filter_parts = []

                if has_intercom:
                    noise_inputs.append(None)  # generated source, not a file
                    label = "[intercom_noise]"
                    noise_filter_parts.append(f"{intercom_noise_params}{label}")
                    noise_labels.append(label)

                if has_add_noise:
                    label = "[add_noise]"
                    noise_filter_parts.append(f"{add_noise_filter}{label}")
                    noise_labels.append(label)

                all_noise = "".join(noise_labels)
                n_inputs = 1 + len(noise_labels)
                complex_graph = (
                    f"[0:a]{filter_chain}[voice];"
                    + ";".join(noise_filter_parts) + ";"
                    + f"[voice]{all_noise}amix=inputs={n_inputs}:weights={'1 ' * n_inputs}:normalize=0:duration=shortest"
                )
                cmd = ["ffmpeg", "-i", str(input_path),
                       "-filter_complex", complex_graph]
                cmd += codec_args
                cmd += ["-y", str(output_path)]
            else:
                cmd = ["ffmpeg", "-i", str(input_path),
                       "-af", filter_chain]
                cmd += codec_args
                cmd += ["-y", str(output_path)]

            subprocess.run(cmd, check=True, capture_output=True, text=True,
                           startupinfo=self._get_subprocess_startupinfo())
            return True, None

        except subprocess.CalledProcessError as e:
            stderr_output = e.stderr if e.stderr else str(e)
            return False, (
                f"Failed to apply audio effects.\n\nFFMPEG Error:\n{stderr_output}"
            )
        except FileNotFoundError:
            return False, (
                "FFMPEG not found in PATH. Please install FFMPEG.\n\n"
                "You can use: https://reactorcore.itch.io/ffmpeg-to-path-installer"
            )

    def apply_peak_normalize(self, input_path, output_path):
        """
        Peak-normalize an audio file (input → output).

        Two-pass: measure peak via volumedetect, then apply linear gain so the
        loudest sample reaches exactly 0 dBFS.

        Returns:
            tuple: (success: bool, error_message: str or None)
        """
        startupinfo = self._get_subprocess_startupinfo()
        try:
            result = subprocess.run([
                "ffmpeg", "-i", str(input_path),
                "-af", "volumedetect",
                "-f", "null", "-"
            ], capture_output=True, text=True, startupinfo=startupinfo)

            match = re.search(r"max_volume:\s*([-\d.]+)\s*dB", result.stderr)
            if not match:
                return False, "Peak normalize failed: could not read max_volume from ffmpeg output."

            max_volume_db = float(match.group(1))
            if max_volume_db >= 0.0:
                import shutil
                if str(input_path) != str(output_path):
                    shutil.copy2(str(input_path), str(output_path))
                return True, None

            gain_db = -max_volume_db
            in_place = str(input_path) == str(output_path)
            if in_place:
                fd, tmp_path = tempfile.mkstemp(suffix=Path(output_path).suffix or ".mp3")
                os.close(fd)
                actual_output = tmp_path
            else:
                actual_output = str(output_path)

            try:
                subprocess.run([
                    "ffmpeg", "-i", str(input_path),
                    "-af", f"volume={gain_db}dB",
                    "-y", actual_output
                ], check=True, capture_output=True, text=True, startupinfo=startupinfo)

                if in_place:
                    os.replace(tmp_path, str(output_path))
            except subprocess.CalledProcessError:
                if in_place:
                    try:
                        os.unlink(tmp_path)
                    except Exception:
                        pass
                raise

            return True, None
        except subprocess.CalledProcessError as e:
            return False, f"Peak normalize failed: {e.stderr}"
        except FileNotFoundError:
            return False, (
                "FFMPEG not found in PATH. Please install FFMPEG.\n\n"
                "You can use: https://reactorcore.itch.io/ffmpeg-to-path-installer"
            )


# ── Effect filter builders ────────────────────────────────────────────────────

def _build_reverb_filter(level: str, room_size: float) -> str:
    """
    Build reverb filter string with room_size tweak applied.
    room_size: 0.0 (small/dry) to 1.0 (large/wet).
    Adjusts the echo wet/decay parameter of the preset.
    """
    from config import AUDIO_EFFECTS
    base = AUDIO_EFFECTS["reverb"]["presets"].get(level, "")
    if not base or room_size == 0.5:
        return base  # Use preset as-is at midpoint

    # Scale wetness: room_size 0.0 → 0.5× wet, 1.0 → 1.5× wet
    scale = 0.5 + room_size
    # Crude but effective: replace the wet values in aecho patterns
    def _scale_wet(m):
        try:
            v = float(m.group(1)) * scale
            return f":{v:.2f}"
        except Exception:
            return m.group(0)

    return re.sub(r':(\d+\.\d+)(?=[,\[]|$)', _scale_wet, base)


def _build_distortion_filter(level: str, drive: float) -> str:
    """
    Build distortion filter string with drive tweak applied.
    drive: 0.0 (light) to 1.0 (heavy).
    At drive=0.5 returns the preset unchanged.
    """
    from config import AUDIO_EFFECTS
    base = AUDIO_EFFECTS["distortion"]["presets"].get(level, "")
    if not base or drive == 0.5:
        return base

    # Scale the volume boost at the start: drive 0.0 → 0.6×, 1.0 → 1.4×
    scale = 0.6 + drive * 0.8
    return re.sub(r'^volume=(\d+\.\d+)', lambda m: f"volume={float(m.group(1)) * scale:.2f}", base)


def _build_add_noise_filter(variant: str, intensity: float) -> str:
    """
    Build the anoisesrc filter string for Add Noise.
    intensity: 0.0 to 1.0. Maps to amplitude range 0.02–0.20.
    Returns None if variant is "off".
    """
    if variant == "off" or not variant:
        return None

    color_map = {
        "White": "white",
        "Pink": "pink",
        "Brown": "brown",
    }
    color = color_map.get(variant, "white")

    # Amplitude: 0.02 at intensity=0, 0.20 at intensity=1
    amplitude = 0.02 + intensity * 0.18
    return f"anoisesrc=amplitude={amplitude:.4f}:color={color}"


def _build_codec_args(output_format: str, output_bitrate: str) -> list:
    """Return FFMPEG codec/bitrate args for the chosen output format."""
    fmt = output_format.lower()
    if fmt == "mp3":
        return ["-c:a", "libmp3lame", "-b:a", output_bitrate]
    elif fmt == "ogg":
        return ["-c:a", "libvorbis", "-b:a", output_bitrate]
    elif fmt == "flac":
        return ["-c:a", "flac"]
    elif fmt == "wav":
        return ["-c:a", "pcm_s16le"]
    elif fmt == "m4a":
        return ["-c:a", "aac", "-b:a", output_bitrate]
    else:
        return ["-c:a", "libmp3lame", "-b:a", "128k"]
