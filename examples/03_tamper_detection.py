"""
ZTI Example 03 — Tamper Detection

Demonstrates that any modification to a record in the chain is detected
by validate_chain. The chain is cryptographically sealed — no tampering
is silent.
"""

from zti.integrity import (
    DecisionRecord,
    create_decision_record,
    validate_chain,
    recompute_decision_hash,
)
from zti.errors import IntegrityErrorCode

# Build a valid 3-record chain.
r1, _ = create_decision_record(record_id="d-001", decision_data=b"output A", previous_record=None, timestamp_ns=1_000_000_001)
r2, _ = create_decision_record(record_id="d-002", decision_data=b"output B", previous_record=r1, timestamp_ns=1_000_000_002)
r3, _ = create_decision_record(record_id="d-003", decision_data=b"output C", previous_record=r2, timestamp_ns=1_000_000_003)

chain = [r1, r2, r3]
valid, err = validate_chain(chain)
assert valid is True
print(f"Original chain valid: {valid}")

# --- Tamper 1: modify the decision_hash of record 2 ---
tampered_r2 = DecisionRecord(
    record_id=r2.record_id,
    timestamp_ns=r2.timestamp_ns,
    version=r2.version,
    decision_hash="f" * 64,           # tampered — payload changed
    previous_hash=r2.previous_hash,
    chain_hash=r2.chain_hash,         # chain_hash no longer matches
)
valid, err = validate_chain([r1, tampered_r2, r3])
assert valid is False
print(f"\nTamper 1 (decision_hash): valid={valid}, error={err}")

# --- Tamper 2: swap record ordering ---
valid, err = validate_chain([r2, r1, r3])
assert valid is False
print(f"Tamper 2 (reordering):    valid={valid}, error={err}")

# --- Tamper 3: inject an unrelated record into the middle ---
foreign, _ = create_decision_record(
    record_id="injected",
    decision_data=b"injected output",
    previous_record=None,
    timestamp_ns=1_000_000_002,
)
valid, err = validate_chain([r1, foreign, r3])
assert valid is False
print(f"Tamper 3 (injection):     valid={valid}, error={err}")

# --- Verify recompute_decision_hash detects payload drift ---
original_payload = b"output B"
tampered_payload = b"output B (modified)"
assert recompute_decision_hash(original_payload) == r2.decision_hash
assert recompute_decision_hash(tampered_payload) != r2.decision_hash
print(f"\nPayload drift detection:  recomputed matches original={recompute_decision_hash(original_payload) == r2.decision_hash}")
print(f"                          recomputed matches tampered={recompute_decision_hash(tampered_payload) == r2.decision_hash}")

print("\nAll tampering attempts correctly detected.")
