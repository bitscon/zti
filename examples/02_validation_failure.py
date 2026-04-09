"""
ZTI Example 02 — Validation Failure

Demonstrates fail-closed behavior: invalid inputs are rejected at every
layer. No partial success is possible.
"""

from zti.integrity import create_decision_record, validate_chain
from zti.errors import IntegrityErrorCode

print("=== Empty record_id ===")
record, err = create_decision_record(
    record_id="",
    decision_data=b"some decision",
    previous_record=None,
    timestamp_ns=1_000_000_001,
)
assert record is None
assert err == IntegrityErrorCode.INVALID_RECORD.value
print(f"  record: {record}")
print(f"  error:  {err}")

print("\n=== Empty decision_data ===")
record, err = create_decision_record(
    record_id="decision-001",
    decision_data=b"",
    previous_record=None,
    timestamp_ns=1_000_000_001,
)
assert record is None
assert err == IntegrityErrorCode.INVALID_DECISION_DATA.value
print(f"  record: {record}")
print(f"  error:  {err}")

print("\n=== Timestamp regression ===")
from zti.integrity import create_decision_record

first, _ = create_decision_record(
    record_id="d-001",
    decision_data=b"first",
    previous_record=None,
    timestamp_ns=1_000_000_010,
)
record, err = create_decision_record(
    record_id="d-002",
    decision_data=b"second",
    previous_record=first,
    timestamp_ns=1_000_000_005,  # earlier than first — regression
)
assert record is None
assert err == IntegrityErrorCode.TIMESTAMP_REGRESSION.value
print(f"  record: {record}")
print(f"  error:  {err}")

print("\n=== Empty chain ===")
valid, chain_err = validate_chain([])
assert valid is False
assert chain_err == IntegrityErrorCode.EMPTY_CHAIN.value
print(f"  valid:  {valid}")
print(f"  error:  {chain_err}")

print("\nAll failure cases correctly rejected.")
