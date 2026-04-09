"""
Zero Trust Intelligence (ZTI) — Reference Protocol Implementation

This module defines deterministic verification and integrity rules for AI systems.
All logic is fail-closed and execution-free.
"""

from __future__ import annotations

from dataclasses import dataclass

from zti.errors import DetectionErrorCode, ValidationErrorCode
from zti.registry import PATTERN_REGISTRY_VERSION, PatternRegistry
from zti.validation import validate_registry_structure


@dataclass(frozen=True)
class Interaction:
    """A single observed interaction with its signal hits and source reference."""

    interaction_id: str
    signal_hits: tuple[str, ...]
    source_line: int


@dataclass(frozen=True)
class InteractionBundle:
    """A session's worth of interactions submitted for pattern detection."""

    session_id: str
    interactions: tuple[Interaction, ...]


@dataclass(frozen=True)
class DetectedPattern:
    """A pattern detected deterministically from an InteractionBundle.

    Every field is evidence-bound. detection_confidence is derived solely
    from registry scoring weights — not from any probabilistic model.
    """

    pattern_id: str
    pattern_type: str
    detection_confidence: float
    evidence_refs: tuple[tuple[str, int], ...]
    session_id: str
    interaction_ids: tuple[str, ...]
    version: str


_CANONICAL_PATTERN_TYPES: frozenset[str] = frozenset([
    "exploratory",
    "directive",
    "stalled",
    "iterative",
    "conflicting",
])


def _normalize_signal_hits(raw_hits: tuple[str, ...]) -> tuple[str, ...] | None:
    normalized: list[str] = []
    seen: set[str] = set()
    for raw_signal in raw_hits:
        if not isinstance(raw_signal, str):
            return None
        signal = raw_signal.strip()
        if not signal:
            return None
        if signal in seen:
            continue
        seen.add(signal)
        normalized.append(signal)
    if not normalized:
        return None
    return tuple(normalized)


def _validate_bundle(bundle: InteractionBundle) -> str | None:
    if not isinstance(bundle, InteractionBundle):
        return DetectionErrorCode.INVALID_INTERACTION_DATA.value
    if not isinstance(bundle.session_id, str) or not bundle.session_id.strip():
        return DetectionErrorCode.INVALID_INTERACTION_DATA.value
    if not isinstance(bundle.interactions, tuple) or not bundle.interactions:
        return DetectionErrorCode.INVALID_INTERACTION_DATA.value

    for interaction in bundle.interactions:
        if not isinstance(interaction, Interaction):
            return DetectionErrorCode.INVALID_INTERACTION_DATA.value
        if not isinstance(interaction.interaction_id, str) or not interaction.interaction_id.strip():
            return DetectionErrorCode.INVALID_INTERACTION_DATA.value
        if not isinstance(interaction.signal_hits, tuple):
            return DetectionErrorCode.INVALID_INTERACTION_DATA.value
        if _normalize_signal_hits(interaction.signal_hits) is None:
            return DetectionErrorCode.INVALID_INTERACTION_DATA.value
        if not isinstance(interaction.source_line, int) or isinstance(interaction.source_line, bool):
            return DetectionErrorCode.INVALID_INTERACTION_DATA.value

    return None


def _validate_registry(registry: PatternRegistry) -> str | None:
    if not isinstance(registry, PatternRegistry):
        return DetectionErrorCode.RULE_EVALUATION_FAILED.value
    if registry.version != PATTERN_REGISTRY_VERSION:
        return DetectionErrorCode.PATTERN_REGISTRY_VERSION_MISMATCH.value
    if not registry.patterns:
        return DetectionErrorCode.RULE_EVALUATION_FAILED.value
    return None


def _first_rule_evidence(
    *,
    interactions: tuple[Interaction, ...],
    detection_rules: tuple[str, ...],
) -> tuple[dict[str, tuple[str, int] | None], bool]:
    evidence_by_rule: dict[str, tuple[str, int] | None] = {}
    any_rule_seen = False

    for interaction in interactions:
        normalized_hits = _normalize_signal_hits(interaction.signal_hits)
        if normalized_hits is None:
            return {}, False
        interaction_id = interaction.interaction_id.strip()

        for rule in detection_rules:
            if rule not in normalized_hits:
                continue
            any_rule_seen = True
            if rule in evidence_by_rule:
                continue
            if interaction.source_line <= 0:
                evidence_by_rule[rule] = None
            else:
                evidence_by_rule[rule] = (interaction_id, interaction.source_line)

    return evidence_by_rule, any_rule_seen


