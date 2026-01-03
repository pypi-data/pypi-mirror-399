"""Ensemble detection heuristics leveraging existing instrument family mapping."""

from collections import Counter
from typing import List, Tuple

from music21 import instrument, stream

from musicxml_to_png.instruments import (
    BIGBAND_RHYTHM_SECTION,
    BIGBAND_SAXOPHONES,
    BIGBAND_TROMBONES,
    BIGBAND_TRUMPETS,
    BIGBAND_UNKNOWN,
    ENSEMBLE_BIGBAND,
    ENSEMBLE_ORCHESTRA,
    ENSEMBLE_UNGROUPED,
    ORCHESTRA_BRASS,
    ORCHESTRA_PERCUSSION,
    ORCHESTRA_STRINGS,
    ORCHESTRA_UNKNOWN,
    ORCHESTRA_WINDS,
    get_instrument_family,
)

# Weight tables give more credit to canonical families for each ensemble.
_ORCHESTRA_WEIGHTS = {
    ORCHESTRA_STRINGS: 1.0,
    ORCHESTRA_WINDS: 0.9,
    ORCHESTRA_BRASS: 0.9,
    ORCHESTRA_PERCUSSION: 0.8,
    ORCHESTRA_UNKNOWN: 0.2,
}

_BIGBAND_WEIGHTS = {
    BIGBAND_TRUMPETS: 1.0,
    BIGBAND_TROMBONES: 1.0,
    BIGBAND_SAXOPHONES: 1.0,
    BIGBAND_RHYTHM_SECTION: 1.0,
    BIGBAND_UNKNOWN: 0.1,
}


def _extract_part_metadata(score: stream.Score) -> List[tuple]:
    """Collect (midi_program, instrument_name) for each part."""
    parts_meta = []
    for part in score.parts:
        midi_program = None
        instrument_name = None

        for element in part.recurse().getElementsByClass(instrument.Instrument):
            if hasattr(element, "midiProgram") and element.midiProgram is not None:
                midi_program = element.midiProgram
            if hasattr(element, "instrumentName") and element.instrumentName:
                instrument_name = str(element.instrumentName)
            break

        if midi_program is None and instrument_name is None and part.partName:
            instrument_name = str(part.partName)

        parts_meta.append((midi_program, instrument_name))

    return parts_meta


def _base_confidence(family_counts: Counter, weights: dict, total_parts: int) -> float:
    return sum(count * weights.get(family, 0.1) for family, count in family_counts.items()) / total_parts


def _apply_small_ensemble_penalty(score: float, total_parts: int) -> float:
    if total_parts < 5:
        size_factor = max(0.2, total_parts / 5.0)
        score *= size_factor
    return max(0.0, min(1.0, score))


def _compute_confidence_orchestra(family_counts: Counter, total_parts: int) -> float:
    bonus = 0.0
    penalty = 0.0

    strings_ratio = family_counts.get(ORCHESTRA_STRINGS, 0) / total_parts
    winds_present = family_counts.get(ORCHESTRA_WINDS, 0) > 0
    brass_present = family_counts.get(ORCHESTRA_BRASS, 0) > 0
    percussion_present = family_counts.get(ORCHESTRA_PERCUSSION, 0) > 0
    families_present = sum(
        1
        for key in (ORCHESTRA_STRINGS, ORCHESTRA_WINDS, ORCHESTRA_BRASS, ORCHESTRA_PERCUSSION)
        if family_counts.get(key, 0) > 0
    )

    if strings_ratio >= 0.3:
        bonus += 0.25
    if strings_ratio >= 0.45:
        bonus += 0.1
    if strings_ratio >= 0.6:
        bonus += 0.1
    if winds_present and brass_present:
        bonus += 0.05
    if winds_present and brass_present and percussion_present:
        bonus += 0.1
    if families_present <= 1:
        penalty += 0.25
    if families_present >= 3:
        bonus += 0.1
    if total_parts >= 12:
        bonus += 0.05
    if total_parts >= 24:
        bonus += 0.05

    base = _base_confidence(family_counts, _ORCHESTRA_WEIGHTS, total_parts)
    final = base + bonus - penalty

    if strings_ratio == 0:
        final *= 0.25
    elif strings_ratio < 0.1:
        final *= 0.3
    elif strings_ratio < 0.2:
        final *= 0.35
    if families_present <= 1:
        final *= 0.25

    bigband_like_parts = (
        family_counts.get(BIGBAND_SAXOPHONES, 0)
        + family_counts.get(BIGBAND_TRUMPETS, 0)
        + family_counts.get(BIGBAND_TROMBONES, 0)
        + family_counts.get(BIGBAND_RHYTHM_SECTION, 0)
    )
    bigband_ratio = bigband_like_parts / total_parts
    if bigband_ratio > 0.5 and strings_ratio < 0.4:
        final *= 0.6
    if bigband_ratio > 0.65 and strings_ratio < 0.4:
        final *= 0.5

    if total_parts > 24:
        final *= 24.0 / float(total_parts)

    return final


