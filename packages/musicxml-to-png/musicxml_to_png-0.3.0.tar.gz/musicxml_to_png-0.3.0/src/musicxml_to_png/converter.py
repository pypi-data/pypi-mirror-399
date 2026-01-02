"""Core conversion logic for MusicXML to PNG."""

from pathlib import Path
from typing import Dict, List, Optional

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from music21 import converter, stream, note, instrument, pitch, chord, dynamics

from musicxml_to_png.instruments import (
    get_instrument_family,
    get_family_color,
    get_individual_color,
    ENSEMBLE_UNGROUPED,
    ENSEMBLE_ORCHESTRA,
    ENSEMBLE_BIGBAND,
    # Orchestra families
    ORCHESTRA_STRINGS,
    ORCHESTRA_WINDS,
    ORCHESTRA_BRASS,
    ORCHESTRA_PERCUSSION,
    ORCHESTRA_UNKNOWN,
    # Bigband families
    BIGBAND_TRUMPETS,
    BIGBAND_TROMBONES,
    BIGBAND_SAXOPHONES,
    BIGBAND_RHYTHM_SECTION,
    BIGBAND_UNKNOWN,
)


class NoteEvent:
    """Represents a note event for visualization."""

    def __init__(
        self,
        pitch_midi: float,
        start_time: float,
        duration: float,
        instrument_family: str,
        instrument_label: Optional[str] = None,
        dynamic_level: float = 0.6,
        dynamic_mark: Optional[str] = None,
        pitch_overlap: int = 1,
    ):
        self.pitch_midi = pitch_midi
        self.start_time = start_time
        self.duration = duration
        self.instrument_family = instrument_family
        # Default label to family if none is supplied (useful for per-instrument mode)
        self.instrument_label = instrument_label or instrument_family
        # Normalized loudness derived from dynamics markings or velocity
        self.dynamic_level = dynamic_level
        # Raw dynamic marking (e.g., mf, f) when available
        self.dynamic_mark = dynamic_mark
        # Count of simultaneous notes at the same pitch (1 = solo)
        self.pitch_overlap = pitch_overlap


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


def _clamp_dynamic_level(level: float) -> float:
    return max(MIN_DYNAMIC_LEVEL, min(MAX_DYNAMIC_LEVEL, level))


