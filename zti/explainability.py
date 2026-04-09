"""
Zero Trust Intelligence (ZTI) — Reference Protocol Implementation

This module defines deterministic verification and integrity rules for AI systems.
All logic is fail-closed and execution-free.
"""

from __future__ import annotations

from dataclasses import dataclass

from zti.detection import DetectedPattern
from zti.errors import ExplainabilityErrorCode, ValidationErrorCode
from zti.registry import PATTERN_REGISTRY_VERSION, PatternRegistry
from zti.validation import validate_cross_layer_integrity, validate_registry_structure


@dataclass(frozen=True)
class ExplanationArtifact:
    """Auditable explanation for a single detected pattern.

    Produced after cross-layer integrity validation passes. Contains all
    fields needed to reconstruct why a detection occurred.
    """

    pattern_id: str
    pattern_type: str
    explanation_text: str
    contributing_signals: tuple[str, ...]
    evidence_refs: tuple[tuple[str, int], ...]
    session_id: str
    interaction_ids: tuple[str, ...]
    version: str


def _validate_registry(registry: PatternRegistry) -> str | None:
    if not isinstance(registry, PatternRegistry):
        return ExplainabilityErrorCode.REGISTRY_VERSION_MISMATCH.value
    if registry.version != PATTERN_REGISTRY_VERSION:
        return ExplainabilityErrorCode.REGISTRY_VERSION_MISMATCH.value
    if not registry.patterns:
        return ExplainabilityErrorCode.PATTERN_NOT_FOUND.value
    return None


def _interaction_ids_from_evidence(evidence_refs: tuple[tuple[str, int], ...]) -> tuple[str, ...] | None:
    ids: list[str] = []
    seen: set[str] = set()

    for ref in evidence_refs:
        if not isinstance(ref, tuple) or len(ref) != 2:
            return None
        interaction_id, source_line = ref
        if not isinstance(interaction_id, str) or not interaction_id.strip():
            return None
        if not isinstance(source_line, int) or isinstance(source_line, bool) or source_line <= 0:
            return None
        normalized = interaction_id.strip()
        if normalized in seen:
            continue
        seen.add(normalized)
        ids.append(normalized)

    if not ids:
        return None
    return tuple(ids)


def _validate_detected_pattern(detected_pattern: object) -> str | None:
    if not isinstance(detected_pattern, DetectedPattern):
        return ExplainabilityErrorCode.INVALID_DETECTED_PATTERN.value

    if not isinstance(detected_pattern.pattern_id, str) or not detected_pattern.pattern_id.strip():
        return ExplainabilityErrorCode.INVALID_DETECTED_PATTERN.value
    if not isinstance(detected_pattern.pattern_type, str) or not detected_pattern.pattern_type.strip():
        return ExplainabilityErrorCode.INVALID_DETECTED_PATTERN.value

    if not isinstance(detected_pattern.detection_confidence, (int, float)):
        return ExplainabilityErrorCode.INVALID_DETECTED_PATTERN.value
    if isinstance(detected_pattern.detection_confidence, bool):
        return ExplainabilityErrorCode.INVALID_DETECTED_PATTERN.value
    confidence = float(detected_pattern.detection_confidence)
    if confidence <= 0.0 or confidence > 1.0:
        return ExplainabilityErrorCode.INVALID_DETECTED_PATTERN.value

    if not isinstance(detected_pattern.session_id, str) or not detected_pattern.session_id.strip():
        return ExplainabilityErrorCode.INVALID_DETECTED_PATTERN.value

    if not isinstance(detected_pattern.interaction_ids, tuple) or not detected_pattern.interaction_ids:
        return ExplainabilityErrorCode.INVALID_DETECTED_PATTERN.value
    for iid in detected_pattern.interaction_ids:
        if not isinstance(iid, str) or not iid.strip():
            return ExplainabilityErrorCode.INVALID_DETECTED_PATTERN.value

    if not isinstance(detected_pattern.evidence_refs, tuple) or not detected_pattern.evidence_refs:
        return ExplainabilityErrorCode.INVALID_DETECTED_PATTERN.value

    evidence_ids = _interaction_ids_from_evidence(detected_pattern.evidence_refs)
    if evidence_ids is None:
        return ExplainabilityErrorCode.EVIDENCE_MISMATCH.value

    normalized_ids = tuple(iid.strip() for iid in detected_pattern.interaction_ids)
    if evidence_ids != normalized_ids:
        return ExplainabilityErrorCode.EVIDENCE_MISMATCH.value

    if detected_pattern.version != PATTERN_REGISTRY_VERSION:
        return ExplainabilityErrorCode.REGISTRY_VERSION_MISMATCH.value

    return None