def _compute_confidence_bigband(family_counts: Counter, orchestra_family_counts: Counter, total_parts: int) -> float:
    bonus = 0.0
    penalty = 0.0

    saxes = family_counts.get(BIGBAND_SAXOPHONES, 0)
    trumpets = family_counts.get(BIGBAND_TRUMPETS, 0)
    bones = family_counts.get(BIGBAND_TROMBONES, 0)
    rhythm = family_counts.get(BIGBAND_RHYTHM_SECTION, 0)
    unknown_ratio = family_counts.get(BIGBAND_UNKNOWN, 0) / total_parts
    strings_like_ratio = family_counts.get(ORCHESTRA_STRINGS, 0) / total_parts
    alt_strings_ratio = orchestra_family_counts.get(ORCHESTRA_STRINGS, 0) / total_parts
    strings_like_ratio = max(strings_like_ratio, alt_strings_ratio)

    if saxes > 0:
        bonus += 0.2
    if (trumpets + bones) > 0:
        bonus += 0.15
    if rhythm > 0:
        bonus += 0.1
    if saxes and (trumpets + bones) and rhythm:
        bonus += 0.2

    missing_sections = int(saxes == 0) + int((trumpets + bones) == 0) + int(rhythm == 0)
    if missing_sections >= 2:
        penalty += 0.35
    elif missing_sections == 1:
        penalty += 0.15

    if strings_like_ratio >= 0.2:
        penalty += 0.5
    if strings_like_ratio >= 0.35:
        penalty += 0.5
    if unknown_ratio > 0.35:
        penalty += 0.1 + 0.4 * (unknown_ratio - 0.35)
    if total_parts > 24:
        penalty += 0.2
    if total_parts > 40:
        penalty += 0.4

    base = _base_confidence(family_counts, _BIGBAND_WEIGHTS, total_parts)
    final = base + bonus - penalty

    sections_present = int(saxes > 0) + int((trumpets + bones) > 0) + int(rhythm > 0)
    coverage_factor = sections_present / 3 if sections_present > 0 else 0.0
    final *= coverage_factor
    if sections_present == 0:
        return 0.0

    core_parts = saxes + trumpets + bones + rhythm
    core_ratio = core_parts / total_parts
    if core_ratio < 0.6:
        final *= core_ratio / 0.6
    if core_ratio < 0.25:
        final *= core_ratio / 0.25

    return final


def _compute_confidence_ensemble(parts_meta: List[tuple], ensemble: str) -> float:
    """Compute a normalized confidence for how well parts match an ensemble."""
    if not parts_meta:
        return 0.0

    family_counts: Counter = Counter()
    orchestra_family_counts: Counter = Counter()

    for midi_program, instrument_name in parts_meta:
        family = get_instrument_family(
            midi_program=midi_program,
            instrument_name=instrument_name,
            ensemble=ensemble,
        )
        family_counts[family] += 1

        orchestra_family = get_instrument_family(
            midi_program=midi_program,
            instrument_name=instrument_name,
            ensemble=ENSEMBLE_ORCHESTRA,
        )
        orchestra_family_counts[orchestra_family] += 1

    total_parts = max(1, sum(family_counts.values()))

    if ensemble == ENSEMBLE_BIGBAND:
        final = _compute_confidence_bigband(family_counts, orchestra_family_counts, total_parts)
    else:
        final = _compute_confidence_orchestra(family_counts, total_parts)

    return _apply_small_ensemble_penalty(final, total_parts)


def detect_ensembles(score: stream.Score) -> List[Tuple[str, float]]:
    """
    Suggest likely ensembles for the given score.

    Returns:
        Sorted list of (ensemble, confidence) tuples; higher is more likely.
    """
    parts_meta = _extract_part_metadata(score)

    if not parts_meta:
        return [(ENSEMBLE_UNGROUPED, 0.0)]

    candidates = [ENSEMBLE_BIGBAND, ENSEMBLE_ORCHESTRA]

    scores = [(ensemble, _compute_confidence_ensemble(parts_meta, ensemble)) for ensemble in candidates]
    scores.sort(key=lambda item: item[1], reverse=True)
    scores.append((ENSEMBLE_UNGROUPED, 0.0))
    return scores

