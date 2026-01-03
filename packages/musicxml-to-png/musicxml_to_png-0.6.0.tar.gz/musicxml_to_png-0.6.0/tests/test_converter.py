"""Unit tests for MusicXML conversion and visualization."""

from pathlib import Path
import sys
import tempfile

import pytest
from music21 import stream, note, instrument, chord, pitch, tie, dynamics, converter, expressions, articulations
import matplotlib.pyplot as plt

from musicxml_to_png.converter import convert_musicxml_to_png
from musicxml_to_png import cli as cli_module
from musicxml_to_png.extract import (
    extract_notes,
    extract_rehearsal_marks,
    build_measure_offset_map,
    detect_note_connections,
)
from musicxml_to_png.visualize import create_visualization, ConnectionConfig
from musicxml_to_png.models import (
    NoteEvent,
    RehearsalMark,
    DEFAULT_DYNAMIC_LEVEL,
    MIN_DYNAMIC_LEVEL,
    MAX_DYNAMIC_LEVEL,
    DEFAULT_STACCATO_FACTOR,
    MIN_STACCATO_FACTOR,
    MAX_STACCATO_FACTOR,
)
from musicxml_to_png.instruments import (
    ENSEMBLE_UNGROUPED,
    ENSEMBLE_ORCHESTRA,
    ENSEMBLE_BIGBAND,
    ORCHESTRA_STRINGS,
    ORCHESTRA_WINDS,
    ORCHESTRA_BRASS,
    BIGBAND_TRUMPETS,
    BIGBAND_RHYTHM_SECTION,
    BIGBAND_UNKNOWN,
)


@pytest.fixture
def simple_score():
    """Create a simple Score with one part and one note."""
    score = stream.Score()
    part = stream.Part()
    part.append(instrument.Violin())
    n = note.Note("C4")
    n.quarterLength = 1.0
    part.append(n)
    score.append(part)
    return score


@pytest.fixture
def score_with_chord():
    """Create a Score with a chord."""
    score = stream.Score()
    part = stream.Part()
    part.append(instrument.Piano())
    c = chord.Chord(["C4", "E4", "G4"])
    c.quarterLength = 2.0
    part.append(c)
    score.append(part)
    return score


@pytest.fixture
def score_with_rest():
    """Create a Score with notes and rests."""
    score = stream.Score()
    part = stream.Part()
    part.append(instrument.Flute())
    n1 = note.Note("D4")
    n1.quarterLength = 1.0
    part.append(n1)
    r = note.Rest()
    r.quarterLength = 1.0
    part.append(r)
    n2 = note.Note("E4")
    n2.quarterLength = 0.5
    part.append(n2)
    score.append(part)
    return score


@pytest.fixture
def multi_part_score():
    """Create a Score with multiple parts."""
    score = stream.Score()
    
    # Part 1: Violin
    part1 = stream.Part()
    part1.append(instrument.Violin())
    n1 = note.Note("G4")
    n1.quarterLength = 1.0
    part1.append(n1)
    score.append(part1)
    
    # Part 2: Trumpet
    part2 = stream.Part()
    part2.append(instrument.Trumpet())
    n2 = note.Note("C5")
    n2.quarterLength = 1.0
    part2.append(n2)
    score.append(part2)
    
    return score


@pytest.fixture
def empty_score():
    """Create an empty Score."""
    return stream.Score()


