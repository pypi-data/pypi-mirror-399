"""Extraction helpers: measure timelines, rehearsal marks, and note events."""

from typing import Dict, List, Optional, Tuple

from music21 import chord, dynamics, expressions, instrument, note, stream

from musicxml_to_png.instruments import get_instrument_family
from musicxml_to_png.models import (
    DEFAULT_DYNAMIC_LEVEL,
    MAX_DYNAMIC_LEVEL,
    MIN_DYNAMIC_LEVEL,
    DYNAMIC_MARK_LEVELS,
    NoteEvent,
    RehearsalMark,
    _clamp_dynamic_level,
)


def _build_measure_offset_map(score: stream.Score) -> tuple[Dict[str, float], float]:
    """
    Build a map of measure start offsets (in quarter lengths) using a
    conservative, cross-part approach that favors the shortest duration seen
    for each measure number. This prevents parts with missing or inflated
    time signatures from pushing their entries late.
    
    Returns:
        measure_offsets: mapping of measure number -> absolute start time
        total_duration: cumulative duration of all measures encountered
    """
    measure_lengths: Dict[str, List[float]] = {}
    measure_order: List[str] = []

    for part in score.parts:
        for measure in part.getElementsByClass(stream.Measure):
            measure_num = str(measure.number)
            duration = None
            if measure.barDuration is not None:
                duration = float(measure.barDuration.quarterLength)
            elif measure.duration is not None:
                duration = float(measure.duration.quarterLength)

            if duration is None:
                continue

            measure_lengths.setdefault(measure_num, []).append(duration)
            if measure_num not in measure_order:
                measure_order.append(measure_num)

    if not measure_lengths:
        return {}, float(score.duration.quarterLength)

    # Use the shortest duration seen for each measure to avoid inflated bars
    canonical_lengths: Dict[str, float] = {
        num: min(durations) for num, durations in measure_lengths.items()
    }

    measure_offsets: Dict[str, float] = {}
    current_offset = 0.0
    for measure_num in measure_order:
        measure_offsets[measure_num] = current_offset
        current_offset += canonical_lengths.get(measure_num, 0.0)

    return measure_offsets, current_offset


def _absolute_offset_from_measure(
    element,
    score: stream.Score,
    measure_offsets: Dict[str, float],
) -> float:
    """
    Compute an absolute offset using canonical measure offsets when available.
    Falls back to music21 hierarchy offsets if the measure is unknown.
    """
    measure = element.getContextByClass(stream.Measure)
    measure_num = measure.number if measure is not None else getattr(element, "measureNumber", None)
    inner_offset = float(getattr(element, "offset", 0.0))

    if measure_num is not None:
        key = str(measure_num)
        if key in measure_offsets:
            return measure_offsets[key] + inner_offset

    return float(element.getOffsetInHierarchy(score))


def extract_rehearsal_marks(
    score: stream.Score,
    measure_offsets: Optional[Dict[str, float]] = None,
) -> List[RehearsalMark]:
    """
    Extract rehearsal marks (letters/numbers) from the first part of the score.
    """
    if not score.parts:
        return []

    measure_offsets = measure_offsets or _build_measure_offset_map(score)[0]
    part = score.parts[0]
    rehearsal_marks: List[RehearsalMark] = []

    for mark in part.recurse().getElementsByClass(expressions.RehearsalMark):
        label = str(mark.content).strip() if getattr(mark, "content", None) else str(mark).strip()
        if not label:
            continue
        start_time = _absolute_offset_from_measure(mark, score, measure_offsets)
        rehearsal_marks.append(RehearsalMark(label=label, start_time=start_time))

    return rehearsal_marks


