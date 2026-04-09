"""Tests for ZTI integrity layer — deterministic, stateless."""

from __future__ import annotations

import hashlib
import pytest

from zti.integrity import (
    GENESIS_HASH,
    INTEGRITY_CHAIN_VERSION,
    DecisionRecord,
    create_decision_record,
    recompute_decision_hash,
    validate_chain,
)
from zti.errors import IntegrityErrorCode

_BASE_TS = 1_000_000_000


def _make(
    *,
    record_id: str = "r-001",
    decision_data: bytes = b"payload",
    previous_record: DecisionRecord | None = None,
    timestamp_ns: int = _BASE_TS,
) -> DecisionRecord:
    record, err = create_decision_record(
        record_id=record_id,
        decision_data=decision_data,
        previous_record=previous_record,
        timestamp_ns=timestamp_ns,
    )
    assert err is None
    assert record is not None
    return record


def _chain(*payloads: bytes) -> list[DecisionRecord]:
    records: list[DecisionRecord] = []
    for i, payload in enumerate(payloads):
        r = _make(
            record_id=f"r-{i+1:03d}",
            decision_data=payload,
            previous_record=records[-1] if records else None,
            timestamp_ns=_BASE_TS + i,
        )
        records.append(r)
    return records


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


# -- create_decision_record valid --

def test_genesis_has_genesis_hash():
    r = _make()
    assert r.previous_hash == GENESIS_HASH


def test_chained_previous_hash_matches_prior_chain_hash():
    r1 = _make(timestamp_ns=_BASE_TS)
    r2 = _make(record_id="r-002", decision_data=b"b", previous_record=r1, timestamp_ns=_BASE_TS + 1)
    assert r2.previous_hash == r1.chain_hash


def test_decision_hash_matches_payload():
    payload = b"the payload"
    r = _make(decision_data=payload)
    assert r.decision_hash == _sha256(payload)


def test_version():
    r = _make()
    assert r.version == INTEGRITY_CHAIN_VERSION


def test_record_id_stripped():
    r = _make(record_id="  r-001  ")
    assert r.record_id == "r-001"


def test_chain_hash_deterministic():
    r1 = _make()
    r2 = _make()
    assert r1.chain_hash == r2.chain_hash


def test_different_payloads_different_chain_hashes():
    r1 = _make(decision_data=b"a")
    r2 = _make(decision_data=b"b")
    assert r1.chain_hash != r2.chain_hash


# -- create_decision_record invalid --

def test_empty_record_id_fails():
    r, err = create_decision_record(record_id="", decision_data=b"d", previous_record=None, timestamp_ns=_BASE_TS)
    assert r is None and err == IntegrityErrorCode.INVALID_RECORD.value


def test_empty_decision_data_fails():
    r, err = create_decision_record(record_id="r", decision_data=b"", previous_record=None, timestamp_ns=_BASE_TS)
    assert r is None and err == IntegrityErrorCode.INVALID_DECISION_DATA.value


def test_zero_timestamp_fails():
    r, err = create_decision_record(record_id="r", decision_data=b"d", previous_record=None, timestamp_ns=0)
    assert r is None and err == IntegrityErrorCode.INVALID_RECORD.value


def test_timestamp_regression_fails():
    r1 = _make(timestamp_ns=_BASE_TS + 10)
    r, err = create_decision_record(record_id="r-002", decision_data=b"d", previous_record=r1, timestamp_ns=_BASE_TS)
    assert r is None and err == IntegrityErrorCode.TIMESTAMP_REGRESSION.value


def test_equal_timestamp_is_regression():
    r1 = _make(timestamp_ns=_BASE_TS)
    r, err = create_decision_record(record_id="r-002", decision_data=b"d", previous_record=r1, timestamp_ns=_BASE_TS)
    assert r is None and err == IntegrityErrorCode.TIMESTAMP_REGRESSION.value


# -- validate_chain valid --

def test_single_record_chain_valid():
    valid, err = validate_chain(_chain(b"a"))
    assert valid is True and err is None


def test_long_chain_valid():
    valid, err = validate_chain(_chain(*[f"p-{i}".encode() for i in range(20)]))
    assert valid is True and err is None


def test_accepts_tuple():
    valid, err = validate_chain(tuple(_chain(b"a", b"b")))
    assert valid is True


# -- validate_chain invalid --

def test_empty_list_fails():
    valid, err = validate_chain([])
    assert valid is False and err == IntegrityErrorCode.EMPTY_CHAIN.value


def test_tampered_decision_hash_detected():
    records = _chain(b"a", b"b")
    tampered = DecisionRecord(
        record_id=records[0].record_id,
        timestamp_ns=records[0].timestamp_ns,
        version=records[0].version,
        decision_hash="f" * 64,
        previous_hash=records[0].previous_hash,
        chain_hash=records[0].chain_hash,
    )
    valid, err = validate_chain([tampered, records[1]])
    assert valid is False


def test_genesis_mismatch_detected():
    r1 = _make()
    r2 = _make(record_id="r-002", decision_data=b"b", previous_record=r1, timestamp_ns=_BASE_TS + 1)
    valid, err = validate_chain([r2])  # r2.previous_hash != GENESIS_HASH
    assert valid is False and err == IntegrityErrorCode.GENESIS_MISMATCH.value


def test_wrong_version_fails():
    r = _make()
    bad = DecisionRecord(
        record_id=r.record_id, timestamp_ns=r.timestamp_ns,
        version="0.0.0", decision_hash=r.decision_hash,
        previous_hash=r.previous_hash, chain_hash=r.chain_hash,
    )
    valid, err = validate_chain([bad])
    assert valid is False and err == IntegrityErrorCode.VERSION_MISMATCH.value


# -- recompute_decision_hash --

def test_recompute_matches_record():
    payload = b"known payload"
    r = _make(decision_data=payload)
    assert recompute_decision_hash(payload) == r.decision_hash


def test_recompute_empty_returns_none():
    assert recompute_decision_hash(b"") is None