class TestExtractNotes:
    """Test note extraction from music21 Score objects."""

    def test_single_note_extraction(self, simple_score):
        """Test extraction of a single note."""
        note_events = extract_notes(simple_score, ensemble=ENSEMBLE_ORCHESTRA)
        
        assert len(note_events) == 1
        assert isinstance(note_events[0], NoteEvent)
        assert note_events[0].pitch_midi == 60.0  # C4
        assert note_events[0].duration == 1.0
        assert note_events[0].start_time == 0.0
        assert note_events[0].instrument_family == ORCHESTRA_STRINGS

    def test_chord_extraction(self, score_with_chord):
        """Test extraction of chord (multiple pitches)."""
        note_events = extract_notes(score_with_chord, ensemble=ENSEMBLE_ORCHESTRA)
        
        # Chord should produce 3 note events (C, E, G)
        assert len(note_events) == 3
        
        # All should have same start time and duration
        assert all(event.start_time == 0.0 for event in note_events)
        assert all(event.duration == 2.0 for event in note_events)
        
        # Check pitches
        pitches = sorted([event.pitch_midi for event in note_events])
        assert pitches == [60.0, 64.0, 67.0]  # C4, E4, G4

    def test_rest_handling(self, score_with_rest):
        """Test that rests are skipped."""
        note_events = extract_notes(score_with_rest, ensemble=ENSEMBLE_ORCHESTRA)
        
        # Should have 2 notes, rest should be skipped
        assert len(note_events) == 2
        
        # First note at offset 0
        assert note_events[0].pitch_midi == 62.0  # D4
        assert note_events[0].start_time == 0.0
        assert note_events[0].duration == 1.0
        
        # Second note at offset 2 (after rest)
        assert note_events[1].pitch_midi == 64.0  # E4
        assert note_events[1].start_time == 2.0
        assert note_events[1].duration == 0.5

    def test_multiple_parts(self, multi_part_score):
        """Test extraction from multiple parts."""
        note_events = extract_notes(multi_part_score, ensemble=ENSEMBLE_ORCHESTRA)
        
        assert len(note_events) == 2
        
        # Check instrument families
        families = [event.instrument_family for event in note_events]
        assert ORCHESTRA_STRINGS in families  # Violin
        assert ORCHESTRA_BRASS in families     # Trumpet

    def test_empty_score(self, empty_score):
        """Test extraction from empty score."""
        note_events = extract_notes(empty_score, ensemble=ENSEMBLE_ORCHESTRA)
        assert len(note_events) == 0

    def test_ensemble_type_affects_classification(self, simple_score):
        """Test that ensemble type affects instrument classification."""
        # Same score, different ensembles
        orchestra_events = extract_notes(simple_score, ensemble=ENSEMBLE_ORCHESTRA)
        bigband_events = extract_notes(simple_score, ensemble=ENSEMBLE_BIGBAND)
        
        # Violin is strings in orchestra
        assert orchestra_events[0].instrument_family == ORCHESTRA_STRINGS
        # instrument.Violin() has MIDI 40, which maps to rhythm_section in bigband
        # This demonstrates that ensemble type affects classification
        assert bigband_events[0].instrument_family == BIGBAND_RHYTHM_SECTION
        # Verify they're different
        assert orchestra_events[0].instrument_family != bigband_events[0].instrument_family

    def test_ungrouped_mode_assigns_unique_labels_for_duplicates(self):
        """Default/ungrouped ensemble should give each part its own label."""
        score = stream.Score()
        
        part1 = stream.Part()
        part1.append(instrument.Flute())
        part1.append(note.Note("C4"))
        score.append(part1)
        
        part2 = stream.Part()
        part2.append(instrument.Flute())
        part2.append(note.Note("D4"))
        score.append(part2)
        
        note_events = extract_notes(score, ensemble=ENSEMBLE_UNGROUPED)
        
        labels = {event.instrument_label for event in note_events}
        assert len(labels) == 2
        assert all(label.startswith("Flute") for label in labels)
        assert labels != {"Flute"}  # duplicate parts should be disambiguated

    def test_part_without_instrument(self):
        """Test part without explicit instrument (should use part name or default to unknown)."""
        score = stream.Score()
        part = stream.Part()
        part.partName = "Unknown Part"
        n = note.Note("C4")
        n.quarterLength = 1.0
        part.append(n)
        score.append(part)
        
        note_events = extract_notes(score, ensemble=ENSEMBLE_ORCHESTRA)
        assert len(note_events) == 1
        # Should fall back to unknown if no instrument info

    def test_tied_notes_within_measure(self):
        """Test that tied notes within a measure are merged into a single NoteEvent."""
        score = stream.Score()
        part = stream.Part()
        part.append(instrument.Flute())
        
        # Create two tied notes: C4 for 1 beat, then tied C4 for 1 beat
        n1 = note.Note("C4")
        n1.quarterLength = 1.0
        n1.tie = tie.Tie("start")
        part.append(n1)
        
        n2 = note.Note("C4")
        n2.quarterLength = 1.0
        n2.tie = tie.Tie("stop")
        part.append(n2)
        
        score.append(part)
        
        note_events = extract_notes(score, ensemble=ENSEMBLE_UNGROUPED)
        
        # Should have only one NoteEvent for the tied C4
        c4_events = [e for e in note_events if e.pitch_midi == 60.0]
        assert len(c4_events) == 1
        assert c4_events[0].start_time == 0.0
        assert c4_events[0].duration == 2.0  # Combined duration

    def test_tied_notes_over_barline(self):
        """Test that tied notes over barlines are merged into a single NoteEvent."""
        score = stream.Score()
        part = stream.Part()
        part.append(instrument.Flute())
        
        # Create a measure with a tied note that continues into the next measure
        m1 = stream.Measure()
        n1 = note.Note("A4")  # MIDI 69
        n1.quarterLength = 2.0
        n1.tie = tie.Tie("start")
        m1.append(n1)
        part.append(m1)
        
        m2 = stream.Measure()
        n2 = note.Note("A4")  # MIDI 69
        n2.quarterLength = 1.0
        n2.tie = tie.Tie("stop")
        m2.append(n2)
        part.append(m2)
        
        score.append(part)
        
        note_events = extract_notes(score, ensemble=ENSEMBLE_UNGROUPED)
        
        # Should have only one NoteEvent for the tied A4
        a4_events = [e for e in note_events if e.pitch_midi == 69.0]
        assert len(a4_events) == 1
        assert a4_events[0].start_time == 0.0
        assert a4_events[0].duration == 3.0  # Combined duration (2.0 + 1.0)

    def test_tied_notes_fixture(self):
        """Test tied notes using the test-fluteduet-1.mxl fixture."""
        from pathlib import Path
        from music21 import converter
        
        fixture_path = Path(__file__).parent / "fixtures" / "test-fluteduet-1.mxl"
        score = converter.parse(str(fixture_path))
        
        note_events = extract_notes(score, ensemble=ENSEMBLE_UNGROUPED)
        
        # Check that pitch 69 around time 28-31 is merged into a single NoteEvent
        # Based on our investigation, there should be a tied note from 28.0-31.0
        tied_events = [e for e in note_events if e.pitch_midi == 69.0 and 27.0 <= e.start_time <= 32.0]
        
        # Should have one continuous event from 28.0-31.0 (duration 3.0)
        # There might be another tied note starting at 32.0, so we check for the specific one
        event_28_31 = [e for e in tied_events if e.start_time == 28.0]
        assert len(event_28_31) == 1
        assert event_28_31[0].duration == 3.0  # 2.0 + 1.0 from the tied segments
        
        # Verify it's continuous (no gap)
        assert event_28_31[0].start_time + event_28_31[0].duration == 31.0

    def test_non_tied_notes_unaffected(self):
        """Test that non-tied notes are not affected by tie merging logic."""
        score = stream.Score()
        part = stream.Part()
        part.append(instrument.Flute())
        
        # Create two separate notes (not tied)
        n1 = note.Note("C4")
        n1.quarterLength = 1.0
        part.append(n1)
        
        n2 = note.Note("D4")
        n2.quarterLength = 1.0
        part.append(n2)
        
        score.append(part)
        
        note_events = extract_notes(score, ensemble=ENSEMBLE_UNGROUPED)
        
        # Should have two separate NoteEvents
        assert len(note_events) == 2
        assert note_events[0].pitch_midi == 60.0  # C4
        assert note_events[0].duration == 1.0
        assert note_events[1].pitch_midi == 62.0  # D4
        assert note_events[1].duration == 1.0

    def test_chord_with_tied_notes(self):
        """Test that tied chords are merged correctly."""
        score = stream.Score()
        part = stream.Part()
        part.append(instrument.Piano())
        
        # Create a tied chord: C4-E4 for 1 beat, then tied C4-E4 for 1 beat
        c1 = chord.Chord(["C4", "E4"])
        c1.quarterLength = 1.0
        c1.tie = tie.Tie("start")
        part.append(c1)
        
        c2 = chord.Chord(["C4", "E4"])
        c2.quarterLength = 1.0
        c2.tie = tie.Tie("stop")
        part.append(c2)
        
        score.append(part)
        
        note_events = extract_notes(score, ensemble=ENSEMBLE_UNGROUPED)
        
        # Should have two NoteEvents (one for C4, one for E4), each with merged duration
        assert len(note_events) == 2
        
        # Both pitches should be present
        pitches = sorted([e.pitch_midi for e in note_events])
        assert pitches == [60.0, 64.0]  # C4, E4
        
        # Both should have merged duration of 2.0
        for event in note_events:
            assert event.start_time == 0.0
            assert event.duration == 2.0  # Combined duration

    def test_dynamic_markings_and_velocity(self):
        """Dynamics markings set baseline level; velocity can raise it."""
        score = stream.Score()
        part = stream.Part()
        part.append(instrument.Violin())
        part.insert(0.0, dynamics.Dynamic("mf"))

        n1 = note.Note("C4")
        n1.quarterLength = 1.0
        part.append(n1)

        part.insert(1.0, dynamics.Dynamic("ff"))
        n2 = note.Note("D4")
        n2.quarterLength = 1.0
        # Velocity should push above the default if higher than the marking
        n2.volume.velocity = 110
        part.append(n2)

        score.append(part)

        note_events = extract_notes(score, ensemble=ENSEMBLE_ORCHESTRA)
        assert len(note_events) == 2

        # First note picks up mf marking
        assert note_events[0].dynamic_mark == "mf"
        assert note_events[0].dynamic_level == 0.7

        # Second note picks up ff marking and velocity lift
        assert note_events[1].dynamic_mark == "ff"
        expected_velocity_level = MIN_DYNAMIC_LEVEL + (110 / 127.0) * (MAX_DYNAMIC_LEVEL - MIN_DYNAMIC_LEVEL)
        assert note_events[1].dynamic_level >= expected_velocity_level
        assert note_events[1].dynamic_level <= MAX_DYNAMIC_LEVEL

    def test_pitch_overlap_counts_shared_pitches(self):
        """Overlapping notes on the same pitch are marked as stacked."""
        score = stream.Score()

        part1 = stream.Part()
        part1.append(instrument.Flute())
        n1 = note.Note("C4")
        n1.quarterLength = 2.0
        part1.append(n1)
        score.insert(0, part1)

        part2 = stream.Part()
        part2.append(instrument.Clarinet())
        n2 = note.Note("C4")
        n2.quarterLength = 1.0
        part2.append(n2)
        score.insert(0, part2)

        note_events = extract_notes(score, ensemble=ENSEMBLE_ORCHESTRA)
        assert len(note_events) == 3

        events_by_label = {}
        for event in note_events:
            events_by_label.setdefault(event.instrument_label, []).append(event)

        assert set(events_by_label) == {"Flute", "Clarinet"}

        clarinet_event = events_by_label["Clarinet"][0]
        assert clarinet_event.start_time == 0.0
        assert clarinet_event.duration == 1.0
        assert clarinet_event.pitch_overlap == 2

        flute_events = sorted(events_by_label["Flute"], key=lambda e: e.start_time)
        assert len(flute_events) == 2
        assert flute_events[0].start_time == 0.0
        assert flute_events[0].duration == 1.0
        assert flute_events[0].pitch_overlap == 2
        assert flute_events[1].start_time == 1.0
        assert flute_events[1].duration == 1.0
        assert flute_events[1].pitch_overlap == 1

    def test_pitch_overlap_legacy_mode_without_splitting(self):
        """Legacy behavior keeps entire note thick when any portion overlaps."""
        score = stream.Score()

        part1 = stream.Part()
        part1.append(instrument.Flute())
        n1 = note.Note("C4")
        n1.quarterLength = 2.0
        part1.append(n1)
        score.insert(0, part1)

        part2 = stream.Part()
        part2.append(instrument.Clarinet())
        n2 = note.Note("C4")
        n2.quarterLength = 1.0
        part2.append(n2)
        score.insert(0, part2)

        note_events = extract_notes(score, ensemble=ENSEMBLE_ORCHESTRA, split_overlaps=False)
        assert len(note_events) == 2

        events_by_label = {}
        for event in note_events:
            events_by_label.setdefault(event.instrument_label, []).append(event)

        assert set(events_by_label) == {"Flute", "Clarinet"}

        clarinet_event = events_by_label["Clarinet"][0]
        assert clarinet_event.start_time == 0.0
        assert clarinet_event.duration == 1.0
        assert clarinet_event.pitch_overlap == 2

        flute_event = events_by_label["Flute"][0]
        assert flute_event.start_time == 0.0
        assert flute_event.duration == 2.0
        assert flute_event.pitch_overlap == 2

    def test_staccato_shortens_duration_default_factor(self):
        """Staccato articulations shorten duration by the default factor."""
        score = stream.Score()
        part = stream.Part()
        part.append(instrument.Flute())

        n1 = note.Note("C4")
        n1.quarterLength = 1.0
        n1.articulations.append(articulations.Staccato())
        part.append(n1)
        score.append(part)

        note_events = extract_notes(score, ensemble=ENSEMBLE_ORCHESTRA)
        assert len(note_events) == 1
        assert pytest.approx(note_events[0].duration, rel=1e-6) == 1.0 * DEFAULT_STACCATO_FACTOR

    def test_staccato_shortens_duration_custom_factor(self):
        """Custom staccato factor is applied and clamped to allowed range."""
        score = stream.Score()
        part = stream.Part()
        part.append(instrument.Oboe())

        n1 = note.Note("D4")
        n1.quarterLength = 2.0
        n1.articulations.append(articulations.Staccato())
        part.append(n1)
        score.append(part)

        factor = 0.5
        note_events = extract_notes(score, ensemble=ENSEMBLE_ORCHESTRA, staccato_factor=factor)
        assert len(note_events) == 1
        assert pytest.approx(note_events[0].duration, rel=1e-6) == 2.0 * factor

        # Clamping lower than min
        clamped_events = extract_notes(score, ensemble=ENSEMBLE_ORCHESTRA, staccato_factor=0.05)
        assert pytest.approx(clamped_events[0].duration, rel=1e-6) == 2.0 * MIN_STACCATO_FACTOR

    def test_slice_window_clips_and_rebases(self):
        """Slicing trims notes to window and re-bases start times."""
        score = stream.Score()
        part = stream.Part()
        part.append(instrument.Violin())

        # Three one-beat notes starting at 0,1,2
        for i, pitch_name in enumerate(["C4", "D4", "E4"]):
            n = note.Note(pitch_name)
            n.quarterLength = 1.0
            part.insert(float(i), n)

        score.append(part)

        # Slice beats 1-3 -> should keep D4 and E4, rebased to 0 and 1
        events = extract_notes(
            score,
            ensemble=ENSEMBLE_ORCHESTRA,
            slice_window=(1.0, 3.0),
        )

        assert len(events) == 2
        starts = [e.start_time for e in events]
        durations = [e.duration for e in events]
        pitches = [e.pitch_midi for e in events]

        assert starts == [0.0, 1.0]
        assert durations == [1.0, 1.0]
        assert pitches == [62.0, 64.0]  # D4, E4

    def test_slice_window_clips_spanning_note(self):
        """Notes starting before the window but sustaining into it are clipped and included."""
        score = stream.Score()
        part = stream.Part()
        part.append(instrument.Viola())

        n = note.Note("C4")
        n.quarterLength = 2.0
        part.insert(0.0, n)
        score.append(part)

        events = extract_notes(
            score,
            ensemble=ENSEMBLE_ORCHESTRA,
            slice_window=(0.5, 1.5),
        )

        assert len(events) == 1
        assert events[0].start_time == 0.0  # rebased
        assert events[0].duration == 1.0  # clipped to window
        assert events[0].pitch_midi == 60.0

    def test_percussion_offsets_align_with_other_parts(self):
        """Percussion (timpani) should align with winds/strings when measures differ."""
        fixture_path = Path(__file__).parent / "fixtures" / "test-orchestra-2.mxl"
        score = converter.parse(str(fixture_path))

        note_events = extract_notes(score, ensemble=ENSEMBLE_ORCHESTRA)
        timp_events = [e for e in note_events if "timp" in e.instrument_label.lower()]

        assert timp_events, "Expected timpani events to be present"

        first_timp = min(e.start_time for e in timp_events)
        # The timpani should enter around measure 11 (~20.5 beats), not after beat 40
        assert 20.0 <= first_timp <= 21.0

    def test_rehearsal_marks_use_canonical_measure_offsets(self):
        """Rehearsal marks should respect shared measure timeline (shortest bars)."""
        score = stream.Score()

        # Part 1 (longer bars)
        part1 = stream.Part()
        m1 = stream.Measure(number=1)
        m1.append(note.Rest(quarterLength=4.0))
        part1.append(m1)
        m2 = stream.Measure(number=2)
        m2.insert(0.0, expressions.RehearsalMark("B"))
        m2.append(note.Rest(quarterLength=4.0))
        part1.append(m2)
        score.append(part1)

        # Part 2 (shorter, canonical bars)
        part2 = stream.Part()
        m1b = stream.Measure(number=1)
        m1b.append(note.Rest(quarterLength=2.0))
        part2.append(m1b)
        m2b = stream.Measure(number=2)
        m2b.append(note.Rest(quarterLength=2.0))
        part2.append(m2b)
        score.append(part2)

        measure_offsets, _ = build_measure_offset_map(score)
        marks = extract_rehearsal_marks(score, measure_offsets=measure_offsets)

        assert len(marks) == 1
        assert marks[0].label == "B"
        # Canonical measure length for measure 1 and 2 is 2.0 (from part2), so mark at start of measure 2 -> offset 2.0
        assert marks[0].start_time == 2.0

    def test_rehearsal_marks_from_bigband_fixture(self):
        """Fixture bigband file should expose rehearsal marks A-H in order."""
        fixture_path = Path(__file__).parent / "fixtures" / "test-bigband-1.mxl"
        score = converter.parse(str(fixture_path))
        measure_offsets, _ = build_measure_offset_map(score)

        marks = extract_rehearsal_marks(score, measure_offsets=measure_offsets)
        labels = [m.label for m in marks]

        assert labels[:8] == ["A", "B", "C", "D", "E", "F", "G", "H"]