def explain_patterns(
    detected_patterns: tuple[DetectedPattern, ...],
    registry: PatternRegistry,
) -> tuple[list[ExplanationArtifact] | None, list[tuple[str, int]], str | None]:
    """Generate auditable explanation artifacts for a set of detected patterns.

    Performs cross-layer integrity validation before generating explanations.
    Returns (artifacts, evidence_refs, None) on success.
    Returns (None, [], error_code) on any failure — fail-closed.

    No side effects. No external calls. Read-only over all inputs.
    """
    structural_valid, structural_error = validate_registry_structure(registry)
    if not structural_valid:
        return None, [], structural_error or ValidationErrorCode.INVALID_REGISTRY_STRUCTURE.value

    registry_error = _validate_registry(registry)
    if registry_error is not None:
        return None, [], registry_error

    if not isinstance(detected_patterns, tuple) or not detected_patterns:
        return None, [], ExplainabilityErrorCode.EMPTY_INPUT.value

    integrity_valid, integrity_error = validate_cross_layer_integrity(detected_patterns, registry)
    if not integrity_valid:
        return None, [], integrity_error or ValidationErrorCode.CROSS_LAYER_INTEGRITY_FAILURE.value

    artifacts: list[ExplanationArtifact] = []

    for detected_pattern in detected_patterns:
        detected_error = _validate_detected_pattern(detected_pattern)
        if detected_error is not None:
            return None, [], detected_error

        pattern_id = detected_pattern.pattern_id.strip()
        registry_pattern = registry.patterns.get(pattern_id)
        if registry_pattern is None:
            return None, [], ExplainabilityErrorCode.PATTERN_NOT_FOUND.value

        if not isinstance(registry_pattern.rule_version, str) or registry_pattern.rule_version != PATTERN_REGISTRY_VERSION:
            return None, [], ExplainabilityErrorCode.REGISTRY_VERSION_MISMATCH.value
        if not isinstance(registry_pattern.pattern_type, str) or not registry_pattern.pattern_type.strip():
            return None, [], ExplainabilityErrorCode.PATTERN_NOT_FOUND.value

        normalized_type = registry_pattern.pattern_type.strip()
        if normalized_type != detected_pattern.pattern_type.strip():
            return None, [], ExplainabilityErrorCode.INVALID_DETECTED_PATTERN.value

        if not isinstance(registry_pattern.detection_rules, tuple) or not registry_pattern.detection_rules:
            return None, [], ExplainabilityErrorCode.PATTERN_NOT_FOUND.value

        contributing_signals: list[str] = []
        for signal in registry_pattern.detection_rules:
            if not isinstance(signal, str) or not signal.strip():
                return None, [], ExplainabilityErrorCode.PATTERN_NOT_FOUND.value
            contributing_signals.append(signal.strip())

        explanation_text = (
            f"Pattern '{pattern_id}' detected due to signals: "
            f"{', '.join(contributing_signals)} "
            f"with evidence at {detected_pattern.interaction_ids}"
        )

        artifacts.append(
            ExplanationArtifact(
                pattern_id=pattern_id,
                pattern_type=normalized_type,
                explanation_text=explanation_text,
                contributing_signals=tuple(contributing_signals),
                evidence_refs=detected_pattern.evidence_refs,
                session_id=detected_pattern.session_id.strip(),
                interaction_ids=tuple(iid.strip() for iid in detected_pattern.interaction_ids),
                version=PATTERN_REGISTRY_VERSION,
            )
        )

    if not artifacts:
        return None, [], ExplainabilityErrorCode.EMPTY_INPUT.value

    ordered = sorted(artifacts, key=lambda item: (item.pattern_id, item.interaction_ids[0]))

    flattened: list[tuple[str, int]] = []
    seen: set[tuple[str, int]] = set()
    for artifact in ordered:
        for ref in artifact.evidence_refs:
            if ref in seen:
                continue
            seen.add(ref)
            flattened.append(ref)

    if not flattened:
        return None, [], ExplainabilityErrorCode.EVIDENCE_MISMATCH.value

    return ordered, flattened, None


__all__ = [
    "ExplanationArtifact",
    "explain_patterns",
]
