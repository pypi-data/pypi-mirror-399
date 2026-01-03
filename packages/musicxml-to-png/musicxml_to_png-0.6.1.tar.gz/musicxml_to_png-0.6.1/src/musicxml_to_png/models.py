"""Shared data models and helpers for MusicXML to PNG conversion."""

from typing import Dict, List, Optional

# Approximated loudness values for common dynamics, clamped to a sane range
DYNAMIC_MARK_LEVELS: Dict[str, float] = {
    "ppp": 0.2,
    "pp": 0.3,
    "p": 0.4,
    "mp": 0.55,
    "mf": 0.7,
    "f": 0.85,
    "ff": 1.0,
    "fff": 1.15,
    "sfz": 1.05,
    "sffz": 1.1,
    "fp": 0.65,
}
MIN_DYNAMIC_LEVEL = 0.2
MAX_DYNAMIC_LEVEL = 1.2
DEFAULT_DYNAMIC_LEVEL = 0.6
DEFAULT_STACCATO_FACTOR = 0.4
MIN_STACCATO_FACTOR = 0.1
MAX_STACCATO_FACTOR = 0.9


def _clamp_dynamic_level(level: float) -> float:
    return max(MIN_DYNAMIC_LEVEL, min(MAX_DYNAMIC_LEVEL, level))


class NoteEvent:
    """Represents a note event for visualization."""

    def __init__(
        self,
        pitch_midi: float,
        start_time: float,
        duration: float,
        instrument_family: str,
        instrument_label: Optional[str] = None,
        dynamic_level: float = DEFAULT_DYNAMIC_LEVEL,
        dynamic_mark: Optional[str] = None,
        pitch_overlap: int = 1,
        original_duration: Optional[float] = None,
    ):
        self.pitch_midi = pitch_midi
        self.start_time = start_time
        self.duration = duration
        self.instrument_family = instrument_family
        self.instrument_label = instrument_label or instrument_family
        self.dynamic_level = dynamic_level
        self.dynamic_mark = dynamic_mark
        self.pitch_overlap = pitch_overlap
        self.original_duration = original_duration if original_duration is not None else duration


class RehearsalMark:
    """Represents a rehearsal letter/number placed on the timeline."""

    def __init__(self, label: str, start_time: float):
        self.label = label
        self.start_time = start_time
