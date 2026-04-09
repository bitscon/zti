"""Tests for ZTI validation layer — cross-layer integrity."""

from __future__ import annotations

from zti.detection import DetectedPattern, detect_patterns, Interaction, InteractionBundle
from zti.registry import DEFAULT_REGISTRY, PATTERN_REGISTRY_VERSION
from zti.validation import validate_cross_layer_integrity, validate_registry_structure


def _detected(
    *,
    pattern_id: str = "exploratory",
    pattern_type: str = "exploratory",
    evidence_refs: tuple[tuple[str, int], ...] = (("i-001", 10), ("i-002", 20), ("i-003", 30)),
    interaction_ids: tuple[str, ...] = ("i-001", "i-002", "i-003"),
    session_id: str = "sess-001",
    confidence: float = 0.777778,
    version: str = PATTERN_REGISTRY_VERSION,
) -> DetectedPattern:
    return DetectedPattern(
        pattern_id=pattern_id,
        pattern_type=pattern_type,
        detection_confidence=confidence,
        evidence_refs=evidence_refs,
        session_id=session_id,
        interaction_ids=interaction_ids,
        version=version,
    )


def test_registry_structure_valid():
    valid, err = validate_registry_structure(DEFAULT_REGISTRY)
    assert valid is True
    assert err is None


def test_cross_layer_integrity_valid():
    bundle = InteractionBundle(
        session_id="s",
        interactions=(
            Interaction("i-001", ("open_question_density",), 10),
            Interaction("i-002", ("option_space_expansion",), 20),
            Interaction("i-003", ("hypothesis_generation",), 30),
        ),
    )
    patterns, _, err = detect_patterns(bundle, DEFAULT_REGISTRY)
    assert err is None

    valid, ci_err = validate_cross_layer_integrity(tuple(patterns), DEFAULT_REGISTRY)
    assert valid is True
    assert ci_err is None


def test_wrong_version_fails_integrity():
    dp = _detected(version="0.0.0")
    valid, err = validate_cross_layer_integrity((dp,), DEFAULT_REGISTRY)
    assert valid is False


def test_wrong_pattern_type_fails_integrity():
    dp = _detected(pattern_type="directive")  # pattern_id="exploratory" but wrong type
    valid, err = validate_cross_layer_integrity((dp,), DEFAULT_REGISTRY)
    assert valid is False


def test_unknown_pattern_id_fails_integrity():
    dp = _detected(pattern_id="unknown_pattern")
    valid, err = validate_cross_layer_integrity((dp,), DEFAULT_REGISTRY)
    assert valid is False


def test_empty_detected_patterns_fails():
    valid, err = validate_cross_layer_integrity((), DEFAULT_REGISTRY)
    assert valid is False
