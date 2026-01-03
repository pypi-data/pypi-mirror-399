"""Command-line interface for MusicXML to PNG converter."""

import argparse
import sys
import warnings
from pathlib import Path

from music21 import converter as m21_converter
from music21.musicxml.xmlToM21 import MusicXMLWarning

from musicxml_to_png import __version__
from musicxml_to_png.converter import convert_musicxml_to_png
from musicxml_to_png.ensemble_detection import detect_ensembles
from musicxml_to_png.instruments import (
    ENSEMBLE_UNGROUPED,
    ENSEMBLE_ORCHESTRA,
    ENSEMBLE_BIGBAND,
)
from musicxml_to_png.models import DEFAULT_STACCATO_FACTOR, MIN_STACCATO_FACTOR, MAX_STACCATO_FACTOR


def _print_ensemble_suggestions(suggestions) -> None:
    """
    Print ensemble suggestions when using the default ensemble.

    Behavior:
      - Filter out ungrouped; only show entries with confidence >= 0.25.
      - Show top candidate, and second candidate if within 0.1 of the top.
      - Message format remains unchanged from prior behavior.
    """
    candidates = [
        (name, confidence)
        for name, confidence in suggestions
        if name != ENSEMBLE_UNGROUPED and confidence >= 0.25
    ]
    if not candidates:
        return

    candidates.sort(key=lambda item: item[1], reverse=True)
    filtered = [candidates[0]]
    if len(candidates) > 1:
        next_confidence = candidates[1][1]
        if (filtered[0][1] - next_confidence) <= 0.1:
            filtered.append(candidates[1])

    for name, confidence in filtered:
        pct = confidence * 100.0
        print(
            f"Info: Ensemble detected: {name} ({pct:.0f}%). "
            f'Use "--ensemble {name}" to group instruments.'
        )