def _compute_confidence(
    *,
    scoring_weights: dict[str, int],
    required_conditions: tuple[str, ...],
    detection_rules: tuple[str, ...],
) -> float | None:
    denominator = sum(scoring_weights.get(rule, 0) for rule in detection_rules)
    numerator = sum(scoring_weights.get(condition, 0) for condition in required_conditions)
    if denominator <= 0 or numerator <= 0:
        return None
    score = round(numerator / denominator, 6)
    if score <= 0.0 or score > 1.0:
        return None
    return score


def _validate_pattern_shape(
    pattern_id: object,
    pattern: object,
) -> tuple[str | None, str | None, tuple[str, ...], tuple[str, ...], dict[str, int]]:
    if not isinstance(pattern_id, str) or not pattern_id.strip():
        return DetectionErrorCode.RULE_EVALUATION_FAILED.value, None, (), (), {}
    if not hasattr(pattern, "pattern_id") or not isinstance(pattern.pattern_id, str):
        return DetectionErrorCode.RULE_EVALUATION_FAILED.value, None, (), (), {}
    if pattern.pattern_id != pattern_id:
        return DetectionErrorCode.RULE_EVALUATION_FAILED.value, None, (), (), {}

    if not hasattr(pattern, "pattern_type") or not isinstance(pattern.pattern_type, str):
        return DetectionErrorCode.RULE_EVALUATION_FAILED.value, None, (), (), {}
    if pattern.pattern_type not in _CANONICAL_PATTERN_TYPES:
        return DetectionErrorCode.UNKNOWN_PATTERN_TYPE.value, None, (), (), {}

    if not hasattr(pattern, "rule_version") or not isinstance(pattern.rule_version, str):
        return DetectionErrorCode.RULE_EVALUATION_FAILED.value, None, (), (), {}
    if pattern.rule_version != PATTERN_REGISTRY_VERSION:
        return DetectionErrorCode.PATTERN_REGISTRY_VERSION_MISMATCH.value, None, (), (), {}

    if not hasattr(pattern, "required_conditions") or not isinstance(pattern.required_conditions, tuple):
        return DetectionErrorCode.RULE_EVALUATION_FAILED.value, None, (), (), {}
    if not hasattr(pattern, "detection_rules") or not isinstance(pattern.detection_rules, tuple):
        return DetectionErrorCode.RULE_EVALUATION_FAILED.value, None, (), (), {}
    if not hasattr(pattern, "scoring_weights") or not isinstance(pattern.scoring_weights, dict):
        return DetectionErrorCode.RULE_EVALUATION_FAILED.value, None, (), (), {}

    required_conditions = tuple(
        item.strip() for item in pattern.required_conditions if isinstance(item, str) and item.strip()
    )
    detection_rules = tuple(
        item.strip() for item in pattern.detection_rules if isinstance(item, str) and item.strip()
    )
    if not required_conditions or not detection_rules:
        return DetectionErrorCode.RULE_EVALUATION_FAILED.value, None, (), (), {}
    if len(required_conditions) != len(set(required_conditions)):
        return DetectionErrorCode.RULE_EVALUATION_FAILED.value, None, (), (), {}
    if len(detection_rules) != len(set(detection_rules)):
        return DetectionErrorCode.RULE_EVALUATION_FAILED.value, None, (), (), {}

    scoring_weights: dict[str, int] = {}
    for raw_key, raw_value in pattern.scoring_weights.items():
        if not isinstance(raw_key, str):
            return DetectionErrorCode.RULE_EVALUATION_FAILED.value, None, (), (), {}
        key = raw_key.strip()
        if not key:
            return DetectionErrorCode.RULE_EVALUATION_FAILED.value, None, (), (), {}
        if not isinstance(raw_value, int) or isinstance(raw_value, bool):
            return DetectionErrorCode.RULE_EVALUATION_FAILED.value, None, (), (), {}
        scoring_weights[key] = raw_value

    if any(condition not in scoring_weights for condition in required_conditions):
        return DetectionErrorCode.RULE_EVALUATION_FAILED.value, None, (), (), {}
    if any(rule not in scoring_weights for rule in detection_rules):
        return DetectionErrorCode.RULE_EVALUATION_FAILED.value, None, (), (), {}

    return None, pattern.pattern_type, required_conditions, detection_rules, scoring_weights


