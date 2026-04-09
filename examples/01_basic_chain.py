"""
ZTI Example 01 — Basic Decision → Record → Chain

Demonstrates the minimal integrity chain: create two decision records,
chain them, and validate the result.
"""

from zti.integrity import create_decision_record, validate_chain

# Decision 1 — genesis
record1, err = create_decision_record(
    record_id="decision-001",
    decision_data=b"AI output: the sky is blue",
    previous_record=None,
    timestamp_ns=1_000_000_001,
)
assert err is None, f"Failed to create record 1: {err}"
assert record1 is not None

print(f"Record 1 ID:    {record1.record_id}")
print(f"  decision_hash: {record1.decision_hash[:16]}...")
print(f"  previous_hash: {record1.previous_hash[:16]}...")
print(f"  chain_hash:    {record1.chain_hash[:16]}...")

# Decision 2 — chained to record 1
record2, err = create_decision_record(
    record_id="decision-002",
    decision_data=b"AI output: water is H2O",
    previous_record=record1,
    timestamp_ns=1_000_000_002,
)
assert err is None, f"Failed to create record 2: {err}"
assert record2 is not None
assert record2.previous_hash == record1.chain_hash

print(f"\nRecord 2 ID:    {record2.record_id}")
print(f"  previous_hash matches record1.chain_hash: {record2.previous_hash == record1.chain_hash}")

# Validate the complete chain
chain = [record1, record2]
valid, chain_err = validate_chain(chain)
assert valid is True, f"Chain validation failed: {chain_err}"
print(f"\nChain length: {len(chain)}")
print(f"Chain valid:  {valid}")
print(f"Chain error:  {chain_err}")
