"""Extraction helpers: measure timelines, rehearsal marks, and note events."""

from typing import Dict, List, Optional, Tuple

from music21 import chord, dynamics, expressions, instrument, note, stream, articulations

from musicxml_to_png.instruments import get_instrument_family
from musicxml_to_png.models import (
    DEFAULT_DYNAMIC_LEVEL,
    MAX_DYNAMIC_LEVEL,
    MIN_DYNAMIC_LEVEL,
    DYNAMIC_MARK_LEVELS,
    NoteEvent,
    RehearsalMark,
    _clamp_dynamic_level,
    DEFAULT_STACCATO_FACTOR,
    MIN_STACCATO_FACTOR,
    MAX_STACCATO_FACTOR,
)

# Small tolerance for matching adjacent note timings to avoid float drift in connections
# EPS means epsilon (small difference)
CONNECTION_TIME_EPS = 0.001


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


def _split_events_by_pitch_overlap(note_events: List[NoteEvent]) -> List[NoteEvent]:
    """
    Split note events whenever the number of active notes on the same pitch changes,
    so overlap height only applies to the portion that is truly stacked.
    """
    events_by_pitch: Dict[float, List[NoteEvent]] = {}
    for event in note_events:
        events_by_pitch.setdefault(event.pitch_midi, []).append(event)

    split_events: List[NoteEvent] = []

    for events in events_by_pitch.values():
        boundaries = set()
        for event in events:
            start = event.start_time
            end = event.start_time + event.duration
            boundaries.add(start)
            boundaries.add(end)

        sorted_boundaries = sorted(boundaries)

        if len(sorted_boundaries) < 2:
            for event in events:
                split_events.append(
                    NoteEvent(
                        pitch_midi=event.pitch_midi,
                        start_time=event.start_time,
                        duration=event.duration,
                        instrument_family=event.instrument_family,
                        instrument_label=event.instrument_label,
                        dynamic_level=event.dynamic_level,
                        dynamic_mark=event.dynamic_mark,
                        pitch_overlap=len(events),
                        original_duration=event.original_duration,
                    )
                )
            continue

        for i in range(len(sorted_boundaries) - 1):
            segment_start = sorted_boundaries[i]
            segment_end = sorted_boundaries[i + 1]
            if segment_end <= segment_start:
                continue

            active_events = [
                event
                for event in events
                if event.start_time < segment_end and (event.start_time + event.duration) > segment_start
            ]
            if not active_events:
                continue

            overlap = len(active_events)
            for event in active_events:
                clipped_start = max(segment_start, event.start_time)
                clipped_end = min(segment_end, event.start_time + event.duration)
                if clipped_end <= clipped_start:
                    continue

                # Calculate original_duration for the clipped segment
                # The key insight: we need to preserve where the note originally ended
                # relative to the segment, not clip it to the visual duration boundaries
                # For connection detection: clipped_start + clipped_original_duration should 
                # equal where the note originally ended relative to segment_start
                original_end_absolute = event.start_time + event.original_duration
                clipped_original_duration = max(0.0, original_end_absolute - clipped_start)

                split_events.append(
                    NoteEvent(
                        pitch_midi=event.pitch_midi,
                        start_time=clipped_start,
                        duration=clipped_end - clipped_start,
                        instrument_family=event.instrument_family,
                        instrument_label=event.instrument_label,
                        dynamic_level=event.dynamic_level,
                        dynamic_mark=event.dynamic_mark,
                        pitch_overlap=overlap,
                        original_duration=clipped_original_duration,
                    )
                )

    split_events.sort(key=lambda e: (e.start_time, e.pitch_midi, e.instrument_label))

    return split_events


def _assign_pitch_overlap_unsplit(note_events: List[NoteEvent]) -> List[NoteEvent]:
    """
    Legacy behavior: mark pitch_overlap on entire notes without splitting them.
    """
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


