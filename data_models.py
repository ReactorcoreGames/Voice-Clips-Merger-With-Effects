"""
Data models for Voice Clips Merger With Effects (VCME)
"""

from dataclasses import dataclass, field


@dataclass
class SpeakerProfile:
    """Effect settings for a single speaker (VCME — no TTS fields)"""
    display_name: str
    last_seen: str = ""

    # Audio effects
    radio: str = "off"
    reverb: str = "off"
    distortion: str = "off"
    telephone: str = "off"
    robot_voice: str = "off"
    cheap_mic: str = "off"
    underwater: str = "off"
    megaphone: str = "off"
    worn_tape: str = "off"
    intercom: str = "off"
    alien: str = "off"
    cave: str = "off"
    inner_thoughts: str = "off"  # off / Whisper / Dreamlike / Dissociated
    add_noise: str = "off"       # off / White / Pink / Brown

    # Flags
    fmsu: bool = False
    reverse: bool = False

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            "display_name": self.display_name,
            "last_seen": self.last_seen,
            "audio_effects": {
                "radio": self.radio,
                "reverb": self.reverb,
                "distortion": self.distortion,
                "telephone": self.telephone,
                "robot_voice": self.robot_voice,
                "cheap_mic": self.cheap_mic,
                "underwater": self.underwater,
                "megaphone": self.megaphone,
                "worn_tape": self.worn_tape,
                "intercom": self.intercom,
                "alien": self.alien,
                "cave": self.cave,
                "inner_thoughts": self.inner_thoughts,
                "add_noise": self.add_noise,
            },
            "flags": {
                "fmsu": self.fmsu,
                "reverse": self.reverse,
            },
        }

    @classmethod
    def from_dict(cls, data):
        """Create SpeakerProfile from dictionary (loaded from JSON)"""
        effects = data.get("audio_effects", {})
        flags = data.get("flags", {})

        return cls(
            display_name=data.get("display_name", ""),
            last_seen=data.get("last_seen", ""),
            radio=effects.get("radio", "off"),
            reverb=effects.get("reverb", "off"),
            distortion=effects.get("distortion", "off"),
            telephone=effects.get("telephone", "off"),
            robot_voice=effects.get("robot_voice", "off"),
            cheap_mic=effects.get("cheap_mic", "off"),
            underwater=effects.get("underwater", "off"),
            megaphone=effects.get("megaphone", "off"),
            worn_tape=effects.get("worn_tape", "off"),
            intercom=effects.get("intercom", "off"),
            alien=effects.get("alien", "off"),
            cave=effects.get("cave", "off"),
            inner_thoughts=effects.get("inner_thoughts", "off"),
            add_noise=effects.get("add_noise", "off"),
            fmsu=flags.get("fmsu", False),
            reverse=flags.get("reverse", False),
        )


@dataclass
class ClipEntry:
    """Represents a single audio clip in the VCME clip list."""
    filename: str           # Bare filename (no path)
    full_path: str          # Absolute path to the file
    speaker_id: str         # Detected speaker ID, or "" for ungrouped
    pause_after_s: float    # Pause to insert after this clip (from suffix or default)
    included: bool = True   # Whether the clip is included in processing/merge


@dataclass
class ClipList:
    """Complete clip list loaded from a folder."""
    clips: list = field(default_factory=list)    # List[ClipEntry], ordered by filename
    speakers: list = field(default_factory=list) # List[str] unique speaker IDs (excl. "")
    is_grouped: bool = False                     # True if any file starts with @
    skipped_files: list = field(default_factory=list)  # Files skipped (unsupported format)
    folder_path: str = ""
