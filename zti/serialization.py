"""
Zero Trust Intelligence (ZTI) — Canonical Serialization

Author: Chad McCormack
© 2026 Chad McCormack

Deterministic, fail-closed verification and integrity model for AI systems.
This module contains no execution logic and serves as a validation layer only.
"""

from __future__ import annotations

_SEPARATOR = "|"


def serialize_explanation_artifact(artifact: object) -> bytes | None:
    """Deterministic canonical serialization of an ExplanationArtifact.

    Fields are joined in a fixed order with a pipe separator. Tuple fields are
    sorted to guarantee byte-for-byte identity for any valid artifact with the
    same logical content. This output is suitable as decision_data for
    create_decision_record.

    Returns None if artifact lacks required fields.
    """
    try:
        signals = _SEPARATOR.join(sorted(artifact.contributing_signals))  # type: ignore[union-attr]
        interactions = _SEPARATOR.join(sorted(artifact.interaction_ids))  # type: ignore[union-attr]
        evidence = _SEPARATOR.join(
            f"{iid}:{line}"
            for iid, line in sorted(artifact.evidence_refs, key=lambda e: (e[0], e[1]))  # type: ignore[union-attr]
        )
        payload = _SEPARATOR.join([
            artifact.version,  # type: ignore[union-attr]
            artifact.session_id,  # type: ignore[union-attr]
            artifact.pattern_id,  # type: ignore[union-attr]
            artifact.pattern_type,  # type: ignore[union-attr]
            signals,
            interactions,
            evidence,
        ])
        return payload.encode("utf-8")
    except (AttributeError, TypeError):
        return None


def serialize_detected_pattern(pattern: object) -> bytes | None:
    """Deterministic canonical serialization of a DetectedPattern.

    Suitable as decision_data for create_decision_record.
    Returns None if pattern lacks required fields.
    """
    try:
        interactions = _SEPARATOR.join(sorted(pattern.interaction_ids))  # type: ignore[union-attr]
        evidence = _SEPARATOR.join(
            f"{iid}:{line}"
            for iid, line in sorted(pattern.evidence_refs, key=lambda e: (e[0], e[1]))  # type: ignore[union-attr]
        )
        payload = _SEPARATOR.join([
            pattern.version,  # type: ignore[union-attr]
            pattern.session_id,  # type: ignore[union-attr]
            pattern.pattern_id,  # type: ignore[union-attr]
            pattern.pattern_type,  # type: ignore[union-attr]
            str(round(pattern.detection_confidence, 6)),  # type: ignore[union-attr]
            interactions,
            evidence,
        ])
        return payload.encode("utf-8")
    except (AttributeError, TypeError):
        return None


__all__ = [
    "serialize_explanation_artifact",
    "serialize_detected_pattern",
]