class TestCreateVisualization:
    """Test visualization creation."""

    def test_empty_note_events_raises_error(self, tmp_path):
        """Test that empty note events raises ValueError."""
        output_path = tmp_path / "output.png"
        
        with pytest.raises(ValueError, match="No notes found"):
            create_visualization([], output_path)

    def test_basic_visualization_creation(self, tmp_path):
        """Test basic visualization creation."""
        output_path = tmp_path / "output.png"
        
        note_events = [
            NoteEvent(pitch_midi=60.0, start_time=0.0, duration=1.0, instrument_family=ORCHESTRA_STRINGS),
            NoteEvent(pitch_midi=64.0, start_time=1.0, duration=1.0, instrument_family=ORCHESTRA_WINDS),
        ]
        
        create_visualization(note_events, output_path, ensemble=ENSEMBLE_ORCHESTRA)
        
        assert output_path.exists()
        assert output_path.suffix == ".png"

    def test_grid_enabled(self, tmp_path):
        """Test visualization with grid enabled."""
        output_path = tmp_path / "output.png"
        
        note_events = [
            NoteEvent(pitch_midi=60.0, start_time=0.0, duration=1.0, instrument_family=ORCHESTRA_STRINGS),
        ]
        
        create_visualization(note_events, output_path, show_grid=True, ensemble=ENSEMBLE_ORCHESTRA)
        assert output_path.exists()

    def test_grid_disabled(self, tmp_path):
        """Test visualization with grid disabled."""
        output_path = tmp_path / "output.png"
        
        note_events = [
            NoteEvent(pitch_midi=60.0, start_time=0.0, duration=1.0, instrument_family=ORCHESTRA_STRINGS),
        ]
        
        create_visualization(note_events, output_path, show_grid=False, ensemble=ENSEMBLE_ORCHESTRA)
        assert output_path.exists()

    def test_timeline_labels_beat_are_1_indexed(self, tmp_path, monkeypatch):
        """Beat labels on x-axis should be 1-indexed."""
        output_path = tmp_path / "output.png"

        note_events = [
            NoteEvent(pitch_midi=60.0, start_time=0.0, duration=1.0, instrument_family=ORCHESTRA_STRINGS),
        ]

        captured_ax = {}
        real_subplots = plt.subplots

        def fake_subplots(*args, **kwargs):
            fig, ax = real_subplots(*args, **kwargs)
            captured_ax["ax"] = ax
            return fig, ax

        monkeypatch.setattr(plt, "subplots", fake_subplots)

        create_visualization(
            note_events,
            output_path,
            ensemble=ENSEMBLE_ORCHESTRA,
            timeline_unit="beat",
            write_output=False,
        )

        ax = captured_ax["ax"]
        labels = [label.get_text() for label in ax.get_xticklabels()]
        assert labels and labels[0] == "1"

    def test_timeline_labels_bar_are_1_indexed(self, tmp_path, monkeypatch):
        """Bar/measure labels on x-axis should be 1-indexed."""
        output_path = tmp_path / "output.png"

        note_events = [
            NoteEvent(pitch_midi=60.0, start_time=0.0, duration=1.0, instrument_family=ORCHESTRA_STRINGS),
        ]

        measure_ticks = [(1, 0.0), (2, 4.0)]

        captured_ax = {}
        real_subplots = plt.subplots

        def fake_subplots(*args, **kwargs):
            fig, ax = real_subplots(*args, **kwargs)
            captured_ax["ax"] = ax
            return fig, ax

        monkeypatch.setattr(plt, "subplots", fake_subplots)

        create_visualization(
            note_events,
            output_path,
            ensemble=ENSEMBLE_ORCHESTRA,
            timeline_unit="measure",
            measure_ticks=measure_ticks,
            write_output=False,
        )

        ax = captured_ax["ax"]
        labels = [label.get_text() for label in ax.get_xticklabels()]
        assert labels and labels[0] == "1"

    def test_ungrouped_visualization(self, tmp_path):
        """Test visualization when instruments are ungrouped."""
        output_path = tmp_path / "output.png"
        
        note_events = [
            NoteEvent(
                pitch_midi=60.0,
                start_time=0.0,
                duration=1.0,
                instrument_family="Flute",
                instrument_label="Flute",
            ),
            NoteEvent(
                pitch_midi=62.0,
                start_time=1.0,
                duration=1.0,
                instrument_family="Flute 2",
                instrument_label="Flute 2",
            ),
        ]
        
        create_visualization(note_events, output_path, show_grid=False, ensemble=ENSEMBLE_UNGROUPED)
        assert output_path.exists()

    def test_unknown_ensemble_falls_back_to_ungrouped(self, tmp_path):
        """Unknown ensemble should fall back to per-instrument labeling/colors."""
        output_path = tmp_path / "output.png"
        
        note_events = [
            NoteEvent(
                pitch_midi=60.0,
                start_time=0.0,
                duration=1.0,
                instrument_family="Flute",
                instrument_label="Flute",
            ),
            NoteEvent(
                pitch_midi=62.0,
                start_time=1.0,
                duration=1.0,
                instrument_family="Clarinet",
                instrument_label="Clarinet",
            ),
        ]
        
        create_visualization(note_events, output_path, show_grid=False, ensemble="future-ensemble")
        assert output_path.exists()

    def test_minimal_mode(self, tmp_path):
        """Test minimal mode visualization."""
        output_path = tmp_path / "output.png"
        
        note_events = [
            NoteEvent(pitch_midi=60.0, start_time=0.0, duration=1.0, instrument_family=ORCHESTRA_STRINGS),
        ]
        
        create_visualization(note_events, output_path, minimal=True, ensemble=ENSEMBLE_ORCHESTRA)
        assert output_path.exists()

    def test_custom_title(self, tmp_path):
        """Test visualization with custom title."""
        output_path = tmp_path / "output.png"
        
        note_events = [
            NoteEvent(pitch_midi=60.0, start_time=0.0, duration=1.0, instrument_family=ORCHESTRA_STRINGS),
        ]
        
        create_visualization(note_events, output_path, title="Test Composition", ensemble=ENSEMBLE_ORCHESTRA)
        assert output_path.exists()

    def test_rehearsal_marks_render(self, tmp_path):
        """Visualization should accept rehearsal marks without error."""
        output_path = tmp_path / "output.png"
        
        note_events = [
            NoteEvent(pitch_midi=60.0, start_time=0.0, duration=1.0, instrument_family=ORCHESTRA_STRINGS),
        ]
        rehearsal_marks = [RehearsalMark(label="A", start_time=0.0), RehearsalMark(label="B", start_time=2.0)]
        
        create_visualization(
            note_events,
            output_path,
            title="Rehearsal Test",
            ensemble=ENSEMBLE_ORCHESTRA,
            rehearsal_marks=rehearsal_marks,
        )
        assert output_path.exists()

    def test_score_duration_parameter(self, tmp_path):
        """Test that score_duration parameter affects time range."""
        output_path = tmp_path / "output.png"
        
        note_events = [
            NoteEvent(pitch_midi=60.0, start_time=0.0, duration=1.0, instrument_family=ORCHESTRA_STRINGS),
        ]
        
        # With score_duration, visualization should extend to that time
        create_visualization(
            note_events,
            output_path,
            score_duration=10.0,
            ensemble=ENSEMBLE_ORCHESTRA,
        )
        assert output_path.exists()

    def test_different_ensembles_produce_different_colors(self, tmp_path):
        """Test that different ensembles use different color palettes."""
        output_path_orch = tmp_path / "orchestra.png"
        output_path_bb = tmp_path / "bigband.png"
        
        # Use rhythm section family which exists in bigband
        note_events = [
            NoteEvent(pitch_midi=60.0, start_time=0.0, duration=1.0, instrument_family=BIGBAND_RHYTHM_SECTION),
        ]
        
        # Should work with bigband ensemble
        create_visualization(note_events, output_path_bb, ensemble=ENSEMBLE_BIGBAND)
        assert output_path_bb.exists()

    def test_transparent_background(self, tmp_path, monkeypatch):
        """Test that transparent=True sets figure and axes backgrounds to transparent."""
        output_path = tmp_path / "output.png"
        
        note_events = [
            NoteEvent(pitch_midi=60.0, start_time=0.0, duration=1.0, instrument_family=ORCHESTRA_STRINGS),
        ]
        
        captured_fig = {}
        captured_ax = {}
        captured_savefig_kwargs = {}
        real_subplots = plt.subplots
        
        def fake_subplots(*args, **kwargs):
            fig, ax = real_subplots(*args, **kwargs)
            captured_fig["fig"] = fig
            captured_ax["ax"] = ax
            # Patch savefig on this specific figure instance
            original_savefig = fig.savefig
            def patched_savefig(path, **save_kwargs):
                captured_savefig_kwargs.update(save_kwargs)
                return original_savefig(path, **save_kwargs)
            fig.savefig = patched_savefig
            return fig, ax
        
        monkeypatch.setattr(plt, "subplots", fake_subplots)
        
        create_visualization(
            note_events,
            output_path,
            ensemble=ENSEMBLE_ORCHESTRA,
            transparent=True,
        )
        
        # Verify file was created
        assert output_path.exists()
        
        # Verify figure and axes have transparent backgrounds
        fig = captured_fig["fig"]
        ax = captured_ax["ax"]
        fig_facecolor = fig.patch.get_facecolor()
        ax_facecolor = ax.get_facecolor()
        # Matplotlib may return 'none', (1,1,1,0), or (0,0,0,0) for transparent
        assert (fig_facecolor == 'none' or 
                (isinstance(fig_facecolor, tuple) and len(fig_facecolor) == 4 and fig_facecolor[3] == 0))
        assert (ax_facecolor == 'none' or 
                (isinstance(ax_facecolor, tuple) and len(ax_facecolor) == 4 and ax_facecolor[3] == 0))
        
        # Verify savefig was called with transparent=True
        assert captured_savefig_kwargs.get("transparent") is True

    def test_non_transparent_background_default(self, tmp_path, monkeypatch):
        """Test that transparent=False (default) uses opaque backgrounds."""
        output_path = tmp_path / "output.png"
        
        note_events = [
            NoteEvent(pitch_midi=60.0, start_time=0.0, duration=1.0, instrument_family=ORCHESTRA_STRINGS),
        ]
        
        captured_savefig_kwargs = {}
        real_subplots = plt.subplots
        
        def fake_subplots(*args, **kwargs):
            fig, ax = real_subplots(*args, **kwargs)
            # Patch savefig on this specific figure instance
            original_savefig = fig.savefig
            def patched_savefig(path, **save_kwargs):
                captured_savefig_kwargs.update(save_kwargs)
                return original_savefig(path, **save_kwargs)
            fig.savefig = patched_savefig
            return fig, ax
        
        monkeypatch.setattr(plt, "subplots", fake_subplots)
        
        create_visualization(
            note_events,
            output_path,
            ensemble=ENSEMBLE_ORCHESTRA,
            transparent=False,  # Explicitly set to False
        )
        
        # Verify file was created
        assert output_path.exists()
        
        # Verify savefig was called with transparent=False (or not set, which defaults to False)
        assert captured_savefig_kwargs.get("transparent") is not True


