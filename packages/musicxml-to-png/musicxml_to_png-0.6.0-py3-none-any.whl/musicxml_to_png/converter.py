"""Core orchestration for MusicXML to PNG."""

from pathlib import Path
from typing import Optional, Tuple, List

from music21 import converter, stream

from musicxml_to_png.extract import (
    extract_notes,
    extract_rehearsal_marks,
    build_measure_offset_map,
    detect_note_connections,
)
from musicxml_to_png.models import DEFAULT_STACCATO_FACTOR, MIN_STACCATO_FACTOR, MAX_STACCATO_FACTOR, RehearsalMark
from musicxml_to_png.visualize import (
    ConnectionConfig,
    VisualizationConfig,
    VisualizationInputs,
    compute_plot_bounds,
    compute_padding,
    generate_time_ticks,
    create_visualization,
)
from musicxml_to_png.instruments import (
    ENSEMBLE_UNGROUPED,
    ENSEMBLE_ORCHESTRA,
    ENSEMBLE_BIGBAND,
)

SliceWindow = Optional[Tuple[float, float]]


def _compute_slice_window(
    slice_mode: Optional[str],
    slice_start: Optional[float],
    slice_end: Optional[float],
    measure_offsets: dict[str, float],
    canonical_score_duration: float,
) -> SliceWindow:
    """
    Compute an absolute slice window (start, end) in beats.

    - slice_mode may be bar/measure or beat; measure is treated as bar.
    - slice_start/slice_end are 1-based for both bars and beats.
    - Bar slicing is start-inclusive, end-exclusive at the start of the end bar.
    """
    if slice_mode is None:
        return None

    mode = "bar" if slice_mode == "measure" else slice_mode

    if slice_start is None or slice_end is None:
        raise ValueError("slice_start and slice_end must be provided when slice_mode is set")
    if slice_end <= slice_start:
        raise ValueError("slice_end must be greater than slice_start")

    if mode == "beat":
        window_start = max(0.0, float(slice_start) - 1.0)
        window_end = max(window_start, float(slice_end) - 1.0)
        return (window_start, window_end)

    if mode == "bar":
        start_bar = int(slice_start)
        end_bar = int(slice_end)

        def _offset_for_bar(bar_num: int) -> Optional[float]:
            return measure_offsets.get(str(bar_num))

        start_offset = _offset_for_bar(start_bar)
        if start_offset is None:
            raise ValueError(f"Start bar {start_bar} not found in score")

        end_offset = _offset_for_bar(end_bar)
        if end_offset is None:
            end_offset = canonical_score_duration

        return (start_offset, end_offset)

    raise ValueError(f"Unknown slice_mode: {slice_mode}")


def _build_measure_ticks(
    measure_offsets: dict[str, float],
    slice_window: SliceWindow,
) -> Optional[List[tuple[int, float]]]:
    """
    Build measure tick positions (optionally rebased to a slice window).
    """
    ticks: List[tuple[int, float]] = []
    for num_str, offset in measure_offsets.items():
        try:
            num_int = int(num_str)
        except ValueError:
            continue

        if slice_window is not None:
            if offset < slice_window[0] or offset >= slice_window[1]:
                continue
            rebased_offset = offset - slice_window[0]
            ticks.append((num_int, rebased_offset))
        else:
            ticks.append((num_int, offset))

    if not ticks:
        return None

    ticks.sort(key=lambda x: x[1])
    return ticks


