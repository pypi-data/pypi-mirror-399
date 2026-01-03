"""Visualization helpers for MusicXML note events."""

from dataclasses import dataclass, replace, field
from pathlib import Path
from typing import List, Optional, Tuple

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
from matplotlib.path import Path as MplPath
from matplotlib.patches import PathPatch

from musicxml_to_png.instruments import (
    BIGBAND_RHYTHM_SECTION,
    BIGBAND_SAXOPHONES,
    BIGBAND_TROMBONES,
    BIGBAND_TRUMPETS,
    ENSEMBLE_BIGBAND,
    ENSEMBLE_ORCHESTRA,
    ENSEMBLE_UNGROUPED,
    ORCHESTRA_BRASS,
    ORCHESTRA_PERCUSSION,
    ORCHESTRA_STRINGS,
    ORCHESTRA_UNKNOWN,
    ORCHESTRA_WINDS,
    BIGBAND_UNKNOWN,
    get_family_color,
    get_individual_color,
)
from musicxml_to_png.models import (
    MAX_DYNAMIC_LEVEL,
    MIN_DYNAMIC_LEVEL,
    NoteEvent,
    RehearsalMark,
)

MIN_FIG_WIDTH = 16.0
MAX_FIG_WIDTH = 72.0
BASE_FIG_WIDTH = MIN_FIG_WIDTH
TIME_TO_WIDTH_SLOPE = 0.6
MIN_FIG_HEIGHT = 10.0
MAX_FIG_HEIGHT = 16.0
BASE_FIG_HEIGHT = MIN_FIG_HEIGHT
PITCH_TO_HEIGHT_SLOPE = 0.15
STRETCH_MAX_MULTIPLIER = 10.0


@dataclass(frozen=True)
class PlotBounds:
    min_duration: float
    min_pitch: float
    max_pitch: float
    min_time: float
    max_time: float

    @property
    def time_range(self) -> float:
        return self.max_time - self.min_time

    @property
    def pitch_range(self) -> float:
        return self.max_pitch - self.min_pitch


@dataclass
class ColorContext:
    color_map: dict[str, str]
    legend_labels: list[str]
    families_present: set[str]


@dataclass
class ConnectionConfig:
    """Visual controls for connection lines."""

    alpha: float = 0.6
    min_alpha: float = 0.25
    fade_start: float = 4.0  # beats where fading begins
    fade_end: float = 8.0  # beats where alpha reaches min_alpha
    max_gap: Optional[float] = None  # skip drawing if connection gap exceeds this (in beats)
    linewidth: float = 1.0
    curve_height_factor: float = 0.0  # 0 = straight line; positive values bend upward

    def alpha_for_length(self, length: float) -> float:
        if self.fade_end <= self.fade_start:
            return max(0.0, min(1.0, self.alpha))
        if length <= self.fade_start:
            return max(0.0, min(1.0, self.alpha))
        fade_range = self.fade_end - self.fade_start
        t = min(1.0, max(0.0, (length - self.fade_start) / fade_range))
        faded = self.alpha * (1.0 - t)
        return max(self.min_alpha, min(1.0, faded))

    def with_overrides(
        self,
        alpha: Optional[float] = None,
        min_alpha: Optional[float] = None,
        fade_start: Optional[float] = None,
        fade_end: Optional[float] = None,
        max_gap: Optional[float] = None,
        linewidth: Optional[float] = None,
        curve_height_factor: Optional[float] = None,
    ) -> "ConnectionConfig":
        return ConnectionConfig(
            alpha=self.alpha if alpha is None else alpha,
            min_alpha=self.min_alpha if min_alpha is None else min_alpha,
            fade_start=self.fade_start if fade_start is None else fade_start,
            fade_end=self.fade_end if fade_end is None else fade_end,
            max_gap=self.max_gap if max_gap is None else max_gap,
            linewidth=self.linewidth if linewidth is None else linewidth,
            curve_height_factor=self.curve_height_factor if curve_height_factor is None else curve_height_factor,
        )