def _parse_range(value: str, cast_type):
    if "-" not in value:
        raise ValueError("Range must be in the form start-end")
    start_str, end_str = value.split("-", 1)
    start = cast_type(start_str.strip())
    end = cast_type(end_str.strip())
    if end <= start:
        raise ValueError("End must be greater than start in range")
    return start, end


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Convert MusicXML files into clean, analyzable PNG visualizations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s input.xml
  %(prog)s input.xml -o output.png
  %(prog)s input.xml --title "My Composition"
  %(prog)s input.xml --no-grid
  %(prog)s input.xml --minimal
  %(prog)s input.xml --ensemble bigband
  %(prog)s input.xml --verbose
        """,
    )
    
    parser.add_argument(
        "input",
        type=str,
        help="Path to the input MusicXML file",
    )
    
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=None,
        help="Path to the output PNG file (default: input filename with .png extension)",
    )
    
    parser.add_argument(
        "-t",
        "--title",
        type=str,
        default=None,
        help="Title for the visualization (default: input filename)",
    )
    
    parser.add_argument(
        "--no-grid",
        action="store_true",
        help="Disable grid lines in the visualization",
    )
    
    parser.add_argument(
        "--minimal",
        action="store_true",
        help="Remove all labels, legend, title, and borders for a clean visualization",
    )

    parser.add_argument(
        "--no-rehearsal-marks",
        action="store_true",
        help="Disable rendering rehearsal letters/numbers on the timeline",
    )

    parser.add_argument(
        "--no-legend",
        action="store_true",
        help="Disable the legend in the visualization",
    )

    parser.add_argument(
        "--no-title",
        action="store_true",
        help="Disable the plot title (otherwise uses filename or --title)",
    )

    parser.add_argument(
        "--no-output",
        action="store_true",
        help="Run the full pipeline without writing a PNG (useful for smoke tests)",
    )
    
    parser.add_argument(
        "--ensemble",
        type=str,
        default=ENSEMBLE_UNGROUPED,
        choices=[ENSEMBLE_UNGROUPED, ENSEMBLE_ORCHESTRA, ENSEMBLE_BIGBAND],
        help=(
            "Ensemble type for instrument categorization. "
            "Defaults to per-instrument colors; choose orchestra or bigband to group by family."
        ),
    )
    
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show music21 warnings and other diagnostic information",
    )

    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s " + __version__,
        help="Show the musicxml-to-png version and exit",
    )

    parser.add_argument(
        "--skip-ensemble-detection",
        action="store_true",
        help="Skip ensemble auto-detection suggestions (useful for CI/pipelines).",
    )

    parser.add_argument(
        "--print-ensemble-confidences",
        action="store_true",
        help=(
            "Print raw ensemble detection confidences (0-1) for all candidates; "
            "useful for debugging or pipeline parsing."
        ),
    )

    parser.add_argument(
        "--time-stretch",
        type=float,
        default=1.0,
        help="Scale timeline width (e.g., 1.2 widens, 0.8 tightens).",
    )

    parser.add_argument(
        "--fig-width",
        type=float,
        default=None,
        help="Explicit figure width in inches; overrides automatic sizing.",
    )

    parser.add_argument(
        "--dpi",
        type=int,
        default=150,
        help="DPI for the output image (e.g., 150, 300).",
    )

    parser.add_argument(
        "--no-overlap-splitting",
        action="store_true",
        help=(
            "Keep stacked height for the entire note when any portion overlaps on the same pitch "
            "(legacy behavior). Default is to split and only thicken the overlapping segments."
        ),
    )

    parser.add_argument(
        "--staccato-factor",
        type=float,
        default=DEFAULT_STACCATO_FACTOR,
        help=(
            f"Scale duration for staccato articulations (range {MIN_STACCATO_FACTOR}-{MAX_STACCATO_FACTOR}, "
            f"default {DEFAULT_STACCATO_FACTOR})."
        ),
    )

    parser.add_argument(
        "--slice-range",
        type=str,
        default=None,
        help="Range to render in the form start-end (e.g., bars 12-24 or beats 48-72). Bars are 1-based; end bar slices until the start of the next bar.",
    )

    parser.add_argument(
        "--timeline-unit",
        type=str,
        choices=["beat", "bar", "measure"],
        default="bar",
        help="Display the timeline using bars/measures (default) or beats on the x-axis.",
    )

    parser.add_argument(
        "--transparent",
        action="store_true",
        help="Use a transparent background for the output PNG instead of white.",
    )

    parser.add_argument(
        "--show-connections",
        action="store_true",
        help="Show curved lines connecting adjacent notes (no rest between) within each instrument.",
    )
    parser.add_argument(
        "--connection-max-gap",
        type=float,
        default=None,
        help="Skip drawing connection lines when the gap from note end to next start exceeds this many beats (advanced).",
    )
    parser.add_argument(
        "--connection-alpha",
        type=float,
        default=None,
        help="Base opacity for short connection lines (default 0.6, advanced).",
    )
    parser.add_argument(
        "--connection-min-alpha",
        type=float,
        default=None,
        help="Minimum opacity for long connection lines after fading (default 0.25, advanced).",
    )
    parser.add_argument(
        "--connection-fade-start",
        type=float,
        default=None,
        help="Length in beats where connection line fading begins (default 4.0, advanced).",
    )
    parser.add_argument(
        "--connection-fade-end",
        type=float,
        default=None,
        help="Length in beats where connection line fading reaches minimum opacity (default 8.0, advanced).",
    )
    parser.add_argument(
        "--connection-linewidth",
        type=float,
        default=None,
        help="Line width for connection lines (default 1.0, advanced).",
    )
    parser.add_argument(
        "--connection-curve-height-factor",
        type=float,
        default=None,
        help="Curve height factor for connection lines; 0 = straight, higher bends upward (advanced).",
    )
    
    args = parser.parse_args()
    
    # Configure warning display based on verbose mode
    if args.verbose:
        # In verbose mode, ensure warnings are shown
        warnings.filterwarnings('always', category=MusicXMLWarning)
    else:
        # In quiet mode (default), suppress music21 warnings
        warnings.filterwarnings('ignore', category=MusicXMLWarning)
    
    # Convert input path to Path object
    input_path = Path(args.input)
    
    # Validate input file exists
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    
    # Validate input file extension
    if input_path.suffix.lower() not in [".xml", ".musicxml", ".mxl"]:
        print(
            f"Warning: Input file doesn't have a standard MusicXML extension: {input_path.suffix}",
            file=sys.stderr,
        )
    
    # Convert output path if provided
    output_path = Path(args.output) if args.output else None
    
    try:
        score = m21_converter.parse(str(input_path))
    except Exception as e:
        print(f"Error: Failed to parse MusicXML file: {e}", file=sys.stderr)
        sys.exit(1)

    if args.ensemble == ENSEMBLE_UNGROUPED and not args.skip_ensemble_detection:
        suggestions = detect_ensembles(score)

        if args.print_ensemble_confidences:
            confidences_str = ", ".join(f"{name}={confidence:.2f}" for name, confidence in suggestions)
            print(f"Ensemble confidences: {confidences_str}")

        _print_ensemble_suggestions(suggestions)

    if args.show_connections:
        print("Info: --show-connections is in beta and may have edge cases. Feedback welcome!", file=sys.stderr)

    try:
        # Validate staccato factor
        if not (MIN_STACCATO_FACTOR <= args.staccato_factor <= MAX_STACCATO_FACTOR):
            print(
                f"Error: --staccato-factor must be between {MIN_STACCATO_FACTOR} and {MAX_STACCATO_FACTOR}",
                file=sys.stderr,
            )
            sys.exit(1)

        slice_mode = None
        slice_start = None
        slice_end = None
        if args.slice_range:
            mode_arg = args.timeline_unit or "bar"
            if mode_arg in ("bar", "measure"):
                caster = int
            else:
                caster = float
            try:
                start, end = _parse_range(args.slice_range, caster)
            except Exception as e:
                print(f"Error parsing --slice-range: {e}", file=sys.stderr)
                sys.exit(1)
            slice_mode = "bar" if mode_arg == "measure" else mode_arg
            slice_start, slice_end = start, end

        # Perform conversion
        result_path = convert_musicxml_to_png(
            input_path=input_path,
            score=score,
            output_path=output_path,
            title=args.title if not args.minimal else None,
            show_grid=not args.no_grid,
            minimal=args.minimal,
            ensemble=args.ensemble,
            show_rehearsal_marks=not args.no_rehearsal_marks,
            show_legend=not args.no_legend,
            show_title=not args.no_title,
            write_output=not args.no_output,
            time_stretch=args.time_stretch,
            fig_width=args.fig_width,
            dpi=args.dpi,
            split_overlaps=not args.no_overlap_splitting,
            staccato_factor=args.staccato_factor,
            slice_mode=slice_mode,
            slice_start=slice_start,
            slice_end=slice_end,
            timeline_unit=args.timeline_unit,
            transparent=args.transparent,
            show_connections=args.show_connections,
            connection_max_gap=args.connection_max_gap,
            connection_alpha=args.connection_alpha,
            connection_min_alpha=args.connection_min_alpha,
            connection_fade_start=args.connection_fade_start,
            connection_fade_end=args.connection_fade_end,
            connection_linewidth=args.connection_linewidth,
            connection_curve_height_factor=args.connection_curve_height_factor,
        )
        if not args.no_output:
            print(f"Successfully created visualization: {result_path}")
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)
