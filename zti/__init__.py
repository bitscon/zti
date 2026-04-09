"""
Zero Trust Intelligence (ZTI) — Reference Protocol Implementation

Don't trust AI. Verify it.

Architecture: Registry → Detection → Explainability → Validation → Integrity
"""

from zti.registry import (
    DEFAULT_REGISTRY,
    PATTERN_REGISTRY_VERSION,
    InteractionPattern,
    PatternRegistry,
    PatternType,
    validate_pattern_registry,
)
from zti.detection import (
    DetectedPattern,
    Interaction,
    InteractionBundle,
    detect_patterns,
)
from zti.explainability import (
    ExplanationArtifact,
    explain_patterns,
)
from zti.validation import (
    validate_cross_layer_integrity,
    validate_registry_structure,
)
from zti.integrity import (
    GENESIS_HASH,
    INTEGRITY_CHAIN_VERSION,
    DecisionRecord,
    create_decision_record,
    recompute_decision_hash,
    validate_chain,
)
from zti.errors import (
    DetectionErrorCode,
    ExplainabilityErrorCode,
    IntegrityErrorCode,
    ValidationErrorCode,
)

__version__ = "1.0.0"

__all__ = [
    # Registry
    "DEFAULT_REGISTRY",
    "PATTERN_REGISTRY_VERSION",
    "InteractionPattern",
    "PatternRegistry",
    "PatternType",
    "validate_pattern_registry",
    # Detection
    "DetectedPattern",
    "Interaction",
    "InteractionBundle",
    "detect_patterns",
    # Explainability
    "ExplanationArtifact",
    "explain_patterns",
    # Validation
    "validate_cross_layer_integrity",
    "validate_registry_structure",
    # Integrity
    "GENESIS_HASH",
    "INTEGRITY_CHAIN_VERSION",
    "DecisionRecord",
    "create_decision_record",
    "recompute_decision_hash",
    "validate_chain",
    # Errors
    "DetectionErrorCode",
    "ExplainabilityErrorCode",
    "IntegrityErrorCode",
    "ValidationErrorCode",
]
