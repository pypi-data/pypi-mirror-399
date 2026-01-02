"""Core orchestration for MusicXML to PNG."""

from pathlib import Path
from typing import Optional

from music21 import converter, stream

from musicxml_to_png.extract import (
    extract_notes,
    extract_rehearsal_marks,
    build_measure_offset_map,
)
from musicxml_to_png.visualize import create_visualization
from musicxml_to_png.instruments import (
    ENSEMBLE_UNGROUPED,
    ENSEMBLE_ORCHESTRA,
    ENSEMBLE_BIGBAND,
)


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
    note_events = extract_notes(score, ensemble=ensemble, measure_offsets=measure_offsets)
    rehearsal_marks = (
        extract_rehearsal_marks(score, measure_offsets=measure_offsets) if show_rehearsal_marks else []
    )

    score_duration = canonical_duration if canonical_duration is not None else score.duration.quarterLength

    if title is None:
        title = input_path.stem

    create_visualization(
        note_events,
        output_path,
        title if show_title else None,
        score_duration,
        show_grid,
        minimal,
        ensemble,
        rehearsal_marks=rehearsal_marks,
        show_legend=show_legend,
        show_title=show_title,
        write_output=write_output,
        dpi=dpi,
        time_stretch=time_stretch,
        fig_width=fig_width,
    )

    return output_path
