# Zero Trust Intelligence (ZTI)

**Don't trust AI. Verify it.**

**Author:** Chad McCormack  
**© 2026 Chad McCormack**  
*(Future ownership may be assigned to a legal entity)*

---

## Overview

AI outputs are not trustworthy by default. Large language models produce plausible text — not verified facts. They hallucinate. They are consistent within a session and wrong across sessions. They pass every guardrail and still fail in production.

The standard response is to add more filters, more human review, more confidence thresholds. None of these produce a deterministic, auditable record of what was verified, when, and by whom.

ZTI takes a different position.

**ZTI does not improve AI. It makes AI's trustworthiness irrelevant.**

Every AI output passes through a deterministic verification chain before it is accepted. The chain is fail-closed: if any layer fails, the output is rejected. Every verified decision is recorded in a tamper-evident integrity chain. Every approval event is bound cryptographically to the decision it covers.

The result is not a more reliable AI. It is a system that does not require AI to be reliable.

---

## Core Idea

```
AI Output → Detection → Explainability → Validation → Integrity → Lineage → Proof
```

No step is optional. No step degrades gracefully. Same input, same registry, same output — every time.

---

## Architecture

| Layer | Role |
|---|---|
| **Registry** | Versioned, closed set of valid patterns. Ground truth for all verification. |
| **Detection** | Deterministic pattern matching. Evidence-bound. Fail-closed. |
| **Explainability** | Auditable artifacts for every detected pattern. Produced before validation. |
| **Validation** | Cross-layer integrity check. All-or-nothing. |
| **Integrity** | Hash-chained, tamper-evident record of every verified decision. |
| **Lineage** | Cryptographically bound approval events — who approved what, when. |

Each layer validates its inputs independently. No layer trusts any other by default.

---

## Example

```python
from zti import (
    DEFAULT_REGISTRY,
    Interaction,
    InteractionBundle,
    detect_patterns,
    explain_patterns,
    create_decision_record,
    validate_chain,
    create_lineage_entry,
    validate_lineage,
    APPROVAL_ACTION_APPROVE,
)
from zti.serialization import serialize_explanation_artifact

# 1. Detect patterns in a bundle of interactions
bundle = InteractionBundle(
    session_id="session-001",
    interactions=(
        Interaction("i-001", ("open_question_density",), 10),
        Interaction("i-002", ("option_space_expansion",), 20),
        Interaction("i-003", ("hypothesis_generation",), 30),
    ),
)

patterns, evidence_refs, err = detect_patterns(bundle, DEFAULT_REGISTRY)
assert err is None

# 2. Generate auditable explanation artifacts
artifacts, _, err = explain_patterns(tuple(patterns), DEFAULT_REGISTRY)
assert err is None

# 3. Record each artifact into the integrity chain
chain = []
for artifact in artifacts:
    previous = chain[-1] if chain else None
    record, err = create_decision_record(
        record_id=f"{artifact.session_id}:{artifact.pattern_id}",
        decision_data=serialize_explanation_artifact(artifact),
        previous_record=previous,
    )
    assert err is None
    chain.append(record)

# 4. Validate the integrity chain
valid, err = validate_chain(chain)
assert valid is True

# 5. Record approval lineage
entry, err = create_lineage_entry(
    entry_id="approval-001",
    decision_record_id=chain[0].record_id,
    approver_id="reviewer@domain.com",
    approval_action=APPROVAL_ACTION_APPROVE,
    timestamp_ns=chain[0].timestamp_ns + 1,
)
assert err is None

valid, err = validate_lineage((entry,))
assert valid is True
```

---

## Non-Goals

ZTI is a **verification protocol**. It explicitly does not:

- Execute AI outputs
- Orchestrate agents or pipelines
- Manage storage, routing, or identity
- Tune or improve AI models
- Replace human judgment

---

## Installation

```bash
pip install zti
```

Or from source:

```bash
git clone https://github.com/bitscon/zerotrustintelligence
cd zerotrustintelligence
pip install -e .
```

---

## Contents

```
zti/
  registry.py          Pattern registry (schema + validation)
  detection.py         Deterministic pattern detection
  explainability.py    Auditable explanation artifacts
  validation.py        Cross-layer integrity validation
  integrity.py         Hash-chained decision records
  lineage.py           Approval lineage contract
  serialization.py     Deterministic canonical serialization
  errors.py            Error code enumerations

examples/
  01_basic_chain.py         Decision → record → chain
  02_validation_failure.py  Fail-closed behavior
  03_tamper_detection.py    Tamper detection
  04_lineage_validation.py  Approval lineage recording + validation

whitepaper/
  zti-whitepaper.md    Full protocol specification

site/
  index.html           Protocol homepage
```

---

## Whitepaper

The full protocol specification is in [whitepaper/zti-whitepaper.md](whitepaper/zti-whitepaper.md).

---

## License

MIT License — © 2026 Chad McCormack. Implement freely.
