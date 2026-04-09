"""
Zero Trust Intelligence (ZTI) — Lineage Layer Tests

Author: Chad McCormack
© 2026 Chad McCormack
"""

from __future__ import annotations

import dataclasses

import pytest

from zti.lineage import (
    APPROVAL_ACTION_APPROVE,
    APPROVAL_ACTION_REJECT,
    LINEAGE_CONTRACT_VERSION,
    LINEAGE_EMPTY,
    LINEAGE_HASH_MISMATCH,
    LINEAGE_INVALID_ACTION,
    LINEAGE_INVALID_ENTRY,
    LINEAGE_TIMESTAMP_REGRESSION,
    LINEAGE_VERSION_MISMATCH,
    ApprovalLineageEntry,
    create_lineage_entry,
    recompute_entry_hash,
    validate_lineage,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _entry(
    *,
    entry_id: str = "entry-001",
    decision_record_id: str = "decision-001",
    approver_id: str = "approver-alice",
    approval_action: str = APPROVAL_ACTION_APPROVE,
    timestamp_ns: int = 1_000_000_001,
) -> ApprovalLineageEntry:
    entry, err = create_lineage_entry(
        entry_id=entry_id,
        decision_record_id=decision_record_id,
        approver_id=approver_id,
        approval_action=approval_action,
        timestamp_ns=timestamp_ns,
    )
    assert err is None
    assert entry is not None
    return entry


# ---------------------------------------------------------------------------
# create_lineage_entry — happy path
# ---------------------------------------------------------------------------

def test_create_approve_entry():
    entry, err = create_lineage_entry(
        entry_id="e-001",
        decision_record_id="dr-001",
        approver_id="alice",
        approval_action=APPROVAL_ACTION_APPROVE,
        timestamp_ns=1_000_000_001,
    )
    assert err is None
    assert entry is not None
    assert entry.entry_id == "e-001"
    assert entry.decision_record_id == "dr-001"
    assert entry.approver_id == "alice"
    assert entry.approval_action == APPROVAL_ACTION_APPROVE
    assert entry.timestamp_ns == 1_000_000_001
    assert entry.version == LINEAGE_CONTRACT_VERSION
    assert len(entry.entry_hash) == 64


def test_create_reject_entry():
    entry, err = create_lineage_entry(
        entry_id="e-002",
        decision_record_id="dr-002",
        approver_id="bob",
        approval_action=APPROVAL_ACTION_REJECT,
        timestamp_ns=2_000_000_000,
    )
    assert err is None
    assert entry is not None
    assert entry.approval_action == APPROVAL_ACTION_REJECT


def test_entry_is_immutable():
    entry = _entry()
    with pytest.raises((dataclasses.FrozenInstanceError, AttributeError)):
        entry.entry_id = "tampered"  # type: ignore[misc]


def test_entry_hash_is_hex():
    entry = _entry()
    assert len(entry.entry_hash) == 64
    int(entry.entry_hash, 16)


def test_whitespace_stripped():
    entry, err = create_lineage_entry(
        entry_id="  e-001  ",
        decision_record_id="  dr-001  ",
        approver_id="  alice  ",
        approval_action=APPROVAL_ACTION_APPROVE,
        timestamp_ns=1_000_000_001,
    )
    assert err is None
    assert entry is not None
    assert entry.entry_id == "e-001"
    assert entry.decision_record_id == "dr-001"
    assert entry.approver_id == "alice"


# ---------------------------------------------------------------------------
# create_lineage_entry — failures
# ---------------------------------------------------------------------------

def test_empty_entry_id_fails():
    _, err = create_lineage_entry(
        entry_id="", decision_record_id="dr-001",
        approver_id="alice", approval_action=APPROVAL_ACTION_APPROVE,
        timestamp_ns=1_000_000_001,
    )
    assert err == LINEAGE_INVALID_ENTRY


def test_empty_decision_record_id_fails():
    _, err = create_lineage_entry(
        entry_id="e-001", decision_record_id="",
        approver_id="alice", approval_action=APPROVAL_ACTION_APPROVE,
        timestamp_ns=1_000_000_001,
    )
    assert err == LINEAGE_INVALID_ENTRY


def test_empty_approver_id_fails():
    _, err = create_lineage_entry(
        entry_id="e-001", decision_record_id="dr-001",
        approver_id="", approval_action=APPROVAL_ACTION_APPROVE,
        timestamp_ns=1_000_000_001,
    )
    assert err == LINEAGE_INVALID_ENTRY


def test_invalid_action_fails():
    _, err = create_lineage_entry(
        entry_id="e-001", decision_record_id="dr-001",
        approver_id="alice", approval_action="maybe",
        timestamp_ns=1_000_000_001,
    )
    assert err == LINEAGE_INVALID_ACTION


def test_zero_timestamp_fails():
    _, err = create_lineage_entry(
        entry_id="e-001", decision_record_id="dr-001",
        approver_id="alice", approval_action=APPROVAL_ACTION_APPROVE,
        timestamp_ns=0,
    )
    assert err == LINEAGE_INVALID_ENTRY


def test_negative_timestamp_fails():
    _, err = create_lineage_entry(
        entry_id="e-001", decision_record_id="dr-001",
        approver_id="alice", approval_action=APPROVAL_ACTION_APPROVE,
        timestamp_ns=-1,
    )
    assert err == LINEAGE_INVALID_ENTRY


# ---------------------------------------------------------------------------
# validate_lineage — happy path
# ---------------------------------------------------------------------------

def test_single_entry_valid():
    entry = _entry(timestamp_ns=1_000_000_001)
    valid, err = validate_lineage((entry,))
    assert valid is True
    assert err is None


def test_multiple_entries_valid():
    e1 = _entry(entry_id="e-001", timestamp_ns=1_000_000_001)
    e2 = _entry(entry_id="e-002", timestamp_ns=2_000_000_001)
    e3 = _entry(entry_id="e-003", timestamp_ns=3_000_000_001)
    valid, err = validate_lineage((e1, e2, e3))
    assert valid is True
    assert err is None


def test_list_input_accepted():
    e1 = _entry(entry_id="e-001", timestamp_ns=1_000_000_001)
    e2 = _entry(entry_id="e-002", timestamp_ns=2_000_000_001)
    valid, err = validate_lineage([e1, e2])
    assert valid is True
    assert err is None


def test_mixed_actions_valid():
    e1 = _entry(entry_id="e-001", approval_action=APPROVAL_ACTION_APPROVE, timestamp_ns=1_000_000_001)
    e2 = _entry(entry_id="e-002", approval_action=APPROVAL_ACTION_REJECT, timestamp_ns=2_000_000_001)
    valid, err = validate_lineage((e1, e2))
    assert valid is True
    assert err is None


# ---------------------------------------------------------------------------
# validate_lineage — failures
# ---------------------------------------------------------------------------

def test_empty_tuple_fails():
    valid, err = validate_lineage(())
    assert valid is False
    assert err == LINEAGE_EMPTY


def test_empty_list_fails():
    valid, err = validate_lineage([])
    assert valid is False
    assert err == LINEAGE_EMPTY


def test_timestamp_regression_fails():
    e1 = _entry(entry_id="e-001", timestamp_ns=2_000_000_001)
    e2 = _entry(entry_id="e-002", timestamp_ns=1_000_000_001)
    valid, err = validate_lineage((e1, e2))
    assert valid is False
    assert err == LINEAGE_TIMESTAMP_REGRESSION


def test_equal_timestamps_fail():
    e1 = _entry(entry_id="e-001", timestamp_ns=1_000_000_001)
    e2 = _entry(entry_id="e-002", timestamp_ns=1_000_000_001)
    valid, err = validate_lineage((e1, e2))
    assert valid is False
    assert err == LINEAGE_TIMESTAMP_REGRESSION


def test_tampered_hash_fails():
    entry = _entry(timestamp_ns=1_000_000_001)
    tampered = dataclasses.replace(entry, entry_hash="a" * 64)
    valid, err = validate_lineage((tampered,))
    assert valid is False
    assert err == LINEAGE_HASH_MISMATCH


def test_tampered_decision_record_id_fails():
    entry = _entry(timestamp_ns=1_000_000_001)
    tampered = dataclasses.replace(entry, decision_record_id="injected")
    valid, err = validate_lineage((tampered,))
    assert valid is False
    assert err == LINEAGE_HASH_MISMATCH


def test_tampered_approver_id_fails():
    entry = _entry(timestamp_ns=1_000_000_001)
    tampered = dataclasses.replace(entry, approver_id="injected-approver")
    valid, err = validate_lineage((tampered,))
    assert valid is False
    assert err == LINEAGE_HASH_MISMATCH


def test_wrong_version_fails():
    entry = _entry(timestamp_ns=1_000_000_001)
    tampered = dataclasses.replace(entry, version="0.0.0")
    valid, err = validate_lineage((tampered,))
    assert valid is False
    assert err == LINEAGE_VERSION_MISMATCH


# ---------------------------------------------------------------------------
# recompute_entry_hash
# ---------------------------------------------------------------------------

def test_recompute_matches_created_hash():
    entry = _entry(timestamp_ns=1_000_000_001)
    recomputed = recompute_entry_hash(
        entry_id=entry.entry_id,
        decision_record_id=entry.decision_record_id,
        approver_id=entry.approver_id,
        approval_action=entry.approval_action,
        timestamp_ns=entry.timestamp_ns,
    )
    assert recomputed == entry.entry_hash


def test_recompute_invalid_action_returns_none():
    result = recompute_entry_hash(
        entry_id="e-001", decision_record_id="dr-001",
        approver_id="alice", approval_action="invalid",
        timestamp_ns=1_000_000_001,
    )
    assert result is None


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------

def test_same_inputs_same_hash():
    kwargs = dict(
        entry_id="e-001", decision_record_id="dr-001",
        approver_id="alice", approval_action=APPROVAL_ACTION_APPROVE,
        timestamp_ns=1_000_000_001,
    )
    e1, _ = create_lineage_entry(**kwargs)
    e2, _ = create_lineage_entry(**kwargs)
    assert e1 is not None and e2 is not None
    assert e1.entry_hash == e2.entry_hash


def test_different_approver_different_hash():
    e1 = _entry(approver_id="alice", timestamp_ns=1_000_000_001)
    e2 = _entry(approver_id="bob", timestamp_ns=1_000_000_001)
    assert e1.entry_hash != e2.entry_hash
