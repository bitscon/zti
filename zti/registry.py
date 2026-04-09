"""
Zero Trust Intelligence (ZTI) — Pattern Registry

Author: Chad McCormack
© 2026 Chad McCormack

Deterministic, fail-closed verification and integrity model for AI systems.
This module contains no execution logic and serves as a validation layer only.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping

PATTERN_REGISTRY_VERSION = "1.0.0"

PATTERN_SCHEMA_INVALID = "PATTERN_SCHEMA_INVALID"
PATTERN_REGISTRY_INVALID = "PATTERN_REGISTRY_INVALID"


class PatternType(str, Enum):
    """Closed canonical interaction pattern types.

    This set is fixed. Unknown pattern types are rejected at construction.
    """

    EXPLORATORY = "exploratory"
    DIRECTIVE = "directive"
    STALLED = "stalled"
    ITERATIVE = "iterative"
    CONFLICTING = "conflicting"


_CANONICAL_PATTERN_TYPES: frozenset[str] = frozenset(item.value for item in PatternType)


@dataclass(frozen=True)
class InteractionPattern:
    """A single verified pattern definition in the registry.

    Immutable. Self-validating at construction. Any schema violation raises
    ValueError(PATTERN_SCHEMA_INVALID) — construction either fully succeeds
    or fails closed.
    """

    pattern_id: str
    pattern_type: str
    rule_version: str
    description: str
    required_signals: tuple[str, ...]
    scoring_weights: dict[str, int]
    required_conditions: tuple[str, ...] = ()
    detection_rules: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        normalized_pattern_id = self.pattern_id.strip() if isinstance(self.pattern_id, str) else ""
        normalized_pattern_type = self.pattern_type.strip() if isinstance(self.pattern_type, str) else ""
        normalized_rule_version = self.rule_version.strip() if isinstance(self.rule_version, str) else ""
        normalized_description = self.description.strip() if isinstance(self.description, str) else ""

        if not normalized_pattern_id:
            raise ValueError(PATTERN_SCHEMA_INVALID)
        if normalized_pattern_type not in _CANONICAL_PATTERN_TYPES:
            raise ValueError(PATTERN_SCHEMA_INVALID)
        if normalized_rule_version != PATTERN_REGISTRY_VERSION:
            raise ValueError(PATTERN_SCHEMA_INVALID)
        if not normalized_description:
            raise ValueError(PATTERN_SCHEMA_INVALID)
        if not isinstance(self.required_signals, tuple) or not self.required_signals:
            raise ValueError(PATTERN_SCHEMA_INVALID)
        if not isinstance(self.scoring_weights, dict) or not self.scoring_weights:
            raise ValueError(PATTERN_SCHEMA_INVALID)

        normalized_signals: list[str] = []
        seen_signals: set[str] = set()
        for signal in self.required_signals:
            normalized_signal = signal.strip() if isinstance(signal, str) else ""
            if not normalized_signal or normalized_signal in seen_signals:
                raise ValueError(PATTERN_SCHEMA_INVALID)
            seen_signals.add(normalized_signal)
            normalized_signals.append(normalized_signal)

        normalized_weights: dict[str, int] = {}
        for key, value in self.scoring_weights.items():
            normalized_key = key.strip() if isinstance(key, str) else ""
            if not normalized_key:
                raise ValueError(PATTERN_SCHEMA_INVALID)
            if not isinstance(value, int) or isinstance(value, bool):
                raise ValueError(PATTERN_SCHEMA_INVALID)
            normalized_weights[normalized_key] = value

        if set(normalized_weights) != set(normalized_signals):
            raise ValueError(PATTERN_SCHEMA_INVALID)

        if self.required_conditions:
            normalized_required_conditions = tuple(
                signal.strip() for signal in self.required_conditions if isinstance(signal, str) and signal.strip()
            )
        else:
            normalized_required_conditions = tuple(normalized_signals)
        if not normalized_required_conditions:
            raise ValueError(PATTERN_SCHEMA_INVALID)
        if len(set(normalized_required_conditions)) != len(normalized_required_conditions):
            raise ValueError(PATTERN_SCHEMA_INVALID)
        if any(signal not in normalized_signals for signal in normalized_required_conditions):
            raise ValueError(PATTERN_SCHEMA_INVALID)

        if self.detection_rules:
            normalized_detection_rules = tuple(
                signal.strip() for signal in self.detection_rules if isinstance(signal, str) and signal.strip()
            )
        else:
            normalized_detection_rules = tuple(normalized_signals)
        if not normalized_detection_rules:
            raise ValueError(PATTERN_SCHEMA_INVALID)
        if len(set(normalized_detection_rules)) != len(normalized_detection_rules):
            raise ValueError(PATTERN_SCHEMA_INVALID)
        if any(signal not in normalized_signals for signal in normalized_detection_rules):
            raise ValueError(PATTERN_SCHEMA_INVALID)

        ordered_weights = {signal: normalized_weights[signal] for signal in normalized_signals}

        object.__setattr__(self, "pattern_id", normalized_pattern_id)
        object.__setattr__(self, "pattern_type", normalized_pattern_type)
        object.__setattr__(self, "rule_version", normalized_rule_version)
        object.__setattr__(self, "description", normalized_description)
        object.__setattr__(self, "required_signals", tuple(normalized_signals))
        object.__setattr__(self, "scoring_weights", ordered_weights)
        object.__setattr__(self, "required_conditions", normalized_required_conditions)
        object.__setattr__(self, "detection_rules", normalized_detection_rules)


@dataclass(frozen=True)
class PatternRegistry:
    """A versioned, closed registry of verified interaction patterns.

    Immutable at runtime. Self-validating at construction. The single source
    of truth for all detection and verification operations.
    """

    version: str
    patterns: Mapping[str, InteractionPattern]

    def __post_init__(self) -> None:
        normalized_version = self.version.strip() if isinstance(self.version, str) else ""
        if normalized_version != PATTERN_REGISTRY_VERSION:
            raise ValueError(PATTERN_SCHEMA_INVALID)
        if not isinstance(self.patterns, Mapping) or not self.patterns:
            raise ValueError(PATTERN_SCHEMA_INVALID)
        valid, reason = validate_pattern_registry(self.patterns)
        if not valid:
            raise ValueError(reason or PATTERN_SCHEMA_INVALID)

        ordered_patterns = dict(sorted(self.patterns.items(), key=lambda item: str(item[0])))
        object.__setattr__(self, "version", normalized_version)
        object.__setattr__(self, "patterns", ordered_patterns)


def validate_pattern_registry(
    registry: Mapping[str, InteractionPattern] | None = None,
) -> tuple[bool, str]:
    """Validate the structural integrity of a pattern registry mapping.

    Accepts either a raw mapping or None (validates the built-in default registry).
    Returns (True, "") on success.
    Returns (False, error_code) on any violation — fail-closed.
    """
    candidate = registry if registry is not None else PATTERN_REGISTRY
    if not isinstance(candidate, Mapping) or not candidate:
        return False, PATTERN_REGISTRY_INVALID

    seen_pattern_ids: set[str] = set()

    for map_key, pattern in sorted(candidate.items(), key=lambda item: str(item[0])):
        if not isinstance(map_key, str) or not map_key.strip():
            return False, PATTERN_REGISTRY_INVALID
        if not isinstance(pattern, InteractionPattern):
            return False, PATTERN_REGISTRY_INVALID

        if pattern.pattern_id in seen_pattern_ids:
            return False, PATTERN_REGISTRY_INVALID
        seen_pattern_ids.add(pattern.pattern_id)

        if map_key.strip() != pattern.pattern_id:
            return False, PATTERN_REGISTRY_INVALID
        if pattern.pattern_type not in _CANONICAL_PATTERN_TYPES:
            return False, PATTERN_REGISTRY_INVALID
        if pattern.rule_version != PATTERN_REGISTRY_VERSION:
            return False, PATTERN_REGISTRY_INVALID
        if not pattern.required_signals:
            return False, PATTERN_REGISTRY_INVALID
        if not pattern.required_conditions:
            return False, PATTERN_REGISTRY_INVALID
        if not pattern.detection_rules:
            return False, PATTERN_REGISTRY_INVALID
        if any(signal not in pattern.required_signals for signal in pattern.required_conditions):
            return False, PATTERN_REGISTRY_INVALID
        if any(signal not in pattern.required_signals for signal in pattern.detection_rules):
            return False, PATTERN_REGISTRY_INVALID
        if set(pattern.scoring_weights) != set(pattern.required_signals):
            return False, PATTERN_REGISTRY_INVALID
        if any(
            (not isinstance(weight, int) or isinstance(weight, bool))
            for weight in pattern.scoring_weights.values()
        ):
            return False, PATTERN_REGISTRY_INVALID

    return True, ""


# Built-in reference pattern registry.
PATTERN_REGISTRY: dict[str, InteractionPattern] = {
    "exploratory": InteractionPattern(
        pattern_id="exploratory",
        pattern_type=PatternType.EXPLORATORY.value,
        rule_version=PATTERN_REGISTRY_VERSION,
        description="Open-ended exploration with option-seeking and scope discovery signals.",
        required_signals=(
            "open_question_density",
            "option_space_expansion",
            "hypothesis_generation",
        ),
        scoring_weights={
            "open_question_density": 4,
            "option_space_expansion": 3,
            "hypothesis_generation": 2,
        },
        required_conditions=(
            "open_question_density",
            "option_space_expansion",
        ),
        detection_rules=(
            "open_question_density",
            "option_space_expansion",
            "hypothesis_generation",
        ),
    ),
    "directive": InteractionPattern(
        pattern_id="directive",
        pattern_type=PatternType.DIRECTIVE.value,
        rule_version=PATTERN_REGISTRY_VERSION,
        description="Instruction-forward requests with explicit constraints and concrete action intent.",
        required_signals=(
            "imperative_command_density",
            "constraint_specificity",
            "single_path_instruction",
        ),
        scoring_weights={
            "imperative_command_density": 4,
            "constraint_specificity": 3,
            "single_path_instruction": 2,
        },
        required_conditions=(
            "imperative_command_density",
            "constraint_specificity",
        ),
        detection_rules=(
            "imperative_command_density",
            "constraint_specificity",
            "single_path_instruction",
        ),
    ),
    "stalled": InteractionPattern(
        pattern_id="stalled",
        pattern_type=PatternType.STALLED.value,
        rule_version=PATTERN_REGISTRY_VERSION,
        description="Progress stalls marked by repeated blockers and unresolved looped attempts.",
        required_signals=(
            "blocker_repetition",
            "retry_without_progress",
            "stagnation_language",
        ),
        scoring_weights={
            "blocker_repetition": 4,
            "retry_without_progress": 3,
            "stagnation_language": 2,
        },
        required_conditions=(
            "blocker_repetition",
            "retry_without_progress",
        ),
        detection_rules=(
            "blocker_repetition",
            "retry_without_progress",
            "stagnation_language",
        ),
    ),
    "iterative": InteractionPattern(
        pattern_id="iterative",
        pattern_type=PatternType.ITERATIVE.value,
        rule_version=PATTERN_REGISTRY_VERSION,
        description="Incremental refinement with explicit revision cycles and feedback incorporation.",
        required_signals=(
            "revision_marker_density",
            "feedback_incorporation",
            "delta_change_tracking",
        ),
        scoring_weights={
            "revision_marker_density": 4,
            "feedback_incorporation": 3,
            "delta_change_tracking": 2,
        },
        required_conditions=(
            "revision_marker_density",
            "feedback_incorporation",
        ),
        detection_rules=(
            "revision_marker_density",
            "feedback_incorporation",
            "delta_change_tracking",
        ),
    ),
    "conflicting": InteractionPattern(
        pattern_id="conflicting",
        pattern_type=PatternType.CONFLICTING.value,
        rule_version=PATTERN_REGISTRY_VERSION,
        description="Conflicting constraints or goals that cannot all be satisfied simultaneously.",
        required_signals=(
            "constraint_collision",
            "goal_incompatibility",
            "instruction_contradiction",
        ),
        scoring_weights={
            "constraint_collision": 4,
            "goal_incompatibility": 3,
            "instruction_contradiction": 2,
        },
        required_conditions=(
            "constraint_collision",
            "goal_incompatibility",
        ),
        detection_rules=(
            "constraint_collision",
            "goal_incompatibility",
            "instruction_contradiction",
        ),
    ),
}

_REGISTRY_VALID, _REGISTRY_REASON = validate_pattern_registry(PATTERN_REGISTRY)
if not _REGISTRY_VALID:
    raise RuntimeError(_REGISTRY_REASON or PATTERN_REGISTRY_INVALID)

DEFAULT_REGISTRY = PatternRegistry(
    version=PATTERN_REGISTRY_VERSION,
    patterns=PATTERN_REGISTRY,
)


__all__ = [
    "PATTERN_REGISTRY_VERSION",
    "PATTERN_SCHEMA_INVALID",
    "PATTERN_REGISTRY_INVALID",
    "PatternType",
    "InteractionPattern",
    "PatternRegistry",
    "PATTERN_REGISTRY",
    "DEFAULT_REGISTRY",
    "validate_pattern_registry",
]