@dataclass
class VisualizationConfig:
    timeline_unit: str = "bar"
    show_grid: bool = True
    minimal: bool = False
    ensemble: str = ENSEMBLE_UNGROUPED
    show_legend: bool = True
    show_title: bool = True
    write_output: bool = True
    time_stretch: float = 1.0
    fig_width: Optional[float] = None
    dpi: int = 150
    transparent: bool = False
    show_connections: bool = False
    connections: ConnectionConfig = field(default_factory=ConnectionConfig)

    def with_overrides(
        self,
        timeline_unit: Optional[str] = None,
        show_grid: Optional[bool] = None,
        minimal: Optional[bool] = None,
        ensemble: Optional[str] = None,
        show_legend: Optional[bool] = None,
        show_title: Optional[bool] = None,
        write_output: Optional[bool] = None,
        time_stretch: Optional[float] = None,
        fig_width: Optional[float] = None,
        dpi: Optional[int] = None,
        transparent: Optional[bool] = None,
        show_connections: Optional[bool] = None,
        connections: Optional[ConnectionConfig] = None,
    ) -> "VisualizationConfig":
        """
        Build a new config overriding only the provided values.
        """
        return replace(
            self,
            timeline_unit=self.timeline_unit if timeline_unit is None else timeline_unit,
            show_grid=self.show_grid if show_grid is None else show_grid,
            minimal=self.minimal if minimal is None else minimal,
            ensemble=self.ensemble if ensemble is None else ensemble,
            show_legend=self.show_legend if show_legend is None else show_legend,
            show_title=self.show_title if show_title is None else show_title,
            write_output=self.write_output if write_output is None else write_output,
            time_stretch=self.time_stretch if time_stretch is None else time_stretch,
            fig_width=self.fig_width if fig_width is None else fig_width,
            dpi=self.dpi if dpi is None else dpi,
            transparent=self.transparent if transparent is None else transparent,
            show_connections=self.show_connections if show_connections is None else show_connections,
            connections=self.connections if connections is None else connections,
        )


@dataclass
class VisualizationContext:
    fig: plt.Figure
    ax: plt.Axes
    clamped_dpi: int
    bounds: PlotBounds
    pitch_padding: float
    time_padding: float
    extra_top_padding: float
    config: VisualizationConfig


@dataclass
class VisualizationInputs:
    note_events: List[NoteEvent]
    rehearsal_marks: Optional[List[RehearsalMark]] = None
    measure_ticks: Optional[List[tuple[int, float]]] = None
    connections: Optional[List[Tuple[int, int]]] = None
    tick_spec: Optional["TimeTickSpec"] = None


@dataclass(frozen=True)
class TimeTickSpec:
    major: List[float]
    minor: List[float]
    labels: List[str]


def _validate_note_events(note_events: List[NoteEvent]) -> None:
    if not note_events:
        raise ValueError("No notes found in the MusicXML file")


def compute_plot_bounds(note_events: List[NoteEvent], score_duration: Optional[float]) -> PlotBounds:
    min_duration = min(event.duration for event in note_events)
    min_pitch = min(event.pitch_midi for event in note_events)
    max_pitch = max(event.pitch_midi for event in note_events)

    if score_duration is not None:
        max_time = score_duration
        min_time = 0.0
    else:
        max_time = max(event.start_time + event.duration for event in note_events)
        min_time = min(event.start_time for event in note_events)

    return PlotBounds(
        min_duration=min_duration,
        min_pitch=min_pitch,
        max_pitch=max_pitch,
        min_time=min_time,
        max_time=max_time,
    )


def compute_figure_dimensions(
    bounds: PlotBounds,
    time_stretch: float,
    fig_width: Optional[float],
) -> tuple[float, float]:
    if fig_width is not None:
        width = max(1.0, float(fig_width))
    else:
        base_width = BASE_FIG_WIDTH + bounds.time_range * TIME_TO_WIDTH_SLOPE
        stretch = float(time_stretch)
        if stretch != 1.0:
            capped_stretch = max(0.0, min(STRETCH_MAX_MULTIPLIER, stretch))
            width = max(1.0, base_width * capped_stretch)
        else:
            width = max(MIN_FIG_WIDTH, min(MAX_FIG_WIDTH, base_width))

    height = max(
        MIN_FIG_HEIGHT,
        min(MAX_FIG_HEIGHT, BASE_FIG_HEIGHT + bounds.pitch_range * PITCH_TO_HEIGHT_SLOPE),
    )
    return width, height


def _create_figure(fig_width: float, fig_height: float, dpi: int, transparent: bool):
    clamped_dpi = max(50, min(600, int(dpi)))
    fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=clamped_dpi)

    if transparent:
        fig.patch.set_facecolor("none")
        ax.set_facecolor("none")

    return fig, ax, clamped_dpi


def _prepare_color_context(note_events: List[NoteEvent], family_mode: bool, ensemble: str) -> ColorContext:
    color_map: dict[str, str] = {}
    legend_labels: list[str] = []
    families_present: set[str] = set()

    if not family_mode:
        for event in note_events:
            label = event.instrument_label
            if label not in color_map:
                color_map[label] = get_individual_color(len(color_map))
                legend_labels.append(label)
    else:
        families_present = {event.instrument_family for event in note_events}

    return ColorContext(color_map=color_map, legend_labels=legend_labels, families_present=families_present)


