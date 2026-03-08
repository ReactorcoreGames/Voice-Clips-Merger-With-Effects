"""
Audio merger for Voice Clips Merger With Effects (VCME).
Takes a list of processed clips and merges them with configurable silence gaps.
No SFX. No punctuation-based pause logic.
"""

import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from data_models import ClipEntry


def _get_subprocess_startupinfo():
    """Get subprocess startup info to hide console windows on Windows."""
    if sys.platform == 'win32':
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        return startupinfo
    return None


class AudioMerger:
    """
    Merges processed voice clips into continuous audio files.
    Pauses come from per-clip pause_after_s (derived from filename suffix or default gap).
    """

    def merge_clips(self, clips, output_pure, output_loudnorm,
                    loudnorm_lufs=-14, output_format="mp3", output_bitrate="128k"):
        """
        Merge a list of ClipEntry objects into two output files.

        Args:
            clips: List of ClipEntry (already filtered to included only, pointing to clips_effect/).
            output_pure: Path for the peak-normalized merged output.
            output_loudnorm: Path for the loudnorm merged output.
            loudnorm_lufs: Target LUFS for loudnorm (e.g. -14).
            output_format: Output file format (mp3/ogg/flac/wav/m4a).
            output_bitrate: Bitrate for lossy formats.

        Returns:
            tuple: (success: bool, error_message: str or None)
        """
        if not clips:
            return False, "No clips to merge."

        # Build concat entries: (type, value) where type="file" or "silence"
        concat_entries = []
        for clip in clips:
            concat_entries.append(("file", clip.full_path))
            pause_ms = int(clip.pause_after_s * 1000)
            if pause_ms > 0:
                concat_entries.append(("silence", pause_ms))

        try:
            codec_args = _build_codec_args(output_format, output_bitrate)
            success, error = self._merge_with_concat_demuxer(
                concat_entries, str(output_pure), codec_args
            )
            if not success:
                return False, error

            success, error = self._apply_peak_normalize(str(output_pure))
            if not success:
                return False, error

            success, error = self._apply_loudnorm(
                str(output_pure), str(output_loudnorm), loudnorm_lufs, codec_args
            )
            if not success:
                return False, error

            return True, None

        except Exception as e:
            return False, f"Merge failed: {str(e)}"

    def _merge_with_concat_demuxer(self, concat_entries, output_path, codec_args):
        """Merge clips with silence gaps using the ffmpeg concat demuxer."""
        if not any(t == "file" for t, _ in concat_entries):
            return False, "No audio clips to merge."

        startupinfo = _get_subprocess_startupinfo()
        tmpdir = tempfile.mkdtemp(prefix="vcme_merge_")
        try:
            silence_cache = {}

            def get_silence_file(duration_ms):
                if duration_ms in silence_cache:
                    return silence_cache[duration_ms]
                sil_path = os.path.join(tmpdir, f"sil_{duration_ms}.mp3")
                subprocess.run([
                    "ffmpeg", "-f", "lavfi",
                    "-i", "anullsrc=r=48000:cl=mono",
                    "-t", str(duration_ms / 1000.0),
                    "-y", sil_path
                ], check=True, capture_output=True, startupinfo=startupinfo)
                silence_cache[duration_ms] = sil_path
                return sil_path

            list_path = os.path.join(tmpdir, "concat_list.txt")
            with open(list_path, "w", encoding="utf-8") as f:
                for entry_type, value in concat_entries:
                    if entry_type == "file":
                        safe = Path(value).as_posix().replace("'", "\\'")
                        f.write(f"file '{safe}'\n")
                    elif entry_type == "silence":
                        sil = get_silence_file(value)
                        safe = Path(sil).as_posix().replace("'", "\\'")
                        f.write(f"file '{safe}'\n")

            cmd = [
                "ffmpeg", "-f", "concat", "-safe", "0",
                "-i", list_path,
                "-ar", "48000",
            ] + codec_args + ["-y", output_path]

            subprocess.run(cmd, check=True, capture_output=True, text=True,
                           startupinfo=startupinfo)
            return True, None

        except subprocess.CalledProcessError as e:
            return False, f"FFmpeg merge failed: {e.stderr}"
        except FileNotFoundError:
            return False, "FFMPEG not found in PATH."
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def _apply_peak_normalize(self, filepath):
        """Peak-normalize an audio file in-place (overwrites the file)."""
        startupinfo = _get_subprocess_startupinfo()
        try:
            result = subprocess.run([
                "ffmpeg", "-i", filepath,
                "-af", "volumedetect",
                "-f", "null", "-"
            ], capture_output=True, text=True, startupinfo=startupinfo)

            match = re.search(r"max_volume:\s*([-\d.]+)\s*dB", result.stderr)
            if not match:
                return False, "Peak normalize failed: could not read max_volume from ffmpeg output."

            max_volume_db = float(match.group(1))
            if max_volume_db >= 0.0:
                return True, None

            gain_db = -max_volume_db

            with tempfile.NamedTemporaryFile(
                suffix=Path(filepath).suffix or ".mp3", delete=False
            ) as tmp:
                tmp_path = tmp.name

            subprocess.run([
                "ffmpeg", "-i", filepath,
                "-af", f"volume={gain_db}dB",
                "-y", tmp_path
            ], check=True, capture_output=True, text=True, startupinfo=startupinfo)

            os.replace(tmp_path, filepath)
            return True, None
        except subprocess.CalledProcessError as e:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass
            return False, f"Peak normalize failed: {e.stderr}"
        except FileNotFoundError:
            return False, "FFMPEG not found in PATH."

    def _apply_loudnorm(self, input_path, output_path, lufs=-14, codec_args=None):
        """Apply loudness normalization to create the balanced version."""
        if codec_args is None:
            codec_args = ["-c:a", "libmp3lame", "-b:a", "128k"]
        try:
            cmd = [
                "ffmpeg", "-i", input_path,
                "-af", f"loudnorm=I={lufs}:TP=-1.5:LRA=11",
            ] + codec_args + ["-y", output_path]
            subprocess.run(cmd, check=True, capture_output=True, text=True,
                           startupinfo=_get_subprocess_startupinfo())
            return True, None
        except subprocess.CalledProcessError as e:
            return False, f"Loudnorm failed: {e.stderr}"
        except FileNotFoundError:
            return False, "FFMPEG not found in PATH."


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