def extract_notes(
    score: stream.Score,
    ensemble: str,
    measure_offsets: Optional[Dict[str, float]] = None,
) -> List[NoteEvent]:
    """
    Extract note events from a music21 Score.
    """
    measure_offsets, _ = (
        _build_measure_offset_map(score) if measure_offsets is None else (measure_offsets, None)
    )

    note_events = []
    instrument_label_counts = {}

    for part_index, part in enumerate(score.parts, start=1):
        part_instrument = None
        midi_program = None
        instrument_name = None
        instrument_label = None

        for element in part.recurse().getElementsByClass(instrument.Instrument):
            part_instrument = element
            if hasattr(element, "midiProgram") and element.midiProgram is not None:
                midi_program = element.midiProgram
            if hasattr(element, "instrumentName") and element.instrumentName:
                instrument_name = str(element.instrumentName)
            break

        if part_instrument is None and part.partName:
            instrument_name = str(part.partName)

        base_label = (instrument_name or part.partName or f"Instrument {part_index}").strip()
        if not base_label:
            base_label = f"Instrument {part_index}"

        if ensemble == "ungrouped":
            count = instrument_label_counts.get(base_label, 0) + 1
            instrument_label_counts[base_label] = count
            instrument_label = base_label if count == 1 else f"{base_label} {count}"
            instrument_family = instrument_label
        else:
            instrument_family = get_instrument_family(
                midi_program=midi_program,
                instrument_name=instrument_name,
                ensemble=ensemble,
            )
            instrument_label = base_label

        note_data = []

        for element in part.recurse().notes:
            absolute_offset = _absolute_offset_from_measure(element, score, measure_offsets)

            if isinstance(element, note.Note):
                pitch_obj = element.pitch
                if pitch_obj.midi is not None:
                    tie_type = element.tie.type if element.tie is not None else None
                    note_data.append(
                        (
                            float(pitch_obj.midi),
                            absolute_offset,
                            float(element.quarterLength),
                            tie_type,
                            element,
                        )
                    )
            elif isinstance(element, chord.Chord):
                for pitch_obj in element.pitches:
                    if pitch_obj.midi is not None:
                        tie_type = element.tie.type if element.tie is not None else None
                        note_data.append(
                            (
                                float(pitch_obj.midi),
                                absolute_offset,
                                float(element.quarterLength),
                                tie_type,
                                element,
                            )
                        )
            elif isinstance(element, note.Rest):
                continue

        processed_indices = set()

        dynamic_timeline = []
        for dyn in part.recurse().getElementsByClass(dynamics.Dynamic):
            dyn_offset = _absolute_offset_from_measure(dyn, score, measure_offsets)
            dyn_mark = None
            if hasattr(dyn, "value") and dyn.value is not None:
                dyn_mark = str(dyn.value).lower()
            level = DYNAMIC_MARK_LEVELS.get(dyn_mark, DEFAULT_DYNAMIC_LEVEL)
            dynamic_timeline.append((dyn_offset, level, dyn_mark))
        dynamic_timeline.sort(key=lambda item: item[0])

        def get_dynamic_at(offset: float, element) -> tuple[float, Optional[str]]:
            level = None
            mark = None
            for dyn_offset, dyn_level, dyn_mark in reversed(dynamic_timeline):
                if dyn_offset <= offset:
                    level = dyn_level
                    mark = dyn_mark
                    break
            if level is None:
                level = DEFAULT_DYNAMIC_LEVEL

            velocity_level = None
            volume = getattr(element, "volume", None)
            if volume:
                if volume.velocity is not None:
                    vel_norm = max(0.0, min(1.0, volume.velocity / 127.0))
                    velocity_level = MIN_DYNAMIC_LEVEL + vel_norm * (MAX_DYNAMIC_LEVEL - MIN_DYNAMIC_LEVEL)
                elif volume.velocityScalar is not None:
                    vel_norm = max(0.0, min(1.0, float(volume.velocityScalar)))
                    velocity_level = MIN_DYNAMIC_LEVEL + vel_norm * (MAX_DYNAMIC_LEVEL - MIN_DYNAMIC_LEVEL)
            if velocity_level is not None:
                level = max(level, velocity_level)

            return _clamp_dynamic_level(level), mark

        for i, (pitch_midi, offset, duration, tie_type, element) in enumerate(note_data):
            if i in processed_indices:
                continue

            if tie_type == "start":
                total_duration = duration
                dynamic_level, dynamic_mark = get_dynamic_at(offset, element)

                for j, (
                    other_pitch,
                    other_offset,
                    other_duration,
                    other_tie_type,
                    _,
                ) in enumerate(note_data[i + 1 :], start=i + 1):
                    if j in processed_indices:
                        continue

                    if (other_pitch == pitch_midi and other_tie_type == "stop" and other_offset >= offset):
                        total_duration += other_duration
                        processed_indices.add(j)
                        break
                    elif other_pitch == pitch_midi and other_tie_type == "start":
                        break

                note_events.append(
                    NoteEvent(
                        pitch_midi=pitch_midi,
                        start_time=offset,
                        duration=total_duration,
                        instrument_family=instrument_family,
                        instrument_label=instrument_label,
                        dynamic_level=dynamic_level,
                        dynamic_mark=dynamic_mark,
                    )
                )
                processed_indices.add(i)
            elif tie_type == "stop":
                if i not in processed_indices:
                    dynamic_level, dynamic_mark = get_dynamic_at(offset, element)
                    note_events.append(
                        NoteEvent(
                            pitch_midi=pitch_midi,
                            start_time=offset,
                            duration=duration,
                            instrument_family=instrument_family,
                            instrument_label=instrument_label,
                            dynamic_level=dynamic_level,
                            dynamic_mark=dynamic_mark,
                        )
                    )
                    processed_indices.add(i)
            else:
                dynamic_level, dynamic_mark = get_dynamic_at(offset, element)
                note_events.append(
                    NoteEvent(
                        pitch_midi=pitch_midi,
                        start_time=offset,
                        duration=duration,
                        instrument_family=instrument_family,
                        instrument_label=instrument_label,
                        dynamic_level=dynamic_level,
                        dynamic_mark=dynamic_mark,
                    )
                )
                processed_indices.add(i)

    overlap_counts = [1] * len(note_events)
    events_by_pitch: Dict[float, List[tuple[int, NoteEvent]]] = {}
    for idx, event in enumerate(note_events):
        events_by_pitch.setdefault(event.pitch_midi, []).append((idx, event))

    for events in events_by_pitch.values():
        events.sort(key=lambda item: (item[1].start_time, item[0]))
        active: List[tuple[int, float]] = []
        for idx, event in events:
            current_start = event.start_time
            current_end = event.start_time + event.duration
            active = [(i, end) for i, end in active if end > current_start]
            current_overlap = len(active) + 1
            overlap_counts[idx] = max(overlap_counts[idx], current_overlap)

            updated_active: List[tuple[int, float]] = []
            for active_idx, end_time in active:
                overlap_counts[active_idx] = max(overlap_counts[active_idx], current_overlap)
                updated_active.append((active_idx, end_time))
            updated_active.append((idx, current_end))
            active = updated_active

    for idx, event in enumerate(note_events):
        event.pitch_overlap = overlap_counts[idx]

    return note_events


# Public aliases for external imports
build_measure_offset_map = _build_measure_offset_map
absolute_offset_from_measure = _absolute_offset_from_measure