def _color_for_event(
    event: NoteEvent,
    color_context: ColorContext,
    family_mode: bool,
    ensemble: str,
) -> str:
    if not family_mode:
        return color_context.color_map[event.instrument_label]
    return get_family_color(event.instrument_family, ensemble=ensemble)


def _compute_base_bar_height(pitch_range: float) -> float:
    return max(0.3, min(0.8, 1.0 / max(1, pitch_range / 20)))


def _draw_note_bars(
    ax,
    note_events: List[NoteEvent],
    color_context: ColorContext,
    family_mode: bool,
    ensemble: str,
    base_bar_height: float,
    dynamic_range: float,
) -> None:
    for event in note_events:
        color = _color_for_event(event, color_context, family_mode, ensemble)

        overlap_scale = 1 + (event.pitch_overlap - 1) * 0.35
        overlap_scale = min(overlap_scale, 3.0)
        bar_height = base_bar_height * overlap_scale

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


def _draw_note_connections(
    ax,
    note_events: List[NoteEvent],
    connections: Optional[List[Tuple[int, int]]],
    color_context: ColorContext,
    family_mode: bool,
    ensemble: str,
    connection_config: ConnectionConfig,
) -> None:
    if not connections:
        return

    for note1_idx, note2_idx in connections:
        if note1_idx >= len(note_events) or note2_idx >= len(note_events):
            continue

        note1 = note_events[note1_idx]
        note2 = note_events[note2_idx]

        x1 = note1.start_time + note1.duration
        y1 = note1.pitch_midi
        x2 = note2.start_time
        y2 = note2.pitch_midi

        gap = x2 - x1
        if connection_config.max_gap is not None and gap > connection_config.max_gap:
            continue

        connection_color = _color_for_event(note1, color_context, family_mode, ensemble)
        alpha = connection_config.alpha_for_length(gap if gap >= 0 else 0.0)

        if connection_config.curve_height_factor > 0 and gap >= 0:
            cx = (x1 + x2) / 2.0
            cy = (y1 + y2) / 2.0 + connection_config.curve_height_factor * gap
            path_data = [
                (MplPath.MOVETO, (x1, y1)),
                (MplPath.CURVE3, (cx, cy)),
                (MplPath.CURVE3, (x2, y2)),
            ]
            codes, verts = zip(*path_data)
            path = MplPath(verts, codes)
            patch = PathPatch(
                path,
                facecolor="none",
                edgecolor=connection_color,
                linewidth=connection_config.linewidth,
                alpha=alpha,
                linestyle="-",
                zorder=0.5,
            )
            ax.add_patch(patch)
        else:
            ax.plot(
                [x1, x2],
                [y1, y2],
                color=connection_color,
                linewidth=connection_config.linewidth,
                alpha=alpha,
                linestyle="-",
                zorder=0.5,
            )


def _apply_axis_labels(ax, timeline_unit: str, minimal: bool) -> None:
    if minimal:
        return

    unit_label = "beats"
    if timeline_unit == "bar":
        unit_label = "bars"
    elif timeline_unit == "measure":
        unit_label = "measures"

    ax.set_xlabel(f"Time ({unit_label})", fontsize=12)
    ax.set_ylabel("Pitch (MIDI note number)", fontsize=12)


def compute_padding(
    bounds: PlotBounds,
    minimal: bool,
    rehearsal_marks: Optional[List[RehearsalMark]],
) -> tuple[float, float, float]:
    pitch_padding = max(1, bounds.pitch_range * 0.05)
    time_padding = max(0.5, bounds.time_range * 0.02)
    extra_top_padding = 0.0 if minimal or not rehearsal_marks else max(1.0, bounds.pitch_range * 0.08)
    return pitch_padding, time_padding, extra_top_padding


def _set_axis_limits(
    ax,
    bounds: PlotBounds,
    pitch_padding: float,
    time_padding: float,
    extra_top_padding: float,
) -> None:
    ax.set_ylim(bounds.min_pitch - pitch_padding, bounds.max_pitch + pitch_padding + extra_top_padding)
    ax.set_xlim(bounds.min_time - time_padding, bounds.max_time + time_padding)