def detect_patterns(
    bundle: InteractionBundle,
    registry: PatternRegistry,
) -> tuple[list[DetectedPattern] | None, list[tuple[str, int]], str | None]:
    """Deterministically detect patterns in an InteractionBundle against a registry.

    Returns (patterns, evidence_refs, None) on success.
    Returns (None, [], error_code) on any failure — fail-closed.

    No side effects. No external calls. Same inputs always produce same outputs.
    """
    structural_valid, structural_error = validate_registry_structure(registry)
    if not structural_valid:
        return None, [], structural_error or ValidationErrorCode.INVALID_REGISTRY_STRUCTURE.value

    registry_error = _validate_registry(registry)
    if registry_error is not None:
        return None, [], registry_error

    bundle_error = _validate_bundle(bundle)
    if bundle_error is not None:
        return None, [], bundle_error

    detected: list[DetectedPattern] = []

    for pattern_id, pattern in sorted(registry.patterns.items(), key=lambda item: str(item[0])):
        (
            pattern_error,
            pattern_type,
            required_conditions,
            detection_rules,
            scoring_weights,
        ) = _validate_pattern_shape(pattern_id, pattern)
        if pattern_error is not None:
            return None, [], pattern_error

        evidence_by_rule, any_rule_seen = _first_rule_evidence(
            interactions=bundle.interactions,
            detection_rules=detection_rules,
        )
        if not any_rule_seen:
            continue

        matched_rules = set(evidence_by_rule)
        if any(rule not in matched_rules for rule in required_conditions):
            continue
        if any(rule not in matched_rules for rule in detection_rules):
            continue
        if any(evidence_by_rule[rule] is None for rule in detection_rules):
            return None, [], DetectionErrorCode.MISSING_EVIDENCE.value

        ordered_evidence = tuple(
            evidence_by_rule[rule] for rule in detection_rules if evidence_by_rule[rule] is not None
        )
        if not ordered_evidence:
            return None, [], DetectionErrorCode.MISSING_EVIDENCE.value

        interaction_ids: list[str] = []
        seen_ids: set[str] = set()
        for interaction_id, source_line in ordered_evidence:
            if not interaction_id or source_line <= 0:
                return None, [], DetectionErrorCode.MISSING_EVIDENCE.value
            if interaction_id in seen_ids:
                continue
            seen_ids.add(interaction_id)
            interaction_ids.append(interaction_id)

        if not interaction_ids:
            return None, [], DetectionErrorCode.MISSING_EVIDENCE.value

        confidence = _compute_confidence(
            scoring_weights=scoring_weights,
            required_conditions=required_conditions,
            detection_rules=detection_rules,
        )
        if confidence is None:
            return None, [], DetectionErrorCode.RULE_EVALUATION_FAILED.value

        detected.append(
            DetectedPattern(
                pattern_id=pattern_id,
                pattern_type=pattern_type or "",
                detection_confidence=confidence,
                evidence_refs=ordered_evidence,
                session_id=bundle.session_id.strip(),
                interaction_ids=tuple(interaction_ids),
                version=PATTERN_REGISTRY_VERSION,
            )
        )

    if not detected:
        return None, [], DetectionErrorCode.PATTERN_NOT_FOUND.value

    ordered = sorted(detected, key=lambda item: (item.pattern_id, item.interaction_ids[0]))

    evidence_refs: list[tuple[str, int]] = []
    seen_refs: set[tuple[str, int]] = set()
    for dp in ordered:
        for ref in dp.evidence_refs:
            if ref in seen_refs:
                continue
            seen_refs.add(ref)
            evidence_refs.append(ref)

    if not evidence_refs:
        return None, [], DetectionErrorCode.MISSING_EVIDENCE.value

    return ordered, evidence_refs, None


__all__ = [
    "Interaction",
    "InteractionBundle",
    "DetectedPattern",
    "detect_patterns",
]
