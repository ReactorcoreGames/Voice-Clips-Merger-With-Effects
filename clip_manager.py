"""
Clip manager for Voice Clips Merger With Effects (VCME).
Handles folder scanning, speaker grouping detection, pause suffix parsing,
and omit filtering.
"""

import re
from pathlib import Path

from data_models import ClipEntry, ClipList

# Audio formats FFMPEG can read (extension whitelist)
SUPPORTED_EXTENSIONS = {
    ".mp3", ".wav", ".ogg", ".flac", ".m4a", ".aiff", ".aif",
    ".opus", ".wma", ".aac", ".mp4", ".webm",
}

# Max pause from suffix (seconds)
_MAX_SUFFIX_PAUSE = 99999.0

# Pattern: _Xs or _X.Xs at end of stem (before extension), e.g. _1s or _0.5s
# Must be the very last _token in the stem.
_PAUSE_SUFFIX_RE = re.compile(r'_(\d+(?:\.\d+)?)s$', re.IGNORECASE)

# Pattern: _@SpeakerID anywhere in the stem (but before the pause suffix).
# Captures the token between _@ and the next _ (or end of string).
# Allows filenames like: 001_line_@Alice_1.5s  or  scene01_@Bob
_SPEAKER_TAG_RE = re.compile(r'_@([^_]+)')


def _strip_pause_suffix(stem: str) -> str:
    """Return stem with the trailing _Xs pause suffix removed (if any)."""
    return _PAUSE_SUFFIX_RE.sub('', stem)


def _parse_speaker(stem: str) -> str:
    """
    Extract speaker ID from filename stem.
    Accepts _@SpeakerID anywhere in the stem (before the pause suffix).
    Also still accepts legacy @SpeakerID_ at the very start.
    Returns "" if no tag found.
    """
    # Strip pause suffix first so it doesn't interfere
    base = _strip_pause_suffix(stem)

    # New format: _@Speaker anywhere (preferred)
    m = _SPEAKER_TAG_RE.search(base)
    if m:
        return m.group(1)

    # Legacy: @Speaker_ at start
    if base.startswith('@'):
        legacy = re.match(r'^@([^_]+)_?', base)
        if legacy:
            return legacy.group(1)

    return ""


def _parse_pause_suffix(stem: str) -> float:
    """
    Extract pause duration from filename stem suffix (_Xs or _X.Xs).
    Returns 0.0 if no suffix found.
    """
    m = _PAUSE_SUFFIX_RE.search(stem)
    if not m:
        return 0.0
    val = float(m.group(1))
    return min(val, _MAX_SUFFIX_PAUSE)


def scan_folder(folder_path: str, default_gap_s: float = 0.0) -> ClipList:
    """
    Scan a folder for audio clips and return a ClipList.

    Clips are ordered alphanumerically by filename (case-insensitive).
    Speaker grouping is activated when any file contains a _@Speaker tag
    (anywhere in the stem) or a legacy @Speaker_ prefix at the start.
    Unsupported files are collected in skipped_files.

    Args:
        folder_path: Path to the folder to scan.
        default_gap_s: Default inter-clip gap in seconds (used when no suffix found).

    Returns:
        ClipList with all detected clips.
    """
    folder = Path(folder_path)
    if not folder.is_dir():
        return ClipList(folder_path=folder_path)

    all_files = sorted(
        (f for f in folder.iterdir() if f.is_file()),
        key=lambda f: f.name.lower()
    )

    clips = []
    skipped = []
    has_speaker_prefix = False

    for f in all_files:
        ext = f.suffix.lower()
        if ext not in SUPPORTED_EXTENSIONS:
            skipped.append(f.name)
            continue

        stem = f.stem
        speaker_id = _parse_speaker(stem)
        if speaker_id:
            has_speaker_prefix = True

        pause_s = _parse_pause_suffix(stem)
        if pause_s == 0.0:
            pause_s = default_gap_s

        clips.append(ClipEntry(
            filename=f.name,
            full_path=str(f),
            speaker_id=speaker_id,
            pause_after_s=pause_s,
            included=True,
        ))

    # Grouped mode: only if at least one file has @prefix
    is_grouped = has_speaker_prefix

    # Collect unique speaker IDs in order of first appearance
    seen = []
    for clip in clips:
        if clip.speaker_id and clip.speaker_id not in seen:
            seen.append(clip.speaker_id)

    return ClipList(
        clips=clips,
        speakers=seen,
        is_grouped=is_grouped,
        skipped_files=skipped,
        folder_path=str(folder),
    )


def get_included_clips(clip_list: ClipList) -> list:
    """Return only the included ClipEntry objects, in order."""
    return [c for c in clip_list.clips if c.included]
