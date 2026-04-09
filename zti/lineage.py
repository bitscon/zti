"""
Zero Trust Intelligence (ZTI) — Approval Lineage Contract

Author: Chad McCormack
© 2026 Chad McCormack

Deterministic, fail-closed verification and integrity model for AI systems.
This module contains no execution logic and serves as a validation layer only.

The lineage layer records who approved or rejected each verified AI decision,
when, and in what order. Each entry is cryptographically bound to its content.
The sequence is validated for monotonic timestamps and hash integrity.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

LINEAGE_CONTRACT_VERSION = "1.0.0"

APPROVAL_ACTION_APPROVE = "approve"
APPROVAL_ACTION_REJECT = "reject"

LINEAGE_APPROVAL_ACTIONS = (APPROVAL_ACTION_APPROVE, APPROVAL_ACTION_REJECT)

# ---------------------------------------------------------------------------
# Error codes
# ---------------------------------------------------------------------------

LINEAGE_INVALID_ENTRY = "LINEAGE_INVALID_ENTRY"
LINEAGE_INVALID_ACTION = "LINEAGE_INVALID_ACTION"
LINEAGE_VERSION_MISMATCH = "LINEAGE_VERSION_MISMATCH"
LINEAGE_EMPTY = "LINEAGE_EMPTY"
LINEAGE_TIMESTAMP_REGRESSION = "LINEAGE_TIMESTAMP_REGRESSION"
LINEAGE_HASH_MISMATCH = "LINEAGE_HASH_MISMATCH"

_FIELD_SEPARATOR = "|"


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ApprovalLineageEntry:
    """A single approval event bound to a verified decision.

    Immutable. Each entry cryptographically binds an approval action to a
    specific decision record, approver identity, and timestamp. Any tampering
    is detectable by validate_lineage.

    Fields
    ------
    entry_id            : Caller-supplied unique identifier for this approval event.
    decision_record_id  : Identifier of the DecisionRecord this approval covers.
    approver_id         : Principal who performed the approval action.
    approval_action     : One of LINEAGE_APPROVAL_ACTIONS — "approve" or "reject".
    timestamp_ns        : UTC nanoseconds at the time of the approval event.
    version             : LINEAGE_CONTRACT_VERSION at the time of creation.
    entry_hash          : SHA-256 hex digest binding all fields for tamper detection.
    """

    entry_id: str
    decision_record_id: str
    approver_id: str
    approval_action: str
    timestamp_ns: int
    version: str
    entry_hash: str


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _compute_entry_hash(
    *,
    entry_id: str,
    decision_record_id: str,
    approver_id: str,
    approval_action: str,
    timestamp_ns: int,
    version: str,
) -> str:
    """Deterministically bind all entry fields into a single tamper-evident hash.

    Field order is fixed. The separator prevents field-boundary ambiguity.
    """
    payload = _FIELD_SEPARATOR.join([
        version,
        entry_id,
        decision_record_id,
        approver_id,
        approval_action,
        str(timestamp_ns),
    ]).encode("utf-8")
    return _sha256_hex(payload)


def _is_valid_hex_digest(value: object) -> bool:
    if not isinstance(value, str) or len(value) != 64:
        return False
    try:
        int(value, 16)
        return True
    except ValueError:
        return False


def _validate_entry_fields(entry: object) -> str | None:
    if not isinstance(entry, ApprovalLineageEntry):
        return LINEAGE_INVALID_ENTRY
    if not isinstance(entry.entry_id, str) or not entry.entry_id.strip():
        return LINEAGE_INVALID_ENTRY
    if not isinstance(entry.decision_record_id, str) or not entry.decision_record_id.strip():
        return LINEAGE_INVALID_ENTRY
    if not isinstance(entry.approver_id, str) or not entry.approver_id.strip():
        return LINEAGE_INVALID_ENTRY
    if entry.approval_action not in LINEAGE_APPROVAL_ACTIONS:
        return LINEAGE_INVALID_ACTION
    if not isinstance(entry.timestamp_ns, int) or isinstance(entry.timestamp_ns, bool):
        return LINEAGE_INVALID_ENTRY
    if entry.timestamp_ns <= 0:
        return LINEAGE_INVALID_ENTRY
    if not isinstance(entry.version, str) or entry.version != LINEAGE_CONTRACT_VERSION:
        return LINEAGE_VERSION_MISMATCH
    if not _is_valid_hex_digest(entry.entry_hash):
        return LINEAGE_INVALID_ENTRY
    return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def create_lineage_entry(
    *,
    entry_id: str,
    decision_record_id: str,
    approver_id: str,
    approval_action: str,
    timestamp_ns: int,
) -> tuple[ApprovalLineageEntry | None, str | None]:
    """Create a new ApprovalLineageEntry binding an approval event to a decision.

    This function is stateless. Callers are responsible for maintaining the
    sequence and passing entries to validate_lineage.

    Parameters
    ----------
    entry_id            : Unique identifier for this approval event. Must be non-empty.
    decision_record_id  : ID of the DecisionRecord this approval covers. Must be non-empty.
    approver_id         : Principal performing the action. Must be non-empty.
    approval_action     : Must be one of LINEAGE_APPROVAL_ACTIONS.
    timestamp_ns        : UTC nanoseconds. Must be a positive integer.

    Returns
    -------
    (ApprovalLineageEntry, None)   on success.
    (None, error_code)             on any validation failure — fail-closed.
    """
    if not isinstance(entry_id, str) or not entry_id.strip():
        return None, LINEAGE_INVALID_ENTRY
    if not isinstance(decision_record_id, str) or not decision_record_id.strip():
        return None, LINEAGE_INVALID_ENTRY
    if not isinstance(approver_id, str) or not approver_id.strip():
        return None, LINEAGE_INVALID_ENTRY
    if approval_action not in LINEAGE_APPROVAL_ACTIONS:
        return None, LINEAGE_INVALID_ACTION
    if not isinstance(timestamp_ns, int) or isinstance(timestamp_ns, bool):
        return None, LINEAGE_INVALID_ENTRY
    if timestamp_ns <= 0:
        return None, LINEAGE_INVALID_ENTRY

    normalized_entry_id = entry_id.strip()
    normalized_decision_record_id = decision_record_id.strip()
    normalized_approver_id = approver_id.strip()

    entry_hash = _compute_entry_hash(
        entry_id=normalized_entry_id,
        decision_record_id=normalized_decision_record_id,
        approver_id=normalized_approver_id,
        approval_action=approval_action,
        timestamp_ns=timestamp_ns,
        version=LINEAGE_CONTRACT_VERSION,
    )

    return ApprovalLineageEntry(
        entry_id=normalized_entry_id,
        decision_record_id=normalized_decision_record_id,
        approver_id=normalized_approver_id,
        approval_action=approval_action,
        timestamp_ns=timestamp_ns,
        version=LINEAGE_CONTRACT_VERSION,
        entry_hash=entry_hash,
    ), None


def validate_lineage(
    entries: tuple[ApprovalLineageEntry, ...] | list[ApprovalLineageEntry],
) -> tuple[bool, str | None]:
    """Validate a sequence of approval lineage entries.

    Stateless. Any sequence of ApprovalLineageEntries can be validated
    independently at any time.

    Checks performed in order (fail-closed — stops at first violation):
    1. Sequence is non-empty.
    2. Every entry passes field-level validation.
    3. Timestamps are strictly monotonically increasing across the sequence.
    4. Each entry's entry_hash can be independently recomputed and matches.

    Returns (True, None) on success.
    Returns (False, error_code) on any violation.
    """
    if not isinstance(entries, (tuple, list)) or not entries:
        return False, LINEAGE_EMPTY

    for entry in entries:
        field_error = _validate_entry_fields(entry)
        if field_error is not None:
            return False, field_error

    for index, entry in enumerate(entries):
        if index > 0:
            prior = entries[index - 1]
            if entry.timestamp_ns <= prior.timestamp_ns:
                return False, LINEAGE_TIMESTAMP_REGRESSION

        expected = _compute_entry_hash(
            entry_id=entry.entry_id,
            decision_record_id=entry.decision_record_id,
            approver_id=entry.approver_id,
            approval_action=entry.approval_action,
            timestamp_ns=entry.timestamp_ns,
            version=entry.version,
        )
        if entry.entry_hash != expected:
            return False, LINEAGE_HASH_MISMATCH

    return True, None


def recompute_entry_hash(
    *,
    entry_id: str,
    decision_record_id: str,
    approver_id: str,
    approval_action: str,
    timestamp_ns: int,
    version: str = LINEAGE_CONTRACT_VERSION,
) -> str | None:
    """Recompute the entry_hash for the given fields.

    Use to verify that a stored entry still matches its original data.
    Returns None if any field is invalid.
    """
    if not isinstance(entry_id, str) or not entry_id.strip():
        return None
    if not isinstance(decision_record_id, str) or not decision_record_id.strip():
        return None
    if not isinstance(approver_id, str) or not approver_id.strip():
        return None
    if approval_action not in LINEAGE_APPROVAL_ACTIONS:
        return None
    if not isinstance(timestamp_ns, int) or isinstance(timestamp_ns, bool) or timestamp_ns <= 0:
        return None
    if not isinstance(version, str) or not version.strip():
        return None

    return _compute_entry_hash(
        entry_id=entry_id.strip(),
        decision_record_id=decision_record_id.strip(),
        approver_id=approver_id.strip(),
        approval_action=approval_action,
        timestamp_ns=timestamp_ns,
        version=version,
    )


__all__ = [
    "LINEAGE_CONTRACT_VERSION",
    "APPROVAL_ACTION_APPROVE",
    "APPROVAL_ACTION_REJECT",
    "LINEAGE_APPROVAL_ACTIONS",
    "LINEAGE_INVALID_ENTRY",
    "LINEAGE_INVALID_ACTION",
    "LINEAGE_VERSION_MISMATCH",
    "LINEAGE_EMPTY",
    "LINEAGE_TIMESTAMP_REGRESSION",
    "LINEAGE_HASH_MISMATCH",
    "ApprovalLineageEntry",
    "create_lineage_entry",
    "validate_lineage",
    "recompute_entry_hash",
]