def generate_time_ticks(
    bounds: PlotBounds,
    timeline_unit: str,
    measure_ticks: Optional[List[tuple[int, float]]],
    time_padding: float,
) -> TimeTickSpec:
    if timeline_unit in ("bar", "measure") and measure_ticks:
        major_xticks = [offset for _, offset in measure_ticks]
        labels = [str(num) for num, _ in measure_ticks]
        return TimeTickSpec(major=major_xticks, minor=[], labels=labels)

    major_xticks: List[float] = []
    beat = 0
    while beat <= bounds.max_time + time_padding:
        major_xticks.append(beat)
        beat += 1

    minor_xticks: List[float] = []
    if bounds.min_duration > 0:
        tick = bounds.min_time
        while tick <= bounds.max_time + time_padding:
            minor_xticks.append(tick)
            tick += bounds.min_duration

    beat_labels = [f"{tick + 1:g}" for tick in major_xticks]
    return TimeTickSpec(major=major_xticks, minor=minor_xticks, labels=beat_labels)


def _apply_time_ticks(ax, tick_spec: TimeTickSpec, minimal: bool) -> None:
    if minimal:
        ax.set_xticks([])
        return

    ax.set_xticks(tick_spec.major, minor=False)
    ax.set_xticks(tick_spec.minor, minor=True)
    ax.set_xticklabels(tick_spec.labels, minor=False)


def _apply_pitch_ticks(ax, bounds: PlotBounds, pitch_padding: float, minimal: bool) -> None:
    if minimal:
        ax.set_yticks([])
        return
    y_ticks = list(range(int(bounds.min_pitch - pitch_padding), int(bounds.max_pitch + pitch_padding) + 1))
    ax.set_yticks(y_ticks)


def _apply_minimal_style(ax) -> None:
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.tick_params(
        left=False,
        bottom=False,
        top=False,
        right=False,
        labelleft=False,
        labelbottom=False,
        labeltop=False,
        labelright=False,
        length=0,
        width=0,
    )


def _draw_rehearsal_marks(
    ax,
    rehearsal_marks: List[RehearsalMark],
    bounds: PlotBounds,
    pitch_padding: float,
    extra_top_padding: float,
) -> None:
    label_y = bounds.max_pitch + pitch_padding + extra_top_padding * 0.5
    for mark in rehearsal_marks:
        ax.axvline(
            mark.start_time,
            color="black",
            alpha=0.35,
            linestyle="--",
            linewidth=0.9,
            zorder=0.5,
        )
        ax.text(
            mark.start_time,
            label_y,
            mark.label,
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="gray", alpha=0.7),
        )


def _build_legend(
    ax,
    color_context: ColorContext,
    family_mode: bool,
    ensemble: str,
    minimal: bool,
    show_legend: bool,
    show_connections: bool,
    connection_config: ConnectionConfig,
) -> None:
    legend_elements = []

    if not family_mode:
        for label in color_context.legend_labels:
            legend_elements.append(mpatches.Patch(color=color_context.color_map[label], label=label))
    else:
        def add_family_legend(family_order: List[str], unknown_family: str) -> None:
            for family in family_order:
                if family in color_context.families_present:
                    color = get_family_color(family, ensemble=ensemble)
                    label = family.replace("_", " ").title()
                    legend_elements.append(mpatches.Patch(color=color, label=label))
            if unknown_family in color_context.families_present:
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
            for label in color_context.legend_labels:
                legend_elements.append(mpatches.Patch(color=color_context.color_map[label], label=label))

    if legend_elements and not minimal and show_legend:
        legend_elements.append(
            mpatches.Patch(
                facecolor="none",
                edgecolor="none",
                label="Width = stacked pitches; Opacity = dynamics",
            )
        )
        if show_connections:
            legend_elements.append(
                Line2D(
                    [0],
                    [0],
                    color="black",
                    alpha=connection_config.alpha,
                    linewidth=connection_config.linewidth,
                    linestyle="-",
                    label="Lines = adjacent notes",
                )
            )
        ax.legend(handles=legend_elements, loc="upper right", fontsize=10)


def _apply_grid(ax, show_grid: bool) -> None:
    if not show_grid:
        return
    ax.grid(True, which="major", alpha=0.4, linestyle="-", linewidth=0.8, color="gray")
    ax.grid(True, which="minor", alpha=0.2, linestyle="--", linewidth=0.3, color="lightgray")
    ax.set_axisbelow(True)