class TestConvertMusicxmlToPng:
    """Test full conversion function."""

    def test_successful_conversion_default_params(self, tmp_path):
        """Test successful conversion with default parameters."""
        # Create a minimal MusicXML file
        score = stream.Score()
        part = stream.Part()
        part.append(instrument.Violin())
        n = note.Note("C4")
        n.quarterLength = 1.0
        part.append(n)
        score.append(part)
        
        input_path = tmp_path / "test.mxl"
        score.write("musicxml", input_path)
        
        output_path = convert_musicxml_to_png(input_path)
        
        assert output_path.exists()
        assert output_path.suffix == ".png"
        assert output_path.stem == "test"

    def test_custom_output_path(self, tmp_path):
        """Test conversion with custom output path."""
        score = stream.Score()
        part = stream.Part()
        part.append(instrument.Violin())
        n = note.Note("C4")
        n.quarterLength = 1.0
        part.append(n)
        score.append(part)
        
        input_path = tmp_path / "test.mxl"
        output_path = tmp_path / "custom_output.png"
        score.write("musicxml", input_path)
        
        result_path = convert_musicxml_to_png(input_path, output_path=output_path)
        
        assert result_path == output_path
        assert output_path.exists()

    def test_cli_rejects_staccato_below_min(self, tmp_path, capsys, monkeypatch):
        """CLI should error when staccato factor is below allowed range."""
        score = stream.Score()
        part = stream.Part()
        part.append(instrument.Violin())
        part.append(note.Note("C4"))
        score.append(part)

        input_path = tmp_path / "test.mxl"
        score.write("musicxml", input_path)

        monkeypatch.setattr(sys, "argv", ["musicxml-to-png", str(input_path), "--no-output", "--staccato-factor", "0.05"])
        with pytest.raises(SystemExit) as exc:
            cli_module.main()

        assert exc.value.code == 1
        err = capsys.readouterr().err
        assert "staccato-factor must be between" in err

    def test_cli_rejects_staccato_above_max(self, tmp_path, capsys, monkeypatch):
        """CLI should error when staccato factor is above allowed range."""
        score = stream.Score()
        part = stream.Part()
        part.append(instrument.Violin())
        part.append(note.Note("C4"))
        score.append(part)

        input_path = tmp_path / "test.mxl"
        score.write("musicxml", input_path)

        monkeypatch.setattr(sys, "argv", ["musicxml-to-png", str(input_path), "--no-output", "--staccato-factor", "1.5"])
        with pytest.raises(SystemExit) as exc:
            cli_module.main()

        assert exc.value.code == 1
        err = capsys.readouterr().err
        assert "staccato-factor must be between" in err

    def test_disable_rehearsal_marks(self, tmp_path):
        """Conversion should succeed with rehearsal marks disabled."""
        score = stream.Score()
        part = stream.Part()
        part.append(instrument.Violin())
        part.append(note.Note("C4"))
        score.append(part)

        input_path = tmp_path / "test.mxl"
        score.write("musicxml", input_path)

        output_path = convert_musicxml_to_png(input_path, show_rehearsal_marks=False)
        assert output_path.exists()

    def test_disable_legend(self, tmp_path):
        """Conversion should succeed with legend disabled."""
        score = stream.Score()
        part = stream.Part()
        part.append(instrument.Violin())
        n = note.Note("C4")
        n.quarterLength = 1.0
        part.append(n)
        score.append(part)

        input_path = tmp_path / "test.mxl"
        score.write("musicxml", input_path)

        output_path = convert_musicxml_to_png(input_path, show_legend=False)
        assert output_path.exists()

    def test_cli_slice_range_with_measure_unit_aliases_to_bar(self, tmp_path, monkeypatch):
        """Slice range with timeline_unit measure should map to bar slicing."""
        score = stream.Score()
        part = stream.Part()
        part.append(instrument.Violin())
        part.append(note.Note("C4"))
        score.append(part)

        input_path = tmp_path / "test.mxl"
        score.write("musicxml", input_path)

        captured = {}

        def fake_convert_musicxml_to_png(**kwargs):
            captured.update(kwargs)
            class DummyPath(Path):
                _flavour = Path(".")._flavour
            return DummyPath("/tmp/out.png")

        monkeypatch.setattr(cli_module, "convert_musicxml_to_png", fake_convert_musicxml_to_png)
        monkeypatch.setattr(sys, "argv", ["musicxml-to-png", str(input_path), "--no-output", "--timeline-unit", "measure", "--slice-range", "1-2"])

        cli_module.main()

        assert captured.get("slice_mode") == "bar"
        assert captured.get("slice_start") == 1
        assert captured.get("slice_end") == 2

    def test_cli_slice_range_defaults_to_bar(self, tmp_path, monkeypatch):
        """Providing --slice-range alone should default to bar slicing."""
        score = stream.Score()
        part = stream.Part()
        part.append(instrument.Violin())
        part.append(note.Note("C4"))
        score.append(part)

        input_path = tmp_path / "test.mxl"
        score.write("musicxml", input_path)

        captured = {}

        def fake_convert_musicxml_to_png(**kwargs):
            captured.update(kwargs)
            class DummyPath(Path):
                _flavour = Path(".")._flavour
            return DummyPath("/tmp/out.png")

        monkeypatch.setattr(cli_module, "convert_musicxml_to_png", fake_convert_musicxml_to_png)
        monkeypatch.setattr(sys, "argv", ["musicxml-to-png", str(input_path), "--no-output", "--slice-range", "3-5"])

        cli_module.main()

        assert captured.get("slice_mode") == "bar"
        assert captured.get("slice_start") == 3
        assert captured.get("slice_end") == 5

    def test_cli_timeline_unit_passes_through(self, tmp_path, monkeypatch):
        """Timeline unit should be forwarded to converter."""
        score = stream.Score()
        part = stream.Part()
        part.append(instrument.Viola())
        part.append(note.Note("C4"))
        score.append(part)

        input_path = tmp_path / "test.mxl"
        score.write("musicxml", input_path)

        captured = {}

        def fake_convert_musicxml_to_png(**kwargs):
            captured.update(kwargs)
            class DummyPath(Path):
                _flavour = Path(".")._flavour
            return DummyPath("/tmp/out.png")

        monkeypatch.setattr(cli_module, "convert_musicxml_to_png", fake_convert_musicxml_to_png)
        monkeypatch.setattr(sys, "argv", ["musicxml-to-png", str(input_path), "--no-output", "--timeline-unit", "measure"])

        cli_module.main()

        assert captured.get("timeline_unit") == "measure"

    def test_slice_range_bar_is_end_exclusive(self, tmp_path, monkeypatch):
        """Bar slicing should be start-inclusive, end-exclusive."""
        score = stream.Score()
        part = stream.Part()
        part.append(instrument.Violin())

        for i in range(1, 5):
            m = stream.Measure(number=i)
            n = note.Note("C4")
            n.quarterLength = 1.0
            m.append(n)
            part.append(m)
        score.append(part)

        captured = {}

        def fake_create_visualization(*args, **kwargs):
            captured["called"] = True
            captured["note_events"] = args[0] if args else kwargs.get("note_events")
            captured.update(kwargs)
            return None

        monkeypatch.setattr(cli_module, "convert_musicxml_to_png", convert_musicxml_to_png)
        monkeypatch.setattr("musicxml_to_png.converter.create_visualization", fake_create_visualization)

        input_path = tmp_path / "in.mxl"
        score.write("musicxml", input_path)
        output_path = tmp_path / "out.png"
        convert_musicxml_to_png(
            input_path=input_path,
            score=score,
            output_path=output_path,
            slice_mode="bar",
            slice_start=2,
            slice_end=4,
            timeline_unit="bar",
        )

        measure_ticks = captured.get("measure_ticks")
        assert measure_ticks == [(2, 0.0), (3, 1.0)]

    def test_slice_range_beat_is_one_indexed_input(self, tmp_path, monkeypatch):
        """Beat slicing should treat inputs as 1-based and end-exclusive."""
        score = stream.Score()
        part = stream.Part()
        part.append(instrument.Flute())

        for i, pitch_name in enumerate(["C4", "D4", "E4"], start=0):
            n = note.Note(pitch_name)
            n.quarterLength = 1.0
            part.insert(float(i), n)
        score.append(part)

        input_path = tmp_path / "in.mxl"
        score.write("musicxml", input_path)
        output_path = tmp_path / "out.png"

        captured = {}

        def fake_create_visualization(*args, **kwargs):
            captured["called"] = True
            captured["note_events"] = args[0] if args else kwargs.get("note_events")
            captured.update(kwargs)
            return None

        monkeypatch.setattr("musicxml_to_png.converter.create_visualization", fake_create_visualization)

        convert_musicxml_to_png(
            input_path=input_path,
            score=score,
            output_path=output_path,
            slice_mode="beat",
            slice_start=2,
            slice_end=3,
            timeline_unit="beat",
        )

        note_events = captured.get("note_events")
        assert captured.get("called") is True
        assert note_events is not None
        # Should include only the second note (beat 2), rebased to start at 0
        assert len(note_events) == 1
        assert note_events[0].pitch_midi == 62.0  # D4
        assert note_events[0].start_time == 0.0
        assert note_events[0].duration == 1.0


    def test_disable_title(self, tmp_path):
        """Conversion should succeed with title disabled."""
        score = stream.Score()
        part = stream.Part()
        part.append(instrument.Violin())
        n = note.Note("C4")
        n.quarterLength = 1.0
        part.append(n)
        score.append(part)

        input_path = tmp_path / "test.mxl"
        score.write("musicxml", input_path)

        output_path = convert_musicxml_to_png(input_path, show_title=False)
        assert output_path.exists()

    def test_custom_title(self, tmp_path):
        """Test conversion with custom title."""
        score = stream.Score()
        part = stream.Part()
        part.append(instrument.Violin())
        n = note.Note("C4")
        n.quarterLength = 1.0
        part.append(n)
        score.append(part)
        
        input_path = tmp_path / "test.mxl"
        score.write("musicxml", input_path)
        
        output_path = convert_musicxml_to_png(input_path, title="My Custom Title")
        assert output_path.exists()

    def test_transparent_background_conversion(self, tmp_path):
        """Test conversion with transparent background."""
        score = stream.Score()
        part = stream.Part()
        part.append(instrument.Violin())
        n = note.Note("C4")
        n.quarterLength = 1.0
        part.append(n)
        score.append(part)
        
        input_path = tmp_path / "test.mxl"
        score.write("musicxml", input_path)
        
        output_path = convert_musicxml_to_png(input_path, transparent=True)
        
        assert output_path.exists()
        assert output_path.suffix == ".png"

    def test_show_connections_conversion(self, tmp_path):
        """Test conversion with show_connections enabled."""
        score = stream.Score()
        part = stream.Part()
        part.append(instrument.Violin())
        n1 = note.Note("C4")
        n1.quarterLength = 1.0
        part.append(n1)
        n2 = note.Note("D4")
        n2.quarterLength = 1.0
        part.insert(1.0, n2)  # Adjacent note
        score.append(part)
        
        input_path = tmp_path / "test.mxl"
        score.write("musicxml", input_path)
        
        output_path = convert_musicxml_to_png(input_path, show_connections=True)
        
        assert output_path.exists()
        assert output_path.suffix == ".png"


