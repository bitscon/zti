# Zero Trust Intelligence (ZTI)

## A Decision Verification Protocol for AI-Driven Systems

AI output is not a decision. A decision is something that can be proven.

Zero Trust Intelligence (ZTI) introduces a deterministic decision verification layer
that transforms AI proposals into provable, auditable, and tamper-evident decision artifacts.

Don't trust AI. Verify it.

ZTI does not make AI smarter.

It defines when AI output is allowed to act.

Zero Trust Intelligence (ZTI)
Author: Chad McCormack
© 2026 Chad McCormack
(Future ownership may be assigned to a legal entity)

*Version 1.0 — April 2026*

---

## Current Project Status

The website is on the barn-first, single-source workflow and the demo is compiled
deterministically from a canonical session model.

For the current migration checkpoint, completed work, known consistency gaps, and
the next required actions, read:

- [PROJECT_STATUS.md](PROJECT_STATUS.md)

---

## What ZTI Is

ZTI defines a new architectural layer in modern systems:

The deterministic decision verification layer, also described here as the Intelligence Trust Layer.

```text
AI (stochastic generation layer)
↓
ZTI (deterministic decision verification layer)
↓
Execution systems
```

This layer does not generate intelligence.
It does not execute actions.

It enforces one rule:

**Only verified decisions are allowed to pass.**

---

## AI vs ZTI

AI and ZTI are not competing systems. They are two different kinds of system at two different positions in the execution stack.

**AI:**
- Probabilistic and generative
- Exploratory, useful for proposing options
- Not a decision system — a proposal system

**ZTI:**
- Deterministic and restrictive
- Enforcement-based, reproducible
- Not an intelligence system — a verification system

> ZTI does not constrain how AI thinks. It constrains what AI is allowed to do.

---

## The Core Principle

No decision is trusted unless it is proven.

AI generates. ZTI verifies. Only verified decisions execute.

A decision is only valid if it is:

- Mapped to an allowed decision type
- Explained in explicit artifact form
- Validated against declared constraints
- Cryptographically sealed
- Lineage-bound to origin and approvals

If any condition fails:

**The decision does not exist.**

---

## Architecture

ZTI transforms raw AI output into a Verified Decision through a deterministic pipeline:

```text
INPUT (AI Output)
  ↓
Pattern Registry
  ↓
Detection
  ↓
Explainability
  ↓
Validation
  ↓
Integrity
  ↓
Lineage
  ↓
VERIFIED DECISION
```

- Pattern Registry defines the contract of allowed decision classes, schemas, and constraints.
- Detection determines what applies via deterministic classification — no inference, no probability.
- Explainability produces an explicit evidence artifact for why the proposal matched.
- Validation enforces admissibility against explicit constraints.
- Integrity locks the decision with cryptographic sealing and chaining.
- Lineage tracks provenance, approvals, and historical linkage.

---

## The Verified Decision

A Verified Decision is:

- Derived
- Explained
- Validated
- Sealed
- Traceable

A Verified Decision is not proof that the AI was right. It is proof that the proposal satisfied the execution contract.

Only Verified Decisions are allowed to cross system boundaries.

Everything else is discarded.

---

## Deterministic Verification, Not Deterministic AI

The verification of a decision must be deterministic and reproducible.

The AI generation process does not have to be.

Verification requires no randomness, no implicit behavior, no hidden state.

If a verification result cannot be reproduced, it is invalid.

This constraint applies to the verification layer — not to the AI system being verified.

---

## Audit Mode and Enforcement Mode

ZTI operates in two modes.

**Audit Mode** — observe, classify, validate, seal, and report without blocking execution. Use this to build visibility into AI-generated proposals before enforcement is active.

**Enforcement Mode** — the execution boundary is fail-closed. Unverifiable outputs do not execute. Fail-closed applies to execution authorization — not general system usability.

---

## Reference Implementation

The following example is a reference implementation of the deterministic verification components — pattern detection, explainability, integrity chaining, and lineage. It demonstrates the verification pipeline, not model behavior improvement.

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
from zti.serialization import serialize_explanation_artifact

bundle = InteractionBundle(
    session_id="session-001",
    interactions=(
        Interaction("i-001", ("open_question_density",), 10),
        Interaction("i-002", ("option_space_expansion",), 20),
        Interaction("i-003", ("hypothesis_generation",), 30),
    ),
)

patterns, _, err = detect_patterns(bundle, DEFAULT_REGISTRY)
assert err is None and patterns

artifacts, _, err = explain_patterns(tuple(patterns), DEFAULT_REGISTRY)
assert err is None and artifacts

record, err = create_decision_record(
    record_id="session-001:exploratory",
    decision_data=serialize_explanation_artifact(artifacts[0]),
    previous_record=None,
)
assert err is None

valid, err = validate_chain((record,))
assert valid is True and err is None
```

---

## What ZTI Is Not

ZTI does not:

- Improve AI intelligence
- Prevent hallucinations
- Replace model safety research
- Guarantee correctness of AI outputs
- Replace AI models
- Act as an agent framework
- Serve as a general-purpose library or model

ZTI does:

- Define when AI output is allowed to become a decision
- Enforce verification before execution
- Provide auditability, lineage, and integrity guarantees

---

## Example: Infrastructure Change

An AI agent generates a Terraform plan. ZTI classifies it into an approved infrastructure-change decision type, then validates policy constraints: approved modules, permitted regions, blast-radius limits, required approvals, schema compliance.

ZTI emits an explanation artifact and seals a reproducible decision artifact. Only that verified artifact is allowed to reach the execution system. If verification fails, the proposal is logged in audit mode or blocked in enforcement mode.

Auditors can later reconstruct what was proposed, which policy it passed against, who approved it, and which artifact hash reached execution.

---

## Where This Matters

ZTI becomes critical anywhere AI-generated proposals drive consequential execution:

- Infrastructure automation
- Security enforcement
- Financial systems
- Compliance and audit pipelines
- Autonomous systems

As systems become more automated, the boundary between proposal and execution becomes the highest-risk surface in the architecture.

---

## Install

Clone the repository and install it in editable mode:

```bash
git clone https://github.com/bitscon/zerotrustintelligence
cd zerotrustintelligence
python3 -m pip install -e .
```

Run the test suite locally with:

```bash
python3 -m pytest -q
```

---

## Examples

Reference examples are available in [`examples/`](examples/).

---

## Whitepaper

Full protocol specification:

[`whitepaper/zti-whitepaper.md`](whitepaper/zti-whitepaper.md)

---

## Site

Website source lives in:

[`dev/site/_src/`](dev/site/_src/)

Build the deployable site artifact with:

```bash
python3 dev/site/build.py --out dev/site/_dist
```

Verify it with:

```bash
./ops/verify.sh
```

---

## License

MIT License