def convert_musicxml_to_png(
    input_path: Path,
    score: Optional[stream.Score] = None,  # Optional pre-parsed music21 Score to avoid re-parsing
    output_path: Optional[Path] = None,
    title: Optional[str] = None,
    show_grid: bool = True,
    minimal: bool = False,
    ensemble: str = ENSEMBLE_UNGROUPED,
    show_rehearsal_marks: bool = True,
    show_legend: bool = True,
    show_title: bool = True,
    write_output: bool = True,
    dpi: int = 150,
    time_stretch: float = 1.0,
    fig_width: Optional[float] = None,
    split_overlaps: bool = True,
    staccato_factor: float = DEFAULT_STACCATO_FACTOR,
    slice_mode: Optional[str] = None,
    slice_start: Optional[float] = None,
    slice_end: Optional[float] = None,
    timeline_unit: str = "bar",
    transparent: bool = False,
    show_connections: bool = False,
    connection_max_gap: Optional[float] = None,
    connection_alpha: Optional[float] = None,
    connection_min_alpha: Optional[float] = None,
    connection_fade_start: Optional[float] = None,
    connection_fade_end: Optional[float] = None,
    connection_linewidth: Optional[float] = None,
    connection_curve_height_factor: Optional[float] = None,
) -> Path:
    """Convert a MusicXML file to a PNG visualization."""
    input_path = Path(input_path)

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    if output_path is None:
        output_path = input_path.with_suffix(".png")
    else:
        output_path = Path(output_path)

    if score is None:
        try:
            score = converter.parse(str(input_path))
        except Exception as e:
            raise ValueError(f"Failed to parse MusicXML file: {e}") from e

    measure_offsets, canonical_duration = build_measure_offset_map(score)
    canonical_score_duration = canonical_duration if canonical_duration is not None else score.duration.quarterLength
    unit_for_computation = "bar" if timeline_unit == "measure" else timeline_unit

    slice_window = _compute_slice_window(
        slice_mode,
        slice_start,
        slice_end,
        measure_offsets,
        canonical_score_duration,
    )

    clamped_staccato = max(MIN_STACCATO_FACTOR, min(MAX_STACCATO_FACTOR, float(staccato_factor)))

    measure_ticks: Optional[list[tuple[int, float]]] = None
    if unit_for_computation == "bar":
        measure_ticks = _build_measure_ticks(measure_offsets, slice_window)

    note_events = extract_notes(
        score,
        ensemble=ensemble,
        measure_offsets=measure_offsets,
        split_overlaps=split_overlaps,
        staccato_factor=clamped_staccato,
        slice_window=slice_window,
    )
    rehearsal_marks = (
        extract_rehearsal_marks(score, measure_offsets=measure_offsets) if show_rehearsal_marks else []
    )

    if not note_events:
        raise ValueError("No notes found in the MusicXML file")

    if slice_window is not None:
        clipped_marks = []
        for mark in rehearsal_marks:
            if mark.start_time < slice_window[0] or mark.start_time >= slice_window[1]:
                continue
            clipped_marks.append(RehearsalMark(label=mark.label, start_time=mark.start_time - slice_window[0]))
        rehearsal_marks = clipped_marks

    score_duration = (
        (slice_window[1] - slice_window[0]) if slice_window is not None else canonical_score_duration
    )

    if title is None:
        title = input_path.stem

    viz_config = VisualizationConfig(
        timeline_unit=timeline_unit,
        show_grid=show_grid,
        minimal=minimal,
        ensemble=ensemble,
        show_legend=show_legend,
        show_title=show_title,
        write_output=write_output,
        time_stretch=time_stretch,
        fig_width=fig_width,
        dpi=dpi,
        transparent=transparent,
        show_connections=show_connections,
    )
    connection_config = viz_config.connections.with_overrides(
        alpha=connection_alpha,
        min_alpha=connection_min_alpha,
        fade_start=connection_fade_start,
        fade_end=connection_fade_end,
        max_gap=connection_max_gap,
        linewidth=connection_linewidth,
        curve_height_factor=connection_curve_height_factor,
    )
    viz_config = viz_config.with_overrides(connections=connection_config)

    connections = None
    if show_connections:
        connections = detect_note_connections(note_events)

    bounds = compute_plot_bounds(note_events, score_duration)
    _, time_padding, _ = compute_padding(bounds, minimal, rehearsal_marks)
    tick_spec = generate_time_ticks(bounds, timeline_unit, measure_ticks, time_padding)

    viz_inputs = VisualizationInputs(
        note_events=note_events,
        rehearsal_marks=rehearsal_marks,
        measure_ticks=measure_ticks,
        connections=connections,
        tick_spec=tick_spec,
    )

    create_visualization(
        note_events,
        output_path,
        title,
        score_duration,
        rehearsal_marks=rehearsal_marks,
        measure_ticks=measure_ticks,
        connections=connections,
        tick_spec=tick_spec,
        config=viz_config,
        inputs=viz_inputs,
        connection_config=connection_config,
    )

    return output_path
