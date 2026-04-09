"""
Zero Trust Intelligence (ZTI) — Cross-Layer Validation

Author: Chad McCormack
© 2026 Chad McCormack

Deterministic, fail-closed verification and integrity model for AI systems.
This module contains no execution logic and serves as a validation layer only.
"""

from __future__ import annotations

from collections.abc import Mapping

from zti.errors import ValidationErrorCode
from zti.registry import (
    PATTERN_REGISTRY_VERSION,
    PatternRegistry,
)


def validate_registry_structure(registry: PatternRegistry) -> tuple[bool, str | None]:
    """Structural validator for a PatternRegistry instance.

    Validates the registry container and each pattern definition.
    Returns (True, None) on success.
    Returns (False, error_code) on any violation — fail-closed.

    Checks:
    - registry must be a PatternRegistry instance
    - registry.version must equal PATTERN_REGISTRY_VERSION
    - registry.patterns must be a non-empty Mapping
    - For each (key, pattern) pair:
        - key must be a non-empty str
        - pattern_id must be non-empty str, key must equal pattern_id
        - pattern_type must be non-empty str
        - rule_version must equal PATTERN_REGISTRY_VERSION
        - detection_rules must be a non-empty tuple of non-empty, unique strings
    """
    if not isinstance(registry, PatternRegistry):
        return False, ValidationErrorCode.INVALID_REGISTRY_STRUCTURE.value

    if not isinstance(registry.version, str) or registry.version != PATTERN_REGISTRY_VERSION:
        return False, ValidationErrorCode.INVALID_REGISTRY_STRUCTURE.value

    if not isinstance(registry.patterns, Mapping) or not registry.patterns:
        return False, ValidationErrorCode.INVALID_REGISTRY_STRUCTURE.value

    for map_key, pattern in registry.patterns.items():
        if not isinstance(map_key, str) or not map_key.strip():
            return False, ValidationErrorCode.INVALID_REGISTRY_STRUCTURE.value

        if not hasattr(pattern, "pattern_id"):
            return False, ValidationErrorCode.INVALID_PATTERN_DEFINITION.value
        if not isinstance(pattern.pattern_id, str) or not pattern.pattern_id.strip():
            return False, ValidationErrorCode.INVALID_PATTERN_DEFINITION.value

        if map_key.strip() != pattern.pattern_id:
            return False, ValidationErrorCode.PATTERN_ID_MISMATCH.value

        if not hasattr(pattern, "pattern_type"):
            return False, ValidationErrorCode.INVALID_PATTERN_DEFINITION.value
        if not isinstance(pattern.pattern_type, str) or not pattern.pattern_type.strip():
            return False, ValidationErrorCode.INVALID_PATTERN_DEFINITION.value

        if not hasattr(pattern, "rule_version"):
            return False, ValidationErrorCode.INVALID_PATTERN_DEFINITION.value
        if pattern.rule_version != PATTERN_REGISTRY_VERSION:
            return False, ValidationErrorCode.INVALID_PATTERN_DEFINITION.value

        if not hasattr(pattern, "detection_rules"):
            return False, ValidationErrorCode.INVALID_PATTERN_DEFINITION.value
        if not isinstance(pattern.detection_rules, tuple) or not pattern.detection_rules:
            return False, ValidationErrorCode.INVALID_PATTERN_DEFINITION.value

        seen_rules: set[str] = set()
        for rule in pattern.detection_rules:
            if not isinstance(rule, str) or not rule.strip():
                return False, ValidationErrorCode.INVALID_PATTERN_DEFINITION.value
            normalized_rule = rule.strip()
            if normalized_rule in seen_rules:
                return False, ValidationErrorCode.DUPLICATE_DETECTION_RULE.value
            seen_rules.add(normalized_rule)

    return True, None


def validate_cross_layer_integrity(
    detected_patterns: tuple,
    registry: PatternRegistry,
) -> tuple[bool, str | None]:
    """Cross-layer integrity validator.

    Validates that every detected pattern is consistent with the registry
    it was produced from. Read-only — no mutation of any input.

    Returns (True, None) on success.
    Returns (False, error_code) on any violation — fail-closed.

    Invariants per detected pattern:
    1. pattern_id exists in registry
    2. pattern_type matches registry entry
    3. version matches PATTERN_REGISTRY_VERSION
    4. registry entry has non-empty detection_rules
    5. evidence_refs and interaction_ids are bijectively consistent
    """
    if not isinstance(detected_patterns, tuple) or not detected_patterns:
        return False, ValidationErrorCode.CROSS_LAYER_INTEGRITY_FAILURE.value

    if not isinstance(registry, PatternRegistry):
        return False, ValidationErrorCode.INVALID_REGISTRY_STRUCTURE.value

    for detected_pattern in detected_patterns:
        pattern_id = getattr(detected_pattern, "pattern_id", None)
        if not isinstance(pattern_id, str) or not pattern_id.strip():
            return False, ValidationErrorCode.CROSS_LAYER_INTEGRITY_FAILURE.value

        registry_entry = registry.patterns.get(pattern_id.strip())
        if registry_entry is None:
            return False, ValidationErrorCode.CROSS_LAYER_INTEGRITY_FAILURE.value

        detected_type = getattr(detected_pattern, "pattern_type", None)
        if not isinstance(detected_type, str) or not detected_type.strip():
            return False, ValidationErrorCode.CROSS_LAYER_INTEGRITY_FAILURE.value
        if not isinstance(registry_entry.pattern_type, str):
            return False, ValidationErrorCode.CROSS_LAYER_INTEGRITY_FAILURE.value
        if detected_type.strip() != registry_entry.pattern_type.strip():
            return False, ValidationErrorCode.CROSS_LAYER_INTEGRITY_FAILURE.value

        detected_version = getattr(detected_pattern, "version", None)
        if detected_version != PATTERN_REGISTRY_VERSION:
            return False, ValidationErrorCode.CROSS_LAYER_INTEGRITY_FAILURE.value

        if not isinstance(registry_entry.detection_rules, tuple) or not registry_entry.detection_rules:
            return False, ValidationErrorCode.CROSS_LAYER_INTEGRITY_FAILURE.value

        evidence_refs = getattr(detected_pattern, "evidence_refs", None)
        interaction_ids = getattr(detected_pattern, "interaction_ids", None)
        if not isinstance(evidence_refs, tuple) or not evidence_refs:
            return False, ValidationErrorCode.CROSS_LAYER_INTEGRITY_FAILURE.value
        if not isinstance(interaction_ids, tuple) or not interaction_ids:
            return False, ValidationErrorCode.CROSS_LAYER_INTEGRITY_FAILURE.value

        derived = _derive_interaction_ids(evidence_refs)
        if derived is None:
            return False, ValidationErrorCode.CROSS_LAYER_INTEGRITY_FAILURE.value

        normalized_ids = tuple(
            iid.strip()
            for iid in interaction_ids
            if isinstance(iid, str) and iid.strip()
        )
        if derived != normalized_ids:
            return False, ValidationErrorCode.CROSS_LAYER_INTEGRITY_FAILURE.value

    return True, None


def _derive_interaction_ids(
    evidence_refs: tuple[tuple[str, int], ...],
) -> tuple[str, ...] | None:
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


__all__ = [
    "validate_registry_structure",
    "validate_cross_layer_integrity",
]
