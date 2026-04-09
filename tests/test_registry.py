"""Tests for ZTI registry — schema enforcement and validation."""

from __future__ import annotations

import pytest

from zti.registry import (
    DEFAULT_REGISTRY,
    PATTERN_REGISTRY,
    PATTERN_REGISTRY_INVALID,
    PATTERN_REGISTRY_VERSION,
    PATTERN_SCHEMA_INVALID,
    InteractionPattern,
    PatternRegistry,
    PatternType,
    validate_pattern_registry,
)


def _valid_pattern(
    *,
    pattern_id: str = "custom",
    pattern_type: str = PatternType.EXPLORATORY.value,
    required_signals: tuple[str, ...] = ("sig_a", "sig_b"),
    scoring_weights: dict[str, int] | None = None,
) -> InteractionPattern:
    return InteractionPattern(
        pattern_id=pattern_id,
        pattern_type=pattern_type,
        rule_version=PATTERN_REGISTRY_VERSION,
        description="Test pattern",
        required_signals=required_signals,
        scoring_weights=scoring_weights or {"sig_a": 2, "sig_b": 1},
    )


def test_default_registry_validates():
    valid, reason = validate_pattern_registry()
    assert valid is True
    assert reason == ""


def test_default_registry_singleton_valid():
    assert DEFAULT_REGISTRY.version == PATTERN_REGISTRY_VERSION
    assert len(DEFAULT_REGISTRY.patterns) == 5


def test_all_canonical_pattern_types_present():
    types = {p.pattern_type for p in PATTERN_REGISTRY.values()}
    assert types == {"exploratory", "directive", "stalled", "iterative", "conflicting"}


def test_invalid_pattern_type_rejected():
    with pytest.raises(ValueError, match=PATTERN_SCHEMA_INVALID):
        _valid_pattern(pattern_type="dynamic")


def test_wrong_version_rejected():
    with pytest.raises(ValueError, match=PATTERN_SCHEMA_INVALID):
        InteractionPattern(
            pattern_id="p",
            pattern_type="exploratory",
            rule_version="0.0.0",
            description="bad version",
            required_signals=("a",),
            scoring_weights={"a": 1},
        )


def test_duplicate_signal_rejected():
    with pytest.raises(ValueError, match=PATTERN_SCHEMA_INVALID):
        InteractionPattern(
            pattern_id="p",
            pattern_type="exploratory",
            rule_version=PATTERN_REGISTRY_VERSION,
            description="desc",
            required_signals=("a", "a"),
            scoring_weights={"a": 1},
        )


def test_weight_key_mismatch_rejected():
    with pytest.raises(ValueError, match=PATTERN_SCHEMA_INVALID):
        InteractionPattern(
            pattern_id="p",
            pattern_type="exploratory",
            rule_version=PATTERN_REGISTRY_VERSION,
            description="desc",
            required_signals=("a", "b"),
            scoring_weights={"a": 1, "c": 2},  # c not in required_signals
        )


def test_duplicate_pattern_id_fails():
    duplicate = _valid_pattern(pattern_id="exploratory")
    invalid = dict(PATTERN_REGISTRY)
    invalid["extra-key"] = duplicate
    valid, reason = validate_pattern_registry(invalid)
    assert valid is False
    assert reason == PATTERN_REGISTRY_INVALID


def test_empty_registry_fails():
    valid, reason = validate_pattern_registry({})
    assert valid is False


def test_pattern_registry_container_validates():
    registry = PatternRegistry(version=PATTERN_REGISTRY_VERSION, patterns=PATTERN_REGISTRY)
    assert registry.version == PATTERN_REGISTRY_VERSION
