"""
Zero Trust Intelligence (ZTI) — Reference Protocol Implementation

This module defines deterministic verification and integrity rules for AI systems.
All logic is fail-closed and execution-free.
"""

from __future__ import annotations

from enum import Enum


class DetectionErrorCode(str, Enum):
    """Error codes returned by the pattern detection engine."""

    PATTERN_NOT_FOUND = "PATTERN_NOT_FOUND"
    PATTERN_REGISTRY_VERSION_MISMATCH = "PATTERN_REGISTRY_VERSION_MISMATCH"
    INVALID_INTERACTION_DATA = "INVALID_INTERACTION_DATA"
    MISSING_EVIDENCE = "MISSING_EVIDENCE"
    UNKNOWN_PATTERN_TYPE = "UNKNOWN_PATTERN_TYPE"
    RULE_EVALUATION_FAILED = "RULE_EVALUATION_FAILED"


class ValidationErrorCode(str, Enum):
    """Error codes returned by the registry and cross-layer validators."""

    INVALID_REGISTRY_STRUCTURE = "INVALID_REGISTRY_STRUCTURE"
    INVALID_PATTERN_DEFINITION = "INVALID_PATTERN_DEFINITION"
    DUPLICATE_DETECTION_RULE = "DUPLICATE_DETECTION_RULE"
    PATTERN_ID_MISMATCH = "PATTERN_ID_MISMATCH"
    CROSS_LAYER_INTEGRITY_FAILURE = "CROSS_LAYER_INTEGRITY_FAILURE"


class ExplainabilityErrorCode(str, Enum):
    """Error codes returned by the explainability engine."""

    REGISTRY_VERSION_MISMATCH = "REGISTRY_VERSION_MISMATCH"
    PATTERN_NOT_FOUND = "PATTERN_NOT_FOUND"
    INVALID_DETECTED_PATTERN = "INVALID_DETECTED_PATTERN"
    EVIDENCE_MISMATCH = "EVIDENCE_MISMATCH"
    EMPTY_INPUT = "EMPTY_INPUT"


class IntegrityErrorCode(str, Enum):
    """Error codes returned by the decision integrity layer."""

    INVALID_RECORD = "INVALID_RECORD"
    INVALID_DECISION_DATA = "INVALID_DECISION_DATA"
    VERSION_MISMATCH = "VERSION_MISMATCH"
    EMPTY_CHAIN = "EMPTY_CHAIN"
    GENESIS_MISMATCH = "GENESIS_MISMATCH"
    CHAIN_BROKEN = "CHAIN_BROKEN"
    TIMESTAMP_REGRESSION = "TIMESTAMP_REGRESSION"
    HASH_MISMATCH = "HASH_MISMATCH"


__all__ = [
    "DetectionErrorCode",
    "ValidationErrorCode",
    "ExplainabilityErrorCode",
    "IntegrityErrorCode",
]
