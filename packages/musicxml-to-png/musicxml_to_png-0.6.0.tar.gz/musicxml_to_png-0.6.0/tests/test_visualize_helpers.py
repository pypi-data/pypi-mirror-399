import pytest

from musicxml_to_png.visualize import (
    VisualizationConfig,
    PlotBounds,
    compute_plot_bounds,
    compute_figure_dimensions,
    compute_padding,
    generate_time_ticks,
    ConnectionConfig,
)
from musicxml_to_png.models import NoteEvent


def _make_event(pitch: float, start: float, duration: float) -> NoteEvent:
    return NoteEvent(
        pitch_midi=pitch,
        start_time=start,
        duration=duration,
        instrument_family="test",
        instrument_label="test",
    )


def test_visualization_config_overrides_are_scoped():
    base = VisualizationConfig()
    updated = base.with_overrides(minimal=True, time_stretch=2.0, show_grid=False)

    assert base.minimal is False
    assert updated.minimal is True
    assert updated.time_stretch == 2.0
    assert updated.show_grid is False
    assert updated.timeline_unit == base.timeline_unit
    assert updated.ensemble == base.ensemble


def test_compute_plot_bounds_respects_score_duration():
    events = [
        _make_event(60, 1.0, 2.0),
        _make_event(65, 4.0, 1.0),
    ]

    bounds = compute_plot_bounds(events, score_duration=10.0)
    assert bounds.min_time == 0.0
    assert bounds.max_time == 10.0
    assert bounds.min_pitch == 60.0
    assert bounds.max_pitch == 65.0


def test_compute_figure_dimensions_scales_with_range():
    bounds = PlotBounds(
        min_duration=1.0,
        min_pitch=60.0,
        max_pitch=72.0,
        min_time=0.0,
        max_time=8.0,
    )

    width, height = compute_figure_dimensions(bounds, time_stretch=1.0, fig_width=None)
    assert width == pytest.approx(20.8)  # 16 base + 8 * 0.6 slope
    assert height == pytest.approx(11.8)  # 10 base + 12 * 0.15 slope


def test_generate_time_ticks_uses_measure_ticks_when_present():
    bounds = PlotBounds(
        min_duration=1.0,
        min_pitch=60.0,
        max_pitch=72.0,
        min_time=0.0,
        max_time=8.0,
    )
    _, time_padding, _ = compute_padding(bounds, minimal=False, rehearsal_marks=None)
    measure_ticks = [(1, 0.0), (2, 4.0), (3, 8.0)]

    tick_spec = generate_time_ticks(bounds, "bar", measure_ticks, time_padding)
    assert tick_spec.major == [0.0, 4.0, 8.0]
    assert tick_spec.labels == ["1", "2", "3"]
    assert tick_spec.minor == []


def test_generate_time_ticks_builds_beat_ticks_when_no_measures():
    bounds = PlotBounds(
        min_duration=1.0,
        min_pitch=60.0,
        max_pitch=72.0,
        min_time=0.0,
        max_time=8.0,
    )
    _, time_padding, _ = compute_padding(bounds, minimal=False, rehearsal_marks=None)

    tick_spec = generate_time_ticks(bounds, "beat", None, time_padding)
    assert tick_spec.major[0] == 0.0
    assert tick_spec.major[-1] == 8.0
    assert tick_spec.labels[0] == "1"
    assert tick_spec.labels[-1] == "9"  # inclusive of the last beat
    assert tick_spec.minor[0] == 0.0


def test_connection_config_alpha_fade():
    cfg = ConnectionConfig(alpha=0.6, min_alpha=0.3, fade_start=2.0, fade_end=4.0)

    assert cfg.alpha_for_length(1.0) == pytest.approx(0.6)
    mid_alpha = cfg.alpha_for_length(2.5)
    assert 0.3 < mid_alpha < 0.6  # fades between start/end
    assert cfg.alpha_for_length(5.0) == pytest.approx(0.3)