class TestNoteConnections:
    """Test note connection detection and visualization."""

    def test_connection_detection_adjacent_notes(self):
        """Test that adjacent notes (no rest) are detected as connected."""
        note_events = [
            NoteEvent(pitch_midi=60.0, start_time=0.0, duration=1.0, instrument_family=ORCHESTRA_STRINGS, original_duration=1.0),
            NoteEvent(pitch_midi=62.0, start_time=1.0, duration=1.0, instrument_family=ORCHESTRA_STRINGS, original_duration=1.0),
            NoteEvent(pitch_midi=64.0, start_time=2.0, duration=1.0, instrument_family=ORCHESTRA_STRINGS, original_duration=1.0),
        ]
        
        connections = detect_note_connections(note_events)
        
        assert len(connections) == 2
        assert (0, 1) in connections
        assert (1, 2) in connections

    def test_connection_detection_with_rest(self):
        """Test that notes separated by a rest are not connected."""
        note_events = [
            NoteEvent(pitch_midi=60.0, start_time=0.0, duration=1.0, instrument_family=ORCHESTRA_STRINGS, original_duration=1.0),
            NoteEvent(pitch_midi=62.0, start_time=2.0, duration=1.0, instrument_family=ORCHESTRA_STRINGS, original_duration=1.0),  # Gap at 1.0
        ]
        
        connections = detect_note_connections(note_events)
        
        assert len(connections) == 0

    def test_connection_detection_per_instrument(self):
        """Test that connections are only within the same instrument."""
        note_events = [
            NoteEvent(pitch_midi=60.0, start_time=0.0, duration=1.0, instrument_family=ORCHESTRA_STRINGS, instrument_label="Violin", original_duration=1.0),
            NoteEvent(pitch_midi=62.0, start_time=1.0, duration=1.0, instrument_family=ORCHESTRA_WINDS, instrument_label="Flute", original_duration=1.0),
        ]
        
        connections = detect_note_connections(note_events)
        
        assert len(connections) == 0  # Different instruments, no connection

    def test_connection_detection_staccato_notes(self):
        """Test that staccato notes still connect if adjacent (using original_duration)."""
        note_events = [
            NoteEvent(pitch_midi=60.0, start_time=0.0, duration=0.4, instrument_family=ORCHESTRA_STRINGS, original_duration=1.0),  # Staccato shortened
            NoteEvent(pitch_midi=62.0, start_time=1.0, duration=1.0, instrument_family=ORCHESTRA_STRINGS, original_duration=1.0),  # Adjacent based on original
        ]
        
        connections = detect_note_connections(note_events)
        
        assert len(connections) == 1
        assert (0, 1) in connections

    def test_connection_detection_deduplicates_split_segments(self):
        """Long note split by overlaps should not spawn duplicate connections."""
        # Simulate a long note split into segments that share the same original end (4.0)
        note_events = [
            NoteEvent(pitch_midi=60.0, start_time=0.0, duration=1.0, instrument_family=ORCHESTRA_STRINGS, instrument_label="Violin", original_duration=4.0),
            NoteEvent(pitch_midi=60.0, start_time=1.0, duration=1.0, instrument_family=ORCHESTRA_STRINGS, instrument_label="Violin", original_duration=3.0),
            NoteEvent(pitch_midi=60.0, start_time=2.0, duration=1.0, instrument_family=ORCHESTRA_STRINGS, instrument_label="Violin", original_duration=2.0),
            NoteEvent(pitch_midi=60.0, start_time=3.0, duration=1.0, instrument_family=ORCHESTRA_STRINGS, instrument_label="Violin", original_duration=1.0),
            NoteEvent(pitch_midi=62.0, start_time=4.0, duration=1.0, instrument_family=ORCHESTRA_STRINGS, instrument_label="Violin", original_duration=1.0),
        ]

        connections = detect_note_connections(note_events)

        # Connection should start from the last segment's visual end (index 3) to the next note
        assert connections == [(3, 4)]

    def test_connection_detection_handles_near_equal_original_ends(self):
        """Tiny float differences in original ends should still deduplicate to a single connection."""
        note_events = [
            NoteEvent(pitch_midi=60.0, start_time=0.0, duration=1.0, instrument_family=ORCHESTRA_STRINGS, instrument_label="Violin", original_duration=3.0004),
            NoteEvent(pitch_midi=60.0, start_time=1.0, duration=1.0, instrument_family=ORCHESTRA_STRINGS, instrument_label="Violin", original_duration=2.0004),
            NoteEvent(pitch_midi=60.0, start_time=2.0, duration=1.0, instrument_family=ORCHESTRA_STRINGS, instrument_label="Violin", original_duration=1.0002),
            NoteEvent(pitch_midi=62.0, start_time=3.0009, duration=1.0, instrument_family=ORCHESTRA_STRINGS, instrument_label="Violin", original_duration=1.0),
        ]

        connections = detect_note_connections(note_events)
        assert connections == [(2, 3)]

    def test_connection_detection_only_one_from_simultaneous_sources(self):
        """When multiple notes start together, only one connection should lead into the next start."""
        note_events = [
            NoteEvent(pitch_midi=60.0, start_time=0.0, duration=1.0, instrument_family=ORCHESTRA_STRINGS, instrument_label="Violin", original_duration=1.0),
            NoteEvent(pitch_midi=62.0, start_time=0.0, duration=1.0, instrument_family=ORCHESTRA_STRINGS, instrument_label="Violin", original_duration=1.0),
            NoteEvent(pitch_midi=64.0, start_time=1.0, duration=1.0, instrument_family=ORCHESTRA_STRINGS, instrument_label="Violin", original_duration=1.0),
            NoteEvent(pitch_midi=67.0, start_time=1.0, duration=1.0, instrument_family=ORCHESTRA_STRINGS, instrument_label="Violin", original_duration=1.0),
        ]

        connections = detect_note_connections(note_events)
        assert connections == [(0, 2)]

    def test_connection_visualization(self, tmp_path):
        """Test that connections are rendered when show_connections=True."""
        output_path = tmp_path / "output.png"
        
        note_events = [
            NoteEvent(pitch_midi=60.0, start_time=0.0, duration=1.0, instrument_family=ORCHESTRA_STRINGS, original_duration=1.0),
            NoteEvent(pitch_midi=62.0, start_time=1.0, duration=1.0, instrument_family=ORCHESTRA_STRINGS, original_duration=1.0),
        ]
        
        connections = [(0, 1)]
        
        create_visualization(
            note_events,
            output_path,
            ensemble=ENSEMBLE_ORCHESTRA,
            show_connections=True,
            connections=connections,
        )
        
        assert output_path.exists()

    def test_connection_curve_render(self, tmp_path):
        """Connection curves should render without error when enabled."""
        output_path = tmp_path / "curve.png"

        note_events = [
            NoteEvent(pitch_midi=60.0, start_time=0.0, duration=1.0, instrument_family=ORCHESTRA_STRINGS, original_duration=1.0),
            NoteEvent(pitch_midi=62.0, start_time=2.0, duration=1.0, instrument_family=ORCHESTRA_STRINGS, original_duration=1.0),
        ]
        connections = [(0, 1)]

        create_visualization(
            note_events,
            output_path,
            ensemble=ENSEMBLE_ORCHESTRA,
            show_connections=True,
            connections=connections,
            connection_config=ConnectionConfig(curve_height_factor=0.3),
        )

        assert output_path.exists()

    def test_connection_config_passes_through_converter(self, tmp_path, monkeypatch):
        """Connection styling overrides should reach visualization config."""
        score = stream.Score()
        part = stream.Part()
        part.append(instrument.Violin())
        part.append(note.Note("C4"))
        part.append(note.Note("D4"))
        score.append(part)

        captured = {}

        def fake_create_visualization(*args, **kwargs):
            captured["config"] = kwargs.get("config")
            return tmp_path / "dummy.png"

        monkeypatch.setattr("musicxml_to_png.converter.create_visualization", fake_create_visualization)

        # Write a temporary MusicXML file so converter's file check passes
        input_path = tmp_path / "in.mxl"
        score.write("musicxml", input_path)

        convert_musicxml_to_png(
            input_path=input_path,
            score=score,
            output_path=tmp_path / "out.png",
            show_connections=True,
            connection_max_gap=1.5,
            connection_alpha=0.4,
            connection_min_alpha=0.2,
            connection_fade_start=2.0,
            connection_fade_end=4.0,
            connection_linewidth=1.3,
            write_output=False,
        )

        cfg = captured.get("config")
        assert cfg is not None
        conn_cfg = cfg.connections
        assert conn_cfg.max_gap == 1.5
        assert conn_cfg.alpha == 0.4
        assert conn_cfg.min_alpha == 0.2
        assert conn_cfg.fade_start == 2.0
        assert conn_cfg.fade_end == 4.0
        assert conn_cfg.linewidth == 1.3