def extract_notes(score: stream.Score, ensemble: str = ENSEMBLE_UNGROUPED) -> List[NoteEvent]:
    """
    Extract note events from a music21 Score.
    
    Args:
        score: music21 Score object
        ensemble: Ensemble type (ungrouped, orchestra, or bigband)
    
    Returns:
        List of NoteEvent objects
    """
    note_events = []
    instrument_label_counts = {}
    
    # Iterate through all parts in the score
    for part_index, part in enumerate(score.parts, start=1):
        # Get instrument information
        part_instrument = None
        midi_program = None
        instrument_name = None
        instrument_label = None
        
        # Try to get instrument from the part
        for element in part.recurse().getElementsByClass(instrument.Instrument):
            part_instrument = element
            if hasattr(element, "midiProgram") and element.midiProgram is not None:
                midi_program = element.midiProgram
            if hasattr(element, "instrumentName") and element.instrumentName:
                instrument_name = str(element.instrumentName)
            break
        
        # If no instrument found, try to infer from part name
        if part_instrument is None and part.partName:
            instrument_name = str(part.partName)
        
        # Build a base label for this instrument/part
        base_label = (instrument_name or part.partName or f"Instrument {part_index}").strip()
        if not base_label:
            base_label = f"Instrument {part_index}"
        
        # Determine instrument grouping based on ensemble
        if ensemble == ENSEMBLE_UNGROUPED:
            # Keep labels unique even for duplicate instruments (Flute, Flute 2, etc.)
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
        
        # Extract notes from this part with tie information
        # First pass: collect all notes with their tie information
        note_data = []  # List of (pitch_midi, offset, duration, tie_type, element)
        
        for element in part.recurse().notes:
            # Get absolute offset from the start of the score
            absolute_offset = float(element.getOffsetInHierarchy(score))
            
            if isinstance(element, note.Note):
                # Single note
                pitch_obj = element.pitch
                if pitch_obj.midi is not None:
                    tie_type = element.tie.type if element.tie is not None else None
                    note_data.append((
                        float(pitch_obj.midi),
                        absolute_offset,
                        float(element.quarterLength),
                        tie_type,
                        element,
                    ))
            elif isinstance(element, chord.Chord):
                # Chord - each pitch can have its own tie
                for pitch_obj in element.pitches:
                    if pitch_obj.midi is not None:
                        # For chords, check if this specific pitch has a tie
                        # music21 stores ties per pitch in chords
                        tie_type = None
                        if element.tie is not None:
                            tie_type = element.tie.type
                        # Also check individual note ties if available
                        # (chords can have ties on individual pitches)
                        note_data.append((
                            float(pitch_obj.midi),
                            absolute_offset,
                            float(element.quarterLength),
                            tie_type,
                            element,
                        ))
            elif isinstance(element, note.Rest):
                # Skip rests
                continue
        
        # Second pass: merge tied notes
        # Track which notes have been processed as part of a tie
        processed_indices = set()

        # Build a simple dynamic timeline for this part so we can grab the most recent marking
        dynamic_timeline = []
        for dyn in part.recurse().getElementsByClass(dynamics.Dynamic):
            dyn_offset = float(dyn.getOffsetInHierarchy(score))
            dyn_mark = None
            if hasattr(dyn, "value") and dyn.value is not None:
                dyn_mark = str(dyn.value).lower()
            level = DYNAMIC_MARK_LEVELS.get(dyn_mark, DEFAULT_DYNAMIC_LEVEL)
            dynamic_timeline.append((dyn_offset, level, dyn_mark))
        dynamic_timeline.sort(key=lambda item: item[0])

        def get_dynamic_at(offset: float, element) -> tuple[float, Optional[str]]:
            """Return (level, mark) for a given absolute offset."""
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
            
            # If this note starts a tie, find all connected tied notes
            if tie_type == 'start':
                total_duration = duration
                dynamic_level, dynamic_mark = get_dynamic_at(offset, element)
                
                # Find the tie stop note (same pitch, later offset)
                for j, (other_pitch, other_offset, other_duration, other_tie_type, _) in enumerate(note_data[i+1:], start=i+1):
                    if j in processed_indices:
                        continue
                    
                    # Check if this is the tie stop for the same pitch
                    if (other_pitch == pitch_midi and 
                        other_tie_type == 'stop' and
                        other_offset >= offset):
                        total_duration += other_duration
                        processed_indices.add(j)
                        break
                    # If we encounter another tie start for the same pitch before finding stop,
                    # that's an error case, but we'll just use what we have
                    elif other_pitch == pitch_midi and other_tie_type == 'start':
                        break
                
                # Create merged NoteEvent
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
            elif tie_type == 'stop':
                # Skip tie stop notes - they should have been merged with their start note
                # Check if this stop was already processed (merged with a start)
                # If not, it's an orphaned stop (no matching start found earlier)
                # In valid MusicXML this shouldn't happen, but handle gracefully
                if i not in processed_indices:
                    dynamic_level, dynamic_mark = get_dynamic_at(offset, element)
                    # Orphaned stop - treat as regular note (defensive programming)
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
                # No tie - create NoteEvent as normal
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

    # Annotate overlapping notes at the same pitch so we can visualize stacking
    overlap_counts = [1] * len(note_events)
    events_by_pitch: Dict[float, List[tuple[int, NoteEvent]]] = {}
    for idx, event in enumerate(note_events):
        events_by_pitch.setdefault(event.pitch_midi, []).append((idx, event))

    for events in events_by_pitch.values():
        events.sort(key=lambda item: (item[1].start_time, item[0]))
        active: List[tuple[int, float]] = []  # (index, end_time)
        for idx, event in events:
            current_start = event.start_time
            current_end = event.start_time + event.duration
            active = [(i, end) for i, end in active if end > current_start]
            current_overlap = len(active) + 1
            overlap_counts[idx] = max(overlap_counts[idx], current_overlap)

            # Existing active notes now overlap with this one; bump their counts
            updated_active: List[tuple[int, float]] = []
            for active_idx, end_time in active:
                overlap_counts[active_idx] = max(overlap_counts[active_idx], current_overlap)
                updated_active.append((active_idx, end_time))
            updated_active.append((idx, current_end))
            active = updated_active

    for idx, event in enumerate(note_events):
        event.pitch_overlap = overlap_counts[idx]

    return note_events


