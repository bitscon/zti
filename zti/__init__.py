"""
Zero Trust Intelligence (ZTI) — Reference Protocol Implementation

Author: Chad McCormack
© 2026 Chad McCormack

Don't trust AI. Verify it.

Architecture: Registry → Detection → Explainability → Validation → Integrity → Lineage
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
from zti.lineage import (
    LINEAGE_CONTRACT_VERSION,
    APPROVAL_ACTION_APPROVE,
    APPROVAL_ACTION_REJECT,
    LINEAGE_APPROVAL_ACTIONS,
    ApprovalLineageEntry,
    create_lineage_entry,
    validate_lineage,
    recompute_entry_hash,
)
from zti.errors import (
    DetectionErrorCode,
    ExplainabilityErrorCode,
    IntegrityErrorCode,
    LineageErrorCode,
    ValidationErrorCode,
)

__version__ = "1.0.0"
__author__ = "Chad McCormack"

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
    # Lineage
    "LINEAGE_CONTRACT_VERSION",
    "APPROVAL_ACTION_APPROVE",
    "APPROVAL_ACTION_REJECT",
    "LINEAGE_APPROVAL_ACTIONS",
    "ApprovalLineageEntry",
    "create_lineage_entry",
    "validate_lineage",
    "recompute_entry_hash",
    # Errors
    "DetectionErrorCode",
    "ExplainabilityErrorCode",
    "IntegrityErrorCode",
    "LineageErrorCode",
    "ValidationErrorCode",
]
