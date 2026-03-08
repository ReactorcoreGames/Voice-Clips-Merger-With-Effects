"""
Config file manager for Voice Clips Merger With Effects (VCME).
Handles loading/saving config.json with atomic writes and validation.
"""

import json
import os
import tempfile
from pathlib import Path

from config import (
    UI_DEFAULTS,
    VCME_SETTINGS_DEFAULTS,
    INNER_THOUGHTS_PRESETS,
    INNER_THOUGHTS_DEFAULT_PRESET,
)

CURRENT_SCHEMA_VERSION = 2


def _get_config_path():
    """Get path to config.json alongside the script/executable."""
    import sys
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent / "config.json"
    return Path(__file__).parent / "config.json"


def _build_defaults():
    """Build a complete default config dictionary."""
    return {
        "schema_version": CURRENT_SCHEMA_VERSION,
        "ui": dict(UI_DEFAULTS),
        "settings": dict(VCME_SETTINGS_DEFAULTS),
    }


def _clamp(value, low, high):
    try:
        v = float(value)
        return max(low, min(high, v))
    except (TypeError, ValueError):
        return low


def _validate_and_fill(config):
    """Validate a loaded config dict; fill missing keys with defaults."""
    defaults = _build_defaults()

    for section in ("ui", "settings"):
        if section not in config or not isinstance(config[section], dict):
            config[section] = dict(defaults[section])
        else:
            for key, default_val in defaults[section].items():
                if key not in config[section]:
                    config[section][key] = default_val

    s = config["settings"]
    s["default_gap_ms"] = int(_clamp(s.get("default_gap_ms", 0), 0, 2000))
    s["trim_leading"] = bool(s.get("trim_leading", False))
    s["trim_trailing"] = bool(s.get("trim_trailing", False))
    s["output_format"] = s.get("output_format", "mp3") if s.get("output_format") in ("mp3", "ogg", "flac", "wav", "m4a") else "mp3"
    s["output_bitrate"] = s.get("output_bitrate", "128k") if s.get("output_bitrate") in ("32k", "64k", "128k", "192k", "320k") else "128k"
    s["loudnorm_lufs"] = int(s.get("loudnorm_lufs", -14)) if int(s.get("loudnorm_lufs", -14)) in (-23, -16, -14, -11) else -14
    s["reverb_room_size"] = _clamp(s.get("reverb_room_size", 0.5), 0.0, 1.0)
    s["distortion_drive"] = _clamp(s.get("distortion_drive", 0.5), 0.0, 1.0)
    s["noise_intensity"] = _clamp(s.get("noise_intensity", 0.5), 0.0, 1.0)

    config.setdefault("schema_version", CURRENT_SCHEMA_VERSION)
    return config


def _atomic_write(path, data):
    """Write JSON atomically: write to temp file then rename."""
    dir_path = path.parent
    try:
        fd, tmp_path = tempfile.mkstemp(dir=str(dir_path), suffix=".tmp")
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        if path.exists():
            path.unlink()
        os.rename(tmp_path, str(path))
    except Exception:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass
        raise


class ConfigManager:
    """Manages the config.json file for VCME."""

    def __init__(self):
        self.path = _get_config_path()
        self.config = self.load()

    def load(self):
        """Load config from disk. Creates default if missing/malformed."""
        if not self.path.exists():
            config = _build_defaults()
            self._save(config)
            return config

        try:
            with open(self.path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except (json.JSONDecodeError, OSError):
            config = _build_defaults()
            self._save(config)
            return config

        file_version = config.get("schema_version", 1)
        if file_version > CURRENT_SCHEMA_VERSION:
            print(f"Warning: config.json schema_version {file_version} "
                  f"is newer than this program knows ({CURRENT_SCHEMA_VERSION}).")

        config = _validate_and_fill(config)
        self._save(config)
        return config

    def _save(self, config=None):
        if config is None:
            config = self.config
        _atomic_write(self.path, config)

    def save(self):
        """Public save — writes current config to disk."""
        self._save(self.config)

    # ── UI persistence ─────────────────────────────────────────

    def get_ui(self, key):
        return self.config["ui"].get(key, UI_DEFAULTS.get(key, ""))

    def set_ui(self, key, value):
        self.config["ui"][key] = value
        self.save()

    # ── Generation settings ────────────────────────────────────

    def get_setting(self, key):
        return self.config["settings"].get(key, VCME_SETTINGS_DEFAULTS.get(key))

    def set_setting(self, key, value):
        self.config["settings"][key] = value
        self.save()

    # ── Inner thoughts filter (used by audio_generator) ────────

    def get_inner_thoughts_filter(self, preset_name: str) -> str:
        """
        Build and return the FFMPEG filter string for the given inner thoughts preset.
        preset_name: "Whisper" | "Dreamlike" | "Dissociated"
        """
        if preset_name not in INNER_THOUGHTS_PRESETS:
            preset_name = INNER_THOUGHTS_DEFAULT_PRESET
        p = INNER_THOUGHTS_PRESETS[preset_name]
        params = {
            "highpass": p["highpass"],
            "lowpass": p["lowpass"],
            "echo_delay_ms": p["echo_delay_ms"],
            "echo_wet": p["echo_wet"],
            "volume": p["volume"],
            "_reverb": p.get("reverb", False),
            "_dreamlike": p.get("dreamlike", False),
        }
        return _build_inner_thoughts_filter(params)


def _build_inner_thoughts_filter(params):
    """Build an FFMPEG filter string from inner thoughts parameters."""
    filters = []
    filters.append(f"highpass=f={int(params['highpass'])}")
    filters.append(f"lowpass=f={int(params['lowpass'])}")

    delay_ms = int(params.get("echo_delay_ms", 0))
    reverb = params.get("_reverb", False)
    dreamlike = params.get("_dreamlike", False)

    if dreamlike:
        filters.append("aecho=0.85:0.7:150|280:0.35|0.2")
    elif reverb:
        filters.append("aecho=0.8:0.88:45:0.28")
    elif delay_ms > 0:
        wet = float(params.get("echo_wet", 0.2))
        wet = max(0.0, min(1.0, wet))
        filters.append(f"aecho=0.6:0.3:{delay_ms}:{wet:.2f}")

    vol = float(params.get("volume", 0.75))
    vol = max(0.1, min(2.0, vol))
    filters.append(f"volume={vol:.2f}")

    return ",".join(filters)
