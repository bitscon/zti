"""Tests for ZTI detection engine — deterministic, fail-closed."""

from __future__ import annotations

import pytest

from zti.detection import Interaction, InteractionBundle, detect_patterns
from zti.errors import DetectionErrorCode
from zti.registry import DEFAULT_REGISTRY, PATTERN_REGISTRY_VERSION


def _bundle(
    session_id: str = "sess-001",
    interactions: list[tuple[str, tuple[str, ...], int]] | None = None,
) -> InteractionBundle:
    if interactions is None:
        interactions = [
            ("i-001", ("open_question_density", "option_space_expansion", "hypothesis_generation"), 10),
        ]
    return InteractionBundle(
        session_id=session_id,
        interactions=tuple(
            Interaction(interaction_id=iid, signal_hits=signals, source_line=line)
            for iid, signals, line in interactions
        ),
    )


def test_exploratory_detected():
    bundle = _bundle(interactions=[
        ("i-001", ("open_question_density",), 1),
        ("i-002", ("option_space_expansion",), 2),
        ("i-003", ("hypothesis_generation",), 3),
    ])
    patterns, refs, err = detect_patterns(bundle, DEFAULT_REGISTRY)
    assert err is None
    assert patterns is not None
    ids = [p.pattern_id for p in patterns]
    assert "exploratory" in ids


def test_directive_detected():
    bundle = _bundle(interactions=[
        ("i-001", ("imperative_command_density",), 1),
        ("i-002", ("constraint_specificity",), 2),
        ("i-003", ("single_path_instruction",), 3),
    ])
    patterns, _, err = detect_patterns(bundle, DEFAULT_REGISTRY)
    assert err is None
    assert any(p.pattern_id == "directive" for p in patterns)


def test_no_matching_signals_fails():
    bundle = _bundle(interactions=[
        ("i-001", ("unknown_signal",), 1),
    ])
    patterns, _, err = detect_patterns(bundle, DEFAULT_REGISTRY)
    assert patterns is None
    assert err == DetectionErrorCode.PATTERN_NOT_FOUND.value


def test_empty_session_id_fails():
    bundle = InteractionBundle(
        session_id="",
        interactions=(Interaction(interaction_id="i-001", signal_hits=("open_question_density",), source_line=1),),
    )
    patterns, _, err = detect_patterns(bundle, DEFAULT_REGISTRY)
    assert patterns is None
    assert err == DetectionErrorCode.INVALID_INTERACTION_DATA.value


def test_evidence_refs_are_populated():
    bundle = _bundle(interactions=[
        ("i-001", ("open_question_density",), 5),
        ("i-002", ("option_space_expansion",), 10),
        ("i-003", ("hypothesis_generation",), 15),
    ])
    patterns, refs, err = detect_patterns(bundle, DEFAULT_REGISTRY)
    assert err is None
    assert len(refs) > 0
    for interaction_id, source_line in refs:
        assert isinstance(interaction_id, str)
        assert source_line > 0


def test_detected_pattern_version():
    bundle = _bundle(interactions=[
        ("i-001", ("open_question_density",), 1),
        ("i-002", ("option_space_expansion",), 2),
        ("i-003", ("hypothesis_generation",), 3),
    ])
    patterns, _, err = detect_patterns(bundle, DEFAULT_REGISTRY)
    assert err is None
    for p in patterns:
        assert p.version == PATTERN_REGISTRY_VERSION


def test_confidence_between_zero_and_one():
    bundle = _bundle(interactions=[
        ("i-001", ("open_question_density",), 1),
        ("i-002", ("option_space_expansion",), 2),
        ("i-003", ("hypothesis_generation",), 3),
    ])
    patterns, _, err = detect_patterns(bundle, DEFAULT_REGISTRY)
    assert err is None
    for p in patterns:
        assert 0.0 < p.detection_confidence <= 1.0


def test_result_is_deterministic():
    bundle = _bundle(interactions=[
        ("i-001", ("open_question_density",), 1),
        ("i-002", ("option_space_expansion",), 2),
        ("i-003", ("hypothesis_generation",), 3),
    ])
    r1, _, _ = detect_patterns(bundle, DEFAULT_REGISTRY)
    r2, _, _ = detect_patterns(bundle, DEFAULT_REGISTRY)
    assert [(p.pattern_id, p.detection_confidence) for p in r1] == [(p.pattern_id, p.detection_confidence) for p in r2]
