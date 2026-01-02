"""Visualization helpers for MusicXML note events."""

from pathlib import Path
from typing import List, Optional

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

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


def create_visualization(
    note_events: List[NoteEvent],
    output_path: Path,
    title: Optional[str] = None,
    score_duration: Optional[float] = None,
    show_grid: bool = True,
    minimal: bool = False,
    ensemble: str = ENSEMBLE_UNGROUPED,
    rehearsal_marks: Optional[List[RehearsalMark]] = None,
    show_legend: bool = True,
    show_title: bool = True,
    write_output: bool = True,
    time_stretch: float = 1.0,
    fig_width: Optional[float] = None,
    dpi: int = 150,
) -> None:
    """
    Create a 2D visualization of note events and save as PNG.
    """
    if not note_events:
        raise ValueError("No notes found in the MusicXML file")

    min_duration = min(event.duration for event in note_events)

    min_pitch = min(event.pitch_midi for event in note_events)
    max_pitch = max(event.pitch_midi for event in note_events)

    if score_duration is not None:
        max_time = score_duration
        min_time = 0.0
    else:
        max_time = max(event.start_time + event.duration for event in note_events)
        min_time = min(event.start_time for event in note_events)

    time_range = max_time - min_time
    pitch_range = max_pitch - min_pitch

    MIN_FIG_WIDTH = 16.0
    MAX_FIG_WIDTH = 72.0
    BASE_FIG_WIDTH = MIN_FIG_WIDTH
    TIME_TO_WIDTH_SLOPE = 0.6
    MIN_FIG_HEIGHT = 10.0
    MAX_FIG_HEIGHT = 16.0
    BASE_FIG_HEIGHT = MIN_FIG_HEIGHT
    PITCH_TO_HEIGHT_SLOPE = 0.15

    STRETCH_MAX_MULTIPLIER = 10.0

    if fig_width is not None:
        fig_width = max(1.0, float(fig_width))
    else:
        base_width = BASE_FIG_WIDTH + time_range * TIME_TO_WIDTH_SLOPE
        stretch = float(time_stretch)
        if stretch != 1.0:
            capped_stretch = max(0.0, min(STRETCH_MAX_MULTIPLIER, stretch))
            fig_width = max(1.0, base_width * capped_stretch)
        else:
            fig_width = max(MIN_FIG_WIDTH, min(MAX_FIG_WIDTH, base_width))
    fig_height = max(MIN_FIG_HEIGHT, min(MAX_FIG_HEIGHT, BASE_FIG_HEIGHT + pitch_range * PITCH_TO_HEIGHT_SLOPE))

    clamped_dpi = max(50, min(600, int(dpi)))
    fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=clamped_dpi)

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
        families_present = set(event.instrument_family for event in note_events)

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

    if not minimal:
        ax.set_xlabel("Time (beats)", fontsize=12)
        ax.set_ylabel("Pitch (MIDI note number)", fontsize=12)

    if title and not minimal and show_title:
        ax.set_title(title, fontsize=14, fontweight="bold")

    pitch_padding = max(1, pitch_range * 0.05)
    time_padding = max(0.5, time_range * 0.02)
    extra_top_padding = 0.0 if minimal or not rehearsal_marks else max(1.0, pitch_range * 0.08)

    ax.set_ylim(min_pitch - pitch_padding, max_pitch + pitch_padding + extra_top_padding)
    ax.set_xlim(min_time - time_padding, max_time + time_padding)

    major_xticks = []
    beat = 0
    while beat <= max_time + time_padding:
        major_xticks.append(beat)
        beat += 1

    minor_xticks = []
    if min_duration > 0:
        tick = min_time
        while tick <= max_time + time_padding:
            minor_xticks.append(tick)
            tick += min_duration

    if not minimal:
        ax.set_xticks(major_xticks, minor=False)
        ax.set_xticks(minor_xticks, minor=True)
    else:
        ax.set_xticks([])

    if not minimal:
        y_ticks = list(range(int(min_pitch - pitch_padding), int(max_pitch + pitch_padding) + 1))
        ax.set_yticks(y_ticks)
    else:
        ax.set_yticks([])

    if minimal:
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

    if rehearsal_marks and not minimal:
        label_y = max_pitch + pitch_padding + extra_top_padding * 0.5
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

    legend_elements = []
    if not family_mode:
        for label in legend_labels:
            legend_elements.append(mpatches.Patch(color=color_map[label], label=label))
    else:
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
            for label in legend_labels:
                legend_elements.append(mpatches.Patch(color=color_map[label], label=label))

    if legend_elements and not minimal and show_legend:
        legend_elements.append(
            mpatches.Patch(
                facecolor="none",
                edgecolor="none",
                label="Width = stacked pitches; Opacity = dynamics",
            )
        )
        ax.legend(handles=legend_elements, loc="upper right", fontsize=10)

    if show_grid:
        ax.grid(True, which="major", alpha=0.4, linestyle="-", linewidth=0.8, color="gray")
        ax.grid(True, which="minor", alpha=0.2, linestyle="--", linewidth=0.3, color="lightgray")
        ax.set_axisbelow(True)

    plt.tight_layout()
    if write_output:
        fig.savefig(output_path, dpi=clamped_dpi, bbox_inches="tight")
    plt.close(fig)

