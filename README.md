# Zero Trust Intelligence (ZTI)

**Don't trust AI. Verify it.**

ZTI is a deterministic verification protocol for AI systems. It defines how to verify AI outputs — not how to improve AI models. The protocol is execution-free, stateless (except for the integrity chain), and fail-closed.

---

## Core Principle

No AI output is trusted without verification.

This is an architectural constraint, not a guideline. Every component in a ZTI system enforces this constraint. There are no exceptions.

---

## Architecture

```
Registry → Detection → Explainability → Validation → Integrity
```

| Layer | Role |
|---|---|
| **Registry** | Versioned, closed set of valid patterns. Ground truth for all verification. |
| **Detection** | Deterministic pattern matching. Evidence-bound. Fail-closed. |
| **Explainability** | Auditable artifacts for every detected pattern. |
| **Validation** | Cross-layer integrity check. All-or-nothing. |
| **Integrity** | Hash-chained, tamper-evident record of every verified decision. |

Each layer validates its inputs independently. No layer trusts any other by default.

---

## How It Differs From Traditional AI Safety

| Traditional approach | ZTI |
|---|---|
| Filter known-bad outputs | Verify all outputs deterministically |
| Sample with human review | Produce tamper-evident audit trail |
| Tune models toward reliability | Make model reliability irrelevant |
| Guardrails at the edge | Verification at every layer |
| Probabilistic confidence | Deterministic evidence-bound results |

---

## Quick Start

```python
from zti import (
    DEFAULT_REGISTRY,
    Interaction,
    InteractionBundle,
    detect_patterns,
    explain_patterns,
    create_decision_record,
    validate_chain,
)

# 1. Build a bundle of observed interactions
bundle = InteractionBundle(
    session_id="session-001",
    interactions=(
        Interaction("i-001", ("open_question_density",), 10),
        Interaction("i-002", ("option_space_expansion",), 20),
        Interaction("i-003", ("hypothesis_generation",), 30),
    ),
)

# 2. Detect patterns
patterns, evidence_refs, err = detect_patterns(bundle, DEFAULT_REGISTRY)
assert err is None

# 3. Generate explanation artifacts
artifacts, _, err = explain_patterns(tuple(patterns), DEFAULT_REGISTRY)
assert err is None

# 4. Record into the integrity chain
from zti.serialization import serialize_explanation_artifact

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

# 5. Validate the chain
valid, err = validate_chain(chain)
assert valid is True
```

---

## Installation

```bash
pip install zti
```

Or from source:

```bash
git clone https://github.com/zerotrustintelligence/zerotrustintelligence
cd zerotrustintelligence
pip install -e .
```

---

## Contents

```
zti/                     Protocol implementation
  registry.py            Pattern registry (schema + validation)
  detection.py           Deterministic pattern detection
  explainability.py      Auditable explanation artifacts
  validation.py          Cross-layer integrity validation
  integrity.py           Hash-chained decision records
  serialization.py       Deterministic canonical serialization
  errors.py              Error code enumerations

examples/
  01_basic_chain.py      Decision → record → chain
  02_validation_failure.py  Fail-closed behavior
  03_tamper_detection.py    Tamper detection

whitepaper/
  zti-whitepaper.md      Full protocol specification

site/
  index.html             Protocol homepage
```

---

## Whitepaper

The full protocol specification is in [whitepaper/zti-whitepaper.md](whitepaper/zti-whitepaper.md).

---

## License

Public domain. Implement freely.