def create_visualization(
    note_events: List[NoteEvent],
    output_path: Path,
    title: Optional[str] = None,
    score_duration: Optional[float] = None,
    show_grid: bool = True,
    minimal: bool = False,
    ensemble: str = ENSEMBLE_UNGROUPED,
) -> None:
    """
    Create a 2D visualization of note events and save as PNG.
    
    Args:
        note_events: List of NoteEvent objects
        output_path: Path to save the PNG file
        title: Optional title for the plot
        score_duration: Optional total duration of the score in beats.
                       If provided, uses this for the full time range.
                       If None, calculates from note events only.
        show_grid: Whether to display grid lines (default: True)
        minimal: If True, removes labels, legend, title, and borders (default: False)
        ensemble: Ensemble type (ungrouped, orchestra, or bigband)
    """
    if not note_events:
        raise ValueError("No notes found in the MusicXML file")
    
    # Calculate smallest note duration for grid granularity
    min_duration = min(event.duration for event in note_events)
    
    # Calculate time and pitch ranges
    min_pitch = min(event.pitch_midi for event in note_events)
    max_pitch = max(event.pitch_midi for event in note_events)
    
    # Use score duration if provided, otherwise fall back to note events
    if score_duration is not None:
        max_time = score_duration
        min_time = 0.0
    else:
        max_time = max(event.start_time + event.duration for event in note_events)
        min_time = min(event.start_time for event in note_events)
    
    # Calculate figure size based on content (more space for more detail)
    time_range = max_time - min_time
    pitch_range = max_pitch - min_pitch
    
    # Scale figure size: wider for longer pieces, taller for wider pitch ranges
    # Base size + proportional scaling
    fig_width = max(16, min(24, 14 + time_range * 0.5))
    fig_height = max(10, min(16, 8 + pitch_range * 0.15))
    
    # Set up the figure with higher resolution
    fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=200)
    
    # Configure color mapping based on ensemble mode
    family_mode = ensemble in (ENSEMBLE_BIGBAND, ENSEMBLE_ORCHESTRA)

    if not family_mode:
        color_map = {}
        legend_labels = []
        for event in note_events:
            label = event.instrument_label
            if label not in color_map:
                color_map[label] = get_individual_color(len(color_map))
                legend_labels.append(label)
    else:
        # Group notes by instrument family for color coding
        families_present = set(event.instrument_family for event in note_events)
    
    # Create horizontal bars for each note
    # Use smaller height for better granularity; widen when multiple notes share a pitch
    base_bar_height = max(0.3, min(0.8, 1.0 / max(1, pitch_range / 20)))
    
    for event in note_events:
        if not family_mode:
            color = color_map[event.instrument_label]
        else:
            color = get_family_color(event.instrument_family, ensemble=ensemble)

        overlap_scale = 1 + (event.pitch_overlap - 1) * 0.35
        overlap_scale = min(overlap_scale, 3.0)
        bar_height = base_bar_height * overlap_scale

        dynamic_range = MAX_DYNAMIC_LEVEL - MIN_DYNAMIC_LEVEL
        normalized_dynamic = 0.0 if dynamic_range == 0 else (event.dynamic_level - MIN_DYNAMIC_LEVEL) / dynamic_range
        normalized_dynamic = max(0.0, min(1.0, normalized_dynamic))
        alpha = min(0.95, 0.35 + 0.45 * normalized_dynamic)

        ax.barh(
            event.pitch_midi,
            event.duration,
            left=event.start_time,
            height=bar_height,
            color=color,
            alpha=alpha,
            edgecolor="black",
            linewidth=0.3,
        )
    
    # Set axis labels (skip in minimal mode)
    if not minimal:
        ax.set_xlabel("Time (beats)", fontsize=12)
        ax.set_ylabel("Pitch (MIDI note number)", fontsize=12)
    
    if title and not minimal:
        ax.set_title(title, fontsize=14, fontweight="bold")
    
    # Set axis limits with minimal padding for maximum detail
    pitch_padding = max(1, pitch_range * 0.05)  # 5% padding or 1 semitone minimum
    time_padding = max(0.5, time_range * 0.02)  # 2% padding or 0.5 beat minimum
    
    ax.set_ylim(min_pitch - pitch_padding, max_pitch + pitch_padding)
    ax.set_xlim(min_time - time_padding, max_time + time_padding)
    
    # Create fine-grained grid based on smallest note duration
    # Major grid lines at whole beats
    major_xticks = []
    beat = 0
    while beat <= max_time + time_padding:
        major_xticks.append(beat)
        beat += 1
    
    # Minor grid lines at smallest duration intervals
    minor_xticks = []
    if min_duration > 0:
        tick = min_time
        while tick <= max_time + time_padding:
            minor_xticks.append(tick)
            tick += min_duration
    
    # Set x-axis ticks (skip in minimal mode)
    if not minimal:
        ax.set_xticks(major_xticks, minor=False)
        ax.set_xticks(minor_xticks, minor=True)
    else:
        ax.set_xticks([])
    
    # Y-axis: show every semitone (MIDI note) for better granularity (skip in minimal mode)
    if not minimal:
        y_ticks = list(range(int(min_pitch - pitch_padding), int(max_pitch + pitch_padding) + 1))
        ax.set_yticks(y_ticks)
    else:
        ax.set_yticks([])
    
    # In minimal mode, remove all tick labels, tick marks, and axis spines
    if minimal:
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)
        # Remove all tick marks and labels completely
        ax.tick_params(left=False, bottom=False, top=False, right=False, 
                      labelleft=False, labelbottom=False, labeltop=False, labelright=False,
                      length=0, width=0)
    
    # Create legend
    legend_elements = []
    if not family_mode:
        for label in legend_labels:
            legend_elements.append(mpatches.Patch(color=color_map[label], label=label))
    else:
        # Helper for family-based legends so additional ensembles can plug in easily
        def add_family_legend(family_order: List[str], unknown_family: str) -> None:
            for family in family_order:
                if family in families_present:
                    color = get_family_color(family, ensemble=ensemble)
                    label = family.replace("_", " ").title()
                    legend_elements.append(mpatches.Patch(color=color, label=label))
            if unknown_family in families_present:
                color = get_family_color(unknown_family, ensemble=ensemble)
                legend_elements.append(mpatches.Patch(color=color, label="Unknown"))

        legend_configs = {
            ENSEMBLE_BIGBAND: (
                [BIGBAND_TRUMPETS, BIGBAND_TROMBONES, BIGBAND_SAXOPHONES, BIGBAND_RHYTHM_SECTION],
                BIGBAND_UNKNOWN,
            ),
            ENSEMBLE_ORCHESTRA: (
                [ORCHESTRA_STRINGS, ORCHESTRA_WINDS, ORCHESTRA_BRASS, ORCHESTRA_PERCUSSION],
                ORCHESTRA_UNKNOWN,
            ),
        }

        if ensemble in legend_configs:
            family_order, unknown_family = legend_configs[ensemble]
            add_family_legend(family_order, unknown_family)
        else:
            # Fallback for future/unknown ensembles: treat as ungrouped for legends
            for label in legend_labels:
                legend_elements.append(mpatches.Patch(color=color_map[label], label=label))
    
    # Show legend only if not in minimal mode
    if legend_elements and not minimal:
        legend_elements.append(
            mpatches.Patch(
                facecolor="none",
                edgecolor="none",
                label="Width = stacked pitches; Opacity = dynamics",
            )
        )
        ax.legend(handles=legend_elements, loc="upper right", fontsize=10)
    
    # Add grid: major grid at whole beats, minor grid at smallest duration
    if show_grid:
        ax.grid(True, which="major", alpha=0.4, linestyle="-", linewidth=0.8, color="gray")
        ax.grid(True, which="minor", alpha=0.2, linestyle="--", linewidth=0.3, color="lightgray")
        ax.set_axisbelow(True)
    
    # Adjust layout to prevent label cutoff
    plt.tight_layout()
    
    # Save the figure with higher DPI for better detail
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def convert_musicxml_to_png(
    input_path: Path,
    output_path: Optional[Path] = None,
    title: Optional[str] = None,
    show_grid: bool = True,
    minimal: bool = False,
    ensemble: str = ENSEMBLE_UNGROUPED,
) -> Path:
    """
    Convert a MusicXML file to a PNG visualization.
    
    Args:
        input_path: Path to the input MusicXML file
        output_path: Optional path for the output PNG file.
                     If not provided, uses input filename with .png extension
        title: Optional title for the visualization
        show_grid: Whether to display grid lines (default: True)
        minimal: If True, removes labels, legend, title, and borders (default: False)
        ensemble: Ensemble type (ungrouped, orchestra, or bigband)
    
    Returns:
        Path to the created PNG file
    
    Raises:
        FileNotFoundError: If input file doesn't exist
        ValueError: If the MusicXML file contains no notes
    """
    input_path = Path(input_path)
    
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    # Determine output path
    if output_path is None:
        output_path = input_path.with_suffix(".png")
    else:
        output_path = Path(output_path)
    
    # Parse MusicXML file
    try:
        score = converter.parse(str(input_path))
    except Exception as e:
        raise ValueError(f"Failed to parse MusicXML file: {e}") from e
    
    # Extract note events
    note_events = extract_notes(score, ensemble=ensemble)
    
    # Get the actual duration of the score (in quarter notes/beats)
    # This accounts for all measures, not just where notes are
    score_duration = score.duration.quarterLength
    
    # Use input filename as title if not provided
    if title is None:
        title = input_path.stem
    
    # Create visualization
    create_visualization(note_events, output_path, title, score_duration, show_grid, minimal, ensemble)
    
    return output_path
