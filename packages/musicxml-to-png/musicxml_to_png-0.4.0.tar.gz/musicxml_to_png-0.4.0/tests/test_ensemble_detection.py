import pytest
from pathlib import Path

from music21 import instrument, note, stream, converter

from musicxml_to_png.ensemble_detection import detect_ensembles
from musicxml_to_png.instruments import ENSEMBLE_BIGBAND, ENSEMBLE_ORCHESTRA
from musicxml_to_png.cli import _print_ensemble_suggestions


def _make_score(instrument_classes) -> stream.Score:
    score = stream.Score()
    for cls in instrument_classes:
        part = stream.Part()
        part.append(cls())
        n = note.Note("C4")
        n.quarterLength = 1.0
        part.append(n)
        score.append(part)
    return score


def test_detect_ensembles_prefers_orchestra_for_orchestral_mix():
    score = _make_score([instrument.Violin, instrument.Flute, instrument.Trumpet, instrument.SnareDrum])
    suggestions = detect_ensembles(score)
    confidences = dict(suggestions)
    assert confidences[ENSEMBLE_ORCHESTRA] > confidences[ENSEMBLE_BIGBAND]


def test_detect_ensembles_prefers_bigband_for_core_sections():
    fixture_path = Path(__file__).parent / "fixtures" / "test-bigband-1.mxl"
    if not fixture_path.exists():
        pytest.skip("test-bigband-1.mxl fixture missing")
    score = converter.parse(str(fixture_path))
    suggestions = detect_ensembles(score)
    confidences = dict(suggestions)
    assert confidences[ENSEMBLE_BIGBAND] > confidences[ENSEMBLE_ORCHESTRA]


def test_print_ensemble_suggestions_formats_output(capsys):
    suggestions = [
        (ENSEMBLE_BIGBAND, 1.0),
        (ENSEMBLE_ORCHESTRA, 0.92),
    ]
    _print_ensemble_suggestions(suggestions)
    out = capsys.readouterr().out.strip().splitlines()
    assert out[0] == 'Info: Ensemble detected: bigband (100%). Use "--ensemble bigband" to group instruments.'
    assert out[1] == 'Info: Ensemble detected: orchestra (92%). Use "--ensemble orchestra" to group instruments.'

