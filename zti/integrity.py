"""
Zero Trust Intelligence (ZTI) — Decision Integrity Chain

Author: Chad McCormack
© 2026 Chad McCormack

Deterministic, fail-closed verification and integrity model for AI systems.
This module contains no execution logic and serves as a validation layer only.
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass

from zti.errors import IntegrityErrorCode

INTEGRITY_CHAIN_VERSION = "1.0.0"

# Sentinel previous_hash for the genesis (first) record in a chain.
GENESIS_HASH: str = "0" * 64

_FIELD_SEPARATOR = "|"


@dataclass(frozen=True)
class DecisionRecord:
    """A single entry in the ZTI decision integrity chain.

    Immutable. Each record cryptographically binds a decision payload to its
    position in the chain. Any tampering is detectable by validate_chain.

    Fields
    ------
    record_id       : Caller-supplied unique identifier for this decision.
    timestamp_ns    : Wall-clock time at record creation, UTC nanoseconds.
                      Must be strictly greater than the preceding record's timestamp.
    version         : INTEGRITY_CHAIN_VERSION at the time of creation.
    decision_hash   : SHA-256 hex digest of the raw decision payload bytes.
    previous_hash   : chain_hash of the preceding record; GENESIS_HASH for first.
    chain_hash      : SHA-256 hex digest that binds all fields into a single proof.
    """

    record_id: str
    timestamp_ns: int
    version: str
    decision_hash: str
    previous_hash: str
    chain_hash: str


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _compute_decision_hash(decision_data: bytes) -> str:
    return _sha256_hex(decision_data)


def _compute_chain_hash(
    *,
    record_id: str,
    timestamp_ns: int,
    version: str,
    decision_hash: str,
    previous_hash: str,
) -> str:
    """Deterministically bind all record fields into a single chain proof.

    Field order is fixed. The separator prevents field-boundary ambiguity.
    """
    payload = _FIELD_SEPARATOR.join([
        version,
        record_id,
        str(timestamp_ns),
        decision_hash,
        previous_hash,
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


def _validate_record_fields(record: object) -> str | None:
    if not isinstance(record, DecisionRecord):
        return IntegrityErrorCode.INVALID_RECORD.value
    if not isinstance(record.record_id, str) or not record.record_id.strip():
        return IntegrityErrorCode.INVALID_RECORD.value
    if not isinstance(record.timestamp_ns, int) or isinstance(record.timestamp_ns, bool):
        return IntegrityErrorCode.INVALID_RECORD.value
    if record.timestamp_ns <= 0:
        return IntegrityErrorCode.INVALID_RECORD.value
    if not isinstance(record.version, str) or record.version != INTEGRITY_CHAIN_VERSION:
        return IntegrityErrorCode.VERSION_MISMATCH.value
    if not _is_valid_hex_digest(record.decision_hash):
        return IntegrityErrorCode.INVALID_RECORD.value
    if not _is_valid_hex_digest(record.previous_hash):
        return IntegrityErrorCode.INVALID_RECORD.value
    if not _is_valid_hex_digest(record.chain_hash):
        return IntegrityErrorCode.INVALID_RECORD.value
    return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def create_decision_record(
    *,
    record_id: str,
    decision_data: bytes,
    previous_record: DecisionRecord | None,
    timestamp_ns: int | None = None,
) -> tuple[DecisionRecord | None, str | None]:
    """Create a new DecisionRecord and attach it to the chain.

    This function is stateless. Callers are responsible for maintaining
    the chain sequence and passing the correct previous_record.

    Parameters
    ----------
    record_id       : Unique identifier for this decision. Must be non-empty.
    decision_data   : Raw bytes representing the decision payload to record.
    previous_record : The preceding DecisionRecord, or None for the genesis entry.
    timestamp_ns    : Timestamp in UTC nanoseconds. Defaults to time.time_ns().
                      Must be strictly greater than previous_record.timestamp_ns.

    Returns
    -------
    (DecisionRecord, None)   on success.
    (None, error_code)       on any validation failure — fail-closed.
    """
    if not isinstance(record_id, str) or not record_id.strip():
        return None, IntegrityErrorCode.INVALID_RECORD.value

    if not isinstance(decision_data, bytes) or not decision_data:
        return None, IntegrityErrorCode.INVALID_DECISION_DATA.value

    if timestamp_ns is None:
        timestamp_ns = time.time_ns()

    if not isinstance(timestamp_ns, int) or isinstance(timestamp_ns, bool) or timestamp_ns <= 0:
        return None, IntegrityErrorCode.INVALID_RECORD.value

    if previous_record is None:
        previous_hash = GENESIS_HASH
    else:
        field_error = _validate_record_fields(previous_record)
        if field_error is not None:
            return None, field_error
        if timestamp_ns <= previous_record.timestamp_ns:
            return None, IntegrityErrorCode.TIMESTAMP_REGRESSION.value
        previous_hash = previous_record.chain_hash

    normalized_record_id = record_id.strip()
    decision_hash = _compute_decision_hash(decision_data)
    chain_hash = _compute_chain_hash(
        record_id=normalized_record_id,
        timestamp_ns=timestamp_ns,
        version=INTEGRITY_CHAIN_VERSION,
        decision_hash=decision_hash,
        previous_hash=previous_hash,
    )

    return DecisionRecord(
        record_id=normalized_record_id,
        timestamp_ns=timestamp_ns,
        version=INTEGRITY_CHAIN_VERSION,
        decision_hash=decision_hash,
        previous_hash=previous_hash,
        chain_hash=chain_hash,
    ), None


def validate_chain(
    records: tuple[DecisionRecord, ...] | list[DecisionRecord],
) -> tuple[bool, str | None]:
    """Validate the integrity of a complete decision chain.

    Stateless. Any sequence of DecisionRecords can be validated independently.

    Checks performed in order (fail-closed — stops at first violation):
    1. Chain is non-empty.
    2. Every record passes field-level validation.
    3. First record's previous_hash equals GENESIS_HASH.
    4. Each record's previous_hash equals the prior record's chain_hash.
    5. Timestamps are strictly monotonically increasing.
    6. Each record's chain_hash can be independently recomputed and matches.

    Returns (True, None) on success.
    Returns (False, error_code) on any violation.
    """
    if not isinstance(records, (tuple, list)) or not records:
        return False, IntegrityErrorCode.EMPTY_CHAIN.value

    for record in records:
        field_error = _validate_record_fields(record)
        if field_error is not None:
            return False, field_error

    if records[0].previous_hash != GENESIS_HASH:
        return False, IntegrityErrorCode.GENESIS_MISMATCH.value

    for index, record in enumerate(records):
        if index > 0:
            prior = records[index - 1]
            if record.timestamp_ns <= prior.timestamp_ns:
                return False, IntegrityErrorCode.TIMESTAMP_REGRESSION.value
            if record.previous_hash != prior.chain_hash:
                return False, IntegrityErrorCode.CHAIN_BROKEN.value

        expected = _compute_chain_hash(
            record_id=record.record_id,
            timestamp_ns=record.timestamp_ns,
            version=record.version,
            decision_hash=record.decision_hash,
            previous_hash=record.previous_hash,
        )
        if record.chain_hash != expected:
            return False, IntegrityErrorCode.HASH_MISMATCH.value

    return True, None


def recompute_decision_hash(decision_data: bytes) -> str | None:
    """Recompute the decision_hash for a given payload.

    Use to verify that a stored record still matches its original data.
    Returns None if decision_data is invalid.
    """
    if not isinstance(decision_data, bytes) or not decision_data:
        return None
    return _compute_decision_hash(decision_data)


__all__ = [
    "INTEGRITY_CHAIN_VERSION",
    "GENESIS_HASH",
    "DecisionRecord",
    "create_decision_record",
    "validate_chain",
    "recompute_decision_hash",
]