def create_visualization(
    note_events: List[NoteEvent],
    output_path: Path,
    title: Optional[str] = None,
    score_duration: Optional[float] = None,
    timeline_unit: Optional[str] = None,
    show_grid: Optional[bool] = None,
    minimal: Optional[bool] = None,
    ensemble: Optional[str] = None,
    rehearsal_marks: Optional[List[RehearsalMark]] = None,
    measure_ticks: Optional[List[tuple[int, float]]] = None,
    show_legend: Optional[bool] = None,
    show_title: Optional[bool] = None,
    write_output: Optional[bool] = None,
    time_stretch: Optional[float] = None,
    fig_width: Optional[float] = None,
    dpi: Optional[int] = None,
    transparent: Optional[bool] = None,
    show_connections: Optional[bool] = None,
    connections: Optional[List[Tuple[int, int]]] = None,
    tick_spec: Optional[TimeTickSpec] = None,
    config: Optional[VisualizationConfig] = None,
    inputs: Optional[VisualizationInputs] = None,
    connection_config: Optional[ConnectionConfig] = None,
) -> None:
    """
    Create a 2D visualization of note events and save as PNG.
    """
    if inputs is not None:
        note_events = inputs.note_events
        if rehearsal_marks is None and inputs.rehearsal_marks is not None:
            rehearsal_marks = inputs.rehearsal_marks
        if measure_ticks is None and inputs.measure_ticks is not None:
            measure_ticks = inputs.measure_ticks
        if connections is None and inputs.connections is not None:
            connections = inputs.connections
        if tick_spec is None and inputs.tick_spec is not None:
            tick_spec = inputs.tick_spec

    _validate_note_events(note_events)

    resolved_config = (config or VisualizationConfig()).with_overrides(
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
        connections=connection_config,
    )
    resolved_connection_config = resolved_config.connections if resolved_config.connections else ConnectionConfig()

    bounds = compute_plot_bounds(note_events, score_duration)
    fig_width, fig_height = compute_figure_dimensions(bounds, resolved_config.time_stretch, resolved_config.fig_width)
    fig, ax, clamped_dpi = _create_figure(fig_width, fig_height, resolved_config.dpi, resolved_config.transparent)

    pitch_padding, time_padding, extra_top_padding = compute_padding(
        bounds, resolved_config.minimal, rehearsal_marks
    )
    ctx = VisualizationContext(
        fig=fig,
        ax=ax,
        clamped_dpi=clamped_dpi,
        bounds=bounds,
        pitch_padding=pitch_padding,
        time_padding=time_padding,
        extra_top_padding=extra_top_padding,
        config=resolved_config,
    )

    family_mode = resolved_config.ensemble in (ENSEMBLE_BIGBAND, ENSEMBLE_ORCHESTRA)
    color_context = _prepare_color_context(note_events, family_mode, resolved_config.ensemble)
    base_bar_height = _compute_base_bar_height(bounds.pitch_range)
    dynamic_range = MAX_DYNAMIC_LEVEL - MIN_DYNAMIC_LEVEL

    _draw_note_bars(
        ctx.ax,
        note_events,
        color_context,
        family_mode,
        resolved_config.ensemble,
        base_bar_height,
        dynamic_range,
    )

    if resolved_config.show_connections and connections:
        _draw_note_connections(
            ctx.ax,
            note_events,
            connections,
            color_context,
            family_mode,
            resolved_config.ensemble,
            resolved_connection_config,
        )

    _apply_axis_labels(ctx.ax, resolved_config.timeline_unit, resolved_config.minimal)

    if title and not resolved_config.minimal and resolved_config.show_title:
        ctx.ax.set_title(title, fontsize=14, fontweight="bold")

    _set_axis_limits(ctx.ax, bounds, pitch_padding, time_padding, extra_top_padding)
    tick_spec = tick_spec or generate_time_ticks(bounds, resolved_config.timeline_unit, measure_ticks, time_padding)
    _apply_time_ticks(ctx.ax, tick_spec, resolved_config.minimal)
    _apply_pitch_ticks(ctx.ax, bounds, pitch_padding, resolved_config.minimal)

    if resolved_config.minimal:
        _apply_minimal_style(ctx.ax)

    if rehearsal_marks and not resolved_config.minimal:
        _draw_rehearsal_marks(ctx.ax, rehearsal_marks, bounds, pitch_padding, extra_top_padding)

    _build_legend(
        ctx.ax,
        color_context,
        family_mode,
        resolved_config.ensemble,
        resolved_config.minimal,
        resolved_config.show_legend,
        resolved_config.show_connections,
        resolved_connection_config,
    )
    _apply_grid(ctx.ax, resolved_config.show_grid)

    plt.tight_layout()
    if resolved_config.write_output:
        ctx.fig.savefig(
            output_path,
            dpi=ctx.clamped_dpi,
            bbox_inches="tight",
            transparent=resolved_config.transparent,
        )
    plt.close(ctx.fig)
