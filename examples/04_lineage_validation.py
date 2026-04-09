"""
Zero Trust Intelligence (ZTI) — Example 04: Lineage Validation

Author: Chad McCormack
© 2026 Chad McCormack

Demonstrates the ZTI lineage layer: recording and validating a sequence of
approval events bound to verified decision records.

Each approval event is cryptographically hashed. The sequence is validated
for tamper detection and strict monotonic timestamps.
"""

from zti.lineage import (
    APPROVAL_ACTION_APPROVE,
    APPROVAL_ACTION_REJECT,
    create_lineage_entry,
    recompute_entry_hash,
    validate_lineage,
)

# ---------------------------------------------------------------------------
# 1. Create a valid sequence of approval lineage entries
# ---------------------------------------------------------------------------

print("=== ZTI Lineage: Valid Approval Sequence ===\n")

e1, err = create_lineage_entry(
    entry_id="entry-001",
    decision_record_id="decision-001",
    approver_id="alice@domain.com",
    approval_action=APPROVAL_ACTION_APPROVE,
    timestamp_ns=1_000_000_001,
)
assert err is None, f"Unexpected error: {err}"

e2, err = create_lineage_entry(
    entry_id="entry-002",
    decision_record_id="decision-002",
    approver_id="bob@domain.com",
    approval_action=APPROVAL_ACTION_APPROVE,
    timestamp_ns=2_000_000_001,
)
assert err is None, f"Unexpected error: {err}"

e3, err = create_lineage_entry(
    entry_id="entry-003",
    decision_record_id="decision-003",
    approver_id="carol@domain.com",
    approval_action=APPROVAL_ACTION_REJECT,
    timestamp_ns=3_000_000_001,
)
assert err is None, f"Unexpected error: {err}"

valid, err = validate_lineage((e1, e2, e3))
assert valid is True, f"Validation failed: {err}"

print(f"entry_id:           {e1.entry_id}")
print(f"decision_record_id: {e1.decision_record_id}")
print(f"approver_id:        {e1.approver_id}")
print(f"approval_action:    {e1.approval_action}")
print(f"timestamp_ns:       {e1.timestamp_ns}")
print(f"entry_hash:         {e1.entry_hash[:16]}...")
print(f"\nSequence of 3 entries: VALID\n")

# ---------------------------------------------------------------------------
# 2. Tamper detection — modified approver_id
# ---------------------------------------------------------------------------

print("=== ZTI Lineage: Tamper Detection ===\n")

import dataclasses

tampered = dataclasses.replace(e2, approver_id="attacker@domain.com")
valid, err = validate_lineage((e1, tampered, e3))
assert valid is False
assert err == "LINEAGE_HASH_MISMATCH"

print(f"Tampered approver_id → validate_lineage result: {err}")
print("Tamper detected. Entry rejected.\n")

# ---------------------------------------------------------------------------
# 3. Timestamp regression — out-of-order entries
# ---------------------------------------------------------------------------

print("=== ZTI Lineage: Timestamp Regression ===\n")

valid, err = validate_lineage((e2, e1))  # e2 timestamp > e1 timestamp
assert valid is False
assert err == "LINEAGE_TIMESTAMP_REGRESSION"

print(f"Out-of-order entries → validate_lineage result: {err}")
print("Regression detected. Sequence rejected.\n")

# ---------------------------------------------------------------------------
# 4. Recompute hash for verification
# ---------------------------------------------------------------------------

print("=== ZTI Lineage: Hash Recomputation ===\n")

recomputed = recompute_entry_hash(
    entry_id=e1.entry_id,
    decision_record_id=e1.decision_record_id,
    approver_id=e1.approver_id,
    approval_action=e1.approval_action,
    timestamp_ns=e1.timestamp_ns,
)
assert recomputed == e1.entry_hash

print(f"Stored hash:     {e1.entry_hash[:16]}...")
print(f"Recomputed hash: {recomputed[:16]}...")
print(f"Match: {recomputed == e1.entry_hash}\n")

print("ZTI_LINEAGE: VERIFIED")