class TestConvertMusicxmlToPngErrors:
    """Test error handling in conversion function."""

    def test_file_not_found_error(self):
        """Test that missing file raises FileNotFoundError."""
        non_existent = Path("/nonexistent/file.mxl")
        
        with pytest.raises(FileNotFoundError):
            convert_musicxml_to_png(non_existent)

    def test_invalid_musicxml_raises_error(self, tmp_path):
        """Test that invalid MusicXML raises ValueError."""
        invalid_file = tmp_path / "invalid.mxl"
        invalid_file.write_text("This is not valid MusicXML")
        
        with pytest.raises(ValueError, match="Failed to parse"):
            convert_musicxml_to_png(invalid_file)

    def test_empty_musicxml_raises_error(self, tmp_path):
        """Test that empty MusicXML (no notes) raises ValueError."""
        score = stream.Score()
        part = stream.Part()
        part.append(instrument.Violin())
        # No notes, only rests or empty
        score.append(part)
        
        input_path = tmp_path / "empty.mxl"
        score.write("musicxml", input_path)
        
        with pytest.raises(ValueError, match="No notes found"):
            convert_musicxml_to_png(input_path)


class TestConvertMusicxmlToPngParameters:
    """Test various parameter combinations in conversion function."""

    def test_ensemble_parameter(self, tmp_path):
        """Test conversion with different ensemble types."""
        score = stream.Score()
        part = stream.Part()
        part.append(instrument.Piano())  # Piano is strings in orchestra, rhythm in bigband
        n = note.Note("C4")
        n.quarterLength = 1.0
        part.append(n)
        score.append(part)
        
        input_path = tmp_path / "test.mxl"
        score.write("musicxml", input_path)
        
        # Test both ensembles
        output_orch = convert_musicxml_to_png(input_path, ensemble=ENSEMBLE_ORCHESTRA)
        output_bb = convert_musicxml_to_png(input_path, ensemble=ENSEMBLE_BIGBAND)
        
        assert output_orch.exists()
        assert output_bb.exists()

    def test_show_grid_parameter(self, tmp_path):
        """Test conversion with grid disabled."""
        score = stream.Score()
        part = stream.Part()
        part.append(instrument.Violin())
        n = note.Note("C4")
        n.quarterLength = 1.0
        part.append(n)
        score.append(part)
        
        input_path = tmp_path / "test.mxl"
        score.write("musicxml", input_path)
        
        output_path = convert_musicxml_to_png(input_path, show_grid=False)
        assert output_path.exists()

    def test_minimal_mode_parameter(self, tmp_path):
        """Test conversion with minimal mode."""
        score = stream.Score()
        part = stream.Part()
        part.append(instrument.Violin())
        n = note.Note("C4")
        n.quarterLength = 1.0
        part.append(n)
        score.append(part)
        
        input_path = tmp_path / "test.mxl"
        score.write("musicxml", input_path)
        
        output_path = convert_musicxml_to_png(input_path, minimal=True)
        assert output_path.exists()

    def test_no_output_skips_writing_file(self, tmp_path):
        """Conversion pipeline should run without writing output when requested."""
        score = stream.Score()
        part = stream.Part()
        part.append(instrument.Violin())
        n = note.Note("C4")
        n.quarterLength = 1.0
        part.append(n)
        score.append(part)

        input_path = tmp_path / "test.mxl"
        score.write("musicxml", input_path)

        output_path = convert_musicxml_to_png(input_path, write_output=False)

        # Should still return the default output path, but file is intentionally absent
        assert output_path == input_path.with_suffix(".png")
        assert not output_path.exists()