def _clip_to_window(note_events: List[NoteEvent], window_start: float, window_end: float) -> List[NoteEvent]:
    """
    Clip note events to a time window and re-base start times to window_start.
    """
    if window_start is None or window_end is None:
        return note_events

    clipped: List[NoteEvent] = []
    for event in note_events:
        ev_start = event.start_time
        ev_end = event.start_time + event.duration
        if ev_end <= window_start or ev_start >= window_end:
            continue

        new_start = max(ev_start, window_start) - window_start
        new_end = min(ev_end, window_end) - window_start
        duration = new_end - new_start
        if duration <= 0:
            continue

        # Calculate original_duration for the clipped segment
        # We need to preserve where the note originally ended for connection detection
        # The key: clipped_start + clipped_original_duration should equal original_end - window_start
        original_start = event.start_time
        original_end = event.start_time + event.original_duration
        
        # Calculate where the note originally ended relative to the window start
        original_end_relative = original_end - window_start
        
        # clipped_original_duration should make clipped_start + clipped_original_duration = original_end_relative
        clipped_original_duration = max(0.0, original_end_relative - new_start)

        clipped.append(
            NoteEvent(
                pitch_midi=event.pitch_midi,
                start_time=new_start,
                duration=duration,
                instrument_family=event.instrument_family,
                instrument_label=event.instrument_label,
                dynamic_level=event.dynamic_level,
                dynamic_mark=event.dynamic_mark,
                pitch_overlap=event.pitch_overlap,
                original_duration=clipped_original_duration,
            )
        )
    return clipped


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
    split_overlaps: bool = True,
    staccato_factor: float = DEFAULT_STACCATO_FACTOR,
    slice_window: Optional[Tuple[float, float]] = None,
) -> List[NoteEvent]:
    """
    Extract note events from a music21 Score.
    """
    staccato_factor = max(MIN_STACCATO_FACTOR, min(MAX_STACCATO_FACTOR, staccato_factor))
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
                    original_duration = float(element.quarterLength)
                    is_staccato = any(isinstance(art, articulations.Staccato) for art in element.articulations)
                    effective_duration = original_duration * (staccato_factor if is_staccato else 1.0)
                    tie_type = element.tie.type if element.tie is not None else None
                    note_data.append(
                        (
                            float(pitch_obj.midi),
                            absolute_offset,
                            effective_duration,
                            original_duration,
                            tie_type,
                            element,
                        )
                    )
            elif isinstance(element, chord.Chord):
                for pitch_obj in element.pitches:
                    if pitch_obj.midi is not None:
                        original_duration = float(element.quarterLength)
                        is_staccato = any(isinstance(art, articulations.Staccato) for art in element.articulations)
                        effective_duration = original_duration * (staccato_factor if is_staccato else 1.0)
                        tie_type = element.tie.type if element.tie is not None else None
                        note_data.append(
                            (
                                float(pitch_obj.midi),
                                absolute_offset,
                                effective_duration,
                                original_duration,
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

        for i, (pitch_midi, offset, duration, original_duration, tie_type, element) in enumerate(note_data):
            if i in processed_indices:
                continue

            if tie_type == "start":
                total_duration = duration
                total_original_duration = original_duration
                dynamic_level, dynamic_mark = get_dynamic_at(offset, element)

                for j, (
                    other_pitch,
                    other_offset,
                    other_duration,
                    other_original_duration,
                    other_tie_type,
                    _,
                ) in enumerate(note_data[i + 1 :], start=i + 1):
                    if j in processed_indices:
                        continue

                    if (other_pitch == pitch_midi and other_tie_type == "stop" and other_offset >= offset):
                        total_duration += other_duration
                        total_original_duration += other_original_duration
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
                        original_duration=total_original_duration,
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
                            original_duration=original_duration,
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
                        original_duration=original_duration,
                    )
                )
                processed_indices.add(i)

    if slice_window is not None:
        note_events = _clip_to_window(note_events, slice_window[0], slice_window[1])

    if split_overlaps:
        return _split_events_by_pitch_overlap(note_events)
    return _assign_pitch_overlap_unsplit(note_events)


def detect_note_connections(note_events: List[NoteEvent]) -> List[Tuple[int, int]]:
    """
    Detect connections between adjacent notes (no rest between) per instrument.
    
    Two notes are connected if note1.start_time + note1.original_duration == note2.start_time
    and they belong to the same instrument.
    
    Returns:
        List of tuples (note1_index, note2_index) representing connections.
    """
    connections: List[Tuple[int, int]] = []
    
    # Group notes by instrument
    notes_by_instrument: Dict[str, List[Tuple[int, NoteEvent]]] = {}
    for idx, event in enumerate(note_events):
        instrument_key = event.instrument_label
        if instrument_key not in notes_by_instrument:
            notes_by_instrument[instrument_key] = []
        notes_by_instrument[instrument_key].append((idx, event))
    
    # For each instrument, find adjacent notes
    for instrument_notes in notes_by_instrument.values():
        # Sort by start_time, then by pitch for consistent ordering
        instrument_notes.sort(key=lambda item: (item[1].start_time, item[1].pitch_midi))

        # Deduplicate split segments from the same underlying note (same pitch, same original end)
        dedup_map: Dict[Tuple[float, float], Tuple[int, NoteEvent]] = {}
        for idx, ev in instrument_notes:
            original_end = ev.start_time + ev.original_duration
            quantized_end = round(original_end / CONNECTION_TIME_EPS) * CONNECTION_TIME_EPS
            key = (ev.pitch_midi, quantized_end)
            # Keep the latest segment for this underlying note so connections start at the actual end
            current = dedup_map.get(key)
            if current is None or ev.start_time >= current[1].start_time:
                dedup_map[key] = (idx, ev)

        deduped_notes: List[Tuple[int, NoteEvent]] = sorted(
            dedup_map.values(),
            key=lambda item: (item[1].start_time, item[1].pitch_midi),
        )

        connected_target_starts: set[float] = set()

        for i in range(len(deduped_notes) - 1):
            idx1, note1 = deduped_notes[i]
            
            # Check all subsequent notes to find the one that starts exactly where this one ends
            # (handles cases where multiple notes might start at the same time)
            note1_end = note1.start_time + note1.original_duration
            
            for j in range(i + 1, len(deduped_notes)):
                idx2, note2 = deduped_notes[j]
                note2_start = note2.start_time
                
                # If note2 starts after note1 ends, no need to check further (sorted by start_time)
                if note2_start > note1_end + CONNECTION_TIME_EPS:
                    break
                
                # Only connect notes on different pitches
                # Notes on the same pitch that are adjacent are likely overlapping segments
                # from split_overlaps, not sequential notes
                if note1.pitch_midi == note2.pitch_midi:
                    continue
                
                # Check if notes are adjacent (no rest between)
                # Use small epsilon for floating point comparison
                if abs(note1_end - note2_start) < CONNECTION_TIME_EPS:
                    target_key = round(note2_start / CONNECTION_TIME_EPS) * CONNECTION_TIME_EPS
                    if target_key in connected_target_starts:
                        break  # already connected to a note starting here; avoid duplicate lines
                    connected_target_starts.add(target_key)
                    connections.append((idx1, idx2))
                    break  # Only connect to the first note that starts at this position
    
    return connections


# Public aliases for external imports
build_measure_offset_map = _build_measure_offset_map
absolute_offset_from_measure = _absolute_offset_from_measure
