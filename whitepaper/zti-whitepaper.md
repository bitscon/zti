# Zero Trust Intelligence (ZTI)
## A Protocol for Verifiable AI Systems

**Author:** Chad McCormack  
**© 2026 Chad McCormack**  
*(Future ownership may be assigned to a legal entity)*

*Version 1.0 — April 2026*

---

## Abstract

AI systems are probabilistic. They produce outputs that are plausible, not proven. No amount of calibration, fine-tuning, or prompt engineering eliminates this. The question is not how to make AI more reliable. The question is how to build systems that do not require AI to be trusted.

Zero Trust Intelligence (ZTI) answers that question with a protocol.

ZTI defines a verification chain that every AI output must pass before it is accepted. The chain is deterministic, fail-closed, and stateless except for the integrity record it produces. It does not modify AI behavior. It does not require access to model internals. It operates entirely on outputs.

The core principle is absolute:

> **No AI output is trusted without verification.**

---

## 1. The Problem

### 1.1 AI Is Probabilistic

Large language models and other AI systems operate on statistical inference. They produce the most plausible next token, not the correct one. This is not a defect — it is the mechanism. The result is a class of systems that are useful but inherently unverifiable at the inference layer.

AI outputs can be:

- Factually incorrect while appearing authoritative
- Consistent within a session but inconsistent across sessions
- Correct under normal conditions and wrong under distribution shift
- Manipulated by adversarial inputs in ways invisible to the model

### 1.2 Trust Accumulates Without Verification

Current deployment patterns treat AI as a trusted component. Outputs are filtered, ranked, or reviewed by humans — but the underlying assumption is that the AI's output is a reasonable starting point, not an untrusted claim.

This assumption fails in high-stakes domains. Legal. Medical. Financial. Compliance. In these domains, the cost of a confident, plausible, incorrect output is not a minor inconvenience. It is a liability.

### 1.3 Existing Approaches Are Insufficient

- **Guardrails** filter known-bad outputs. They do not verify correctness.
- **Human review** is sampling, not verification. It scales poorly and introduces its own errors.
- **Confidence scores** measure calibration, not truth. A highly confident wrong answer is still wrong.
- **RAG and grounding** reduce hallucination rates. They do not eliminate them.

None of these approaches establish a deterministic, auditable verification record. None of them are fail-closed.

---

## 2. The Insight

### 2.1 Trust Is the Wrong Model

Zero trust security rejected perimeter-based trust models. The insight was simple: don't try to make the network trustworthy. Make trust irrelevant by verifying every request.

The same insight applies to AI.

Don't try to make AI trustworthy. Make AI's trustworthiness irrelevant by verifying every output.

### 2.2 Verification Must Be Deterministic

A probabilistic verification system is not verification — it is another layer of uncertainty. ZTI requires that all verification steps be deterministic: same input, same registry, same output, every time.

This is the property that makes verification meaningful. A system that might catch tampering is not a tamper-evident system.

### 2.3 Verification Must Be Fail-Closed

If the system cannot verify an output, it rejects the output. No partial acceptance. No fallback to unverified outputs. No silent degradation.

---

## 3. Core Principle

> **No AI output is trusted without verification.**

This is an architectural constraint, not a guideline. Every component in a ZTI system is designed around this constraint. The constraint does not have exceptions for performance, latency, or confidence.

---

## 4. Architecture

```
Registry → Detection → Explainability → Validation → Integrity → Lineage
```

### 4.1 Registry

The registry is the ground truth of the verification system. It contains:

- A closed, versioned set of valid patterns
- Detection rules for each pattern
- Scoring weights for confidence derivation
- Required conditions that must be satisfied

The registry is immutable at runtime. It is versioned. Every downstream component references the same registry version. Version mismatches are a hard failure.

### 4.2 Detection

Detection matches an AI output against the registry. It is:

- **Deterministic** — same input produces the same detection result
- **Evidence-bound** — every detection is tied to specific input signals and source references
- **Fail-closed** — if detection cannot complete, the output is rejected

Confidence is computed from registry scoring weights, not from the AI model. The AI model's internal confidence is not consulted.

### 4.3 Explainability

Every detected pattern produces an explanation artifact. The artifact contains:

- The pattern detected
- The signals that contributed to the detection
- Evidence references (interaction IDs and source positions)
- The registry version under which detection occurred

Explanation artifacts are the audit trail. They are produced before validation and retained regardless of what follows.

### 4.4 Validation

Validation performs cross-layer integrity checks:

- Detected patterns exist in the registry
- Pattern types match registry definitions
- Evidence references are internally consistent
- Version alignment holds across all layers

Validation is all-or-nothing. Partial validation is not validation.

### 4.5 Integrity

The integrity layer records every verified decision into a hash-chained, tamper-evident log.

Each record contains:

- A unique decision ID
- A UTC nanosecond timestamp
- SHA-256 hash of the decision payload
- SHA-256 hash of the previous record (GENESIS_HASH for first)
- A chain hash binding all fields

The chain enforces:

- **Strict monotonic timestamps** — no record can be backdated
- **Hash linkage** — any insertion, deletion, or modification is detectable
- **Genesis binding** — the chain start is explicitly marked

Any tampering with any record invalidates the entire chain from that point forward.

### 4.6 Lineage

The lineage layer records who approved or rejected each verified decision, when, and in what order.

Each lineage entry contains:

- A unique entry ID
- The ID of the decision record being approved
- The approver's identity
- The approval action (approve or reject)
- A UTC nanosecond timestamp
- A SHA-256 hash binding all fields

The lineage layer is stateless. It does not chain entries to each other. Instead, each entry is independently tamper-evident: any modification to the entry_id, decision_record_id, approver_id, approval_action, or timestamp is immediately detectable by recomputing the entry_hash.

Sequences of lineage entries are validated for:

- **Non-empty input** — an empty approval log is an unverified decision
- **Field validity** — all required fields present and well-formed
- **Monotonic timestamps** — approval events cannot be backdated relative to each other
- **Hash integrity** — each entry's hash is independently recomputable

---

## 5. Design Principles

### 5.1 Fail Closed

If verification cannot complete, the output is rejected. This applies at every layer. There is no partial success state.

### 5.2 No Implicit Trust

No component trusts any other component by default. The registry validates its own structure at load time. The detection layer validates the registry before running. The explainability layer validates detected patterns before generating artifacts. The integrity layer validates each record before appending. The lineage layer validates each entry independently.

### 5.3 Determinism

Every operation is deterministic. Sorting is explicit. Hash inputs are field-separated to prevent boundary collisions. Floating point arithmetic is bounded and validated before use.

### 5.4 Evidence Binding

No result exists without evidence. Every detected pattern references the specific inputs that produced it. Every explanation artifact references specific evidence. Every integrity record references the specific payload it covers. Every lineage entry references the specific decision record it approves.

### 5.5 Versioned, Closed Registry

The registry is closed. Unknown patterns cannot be inferred. Unknown signals are not accepted. The version string is a hard constraint at every layer. Mismatches fail the chain.

### 5.6 Stateless Protocol

ZTI defines the verification rules. It does not define where or when they are applied. The integrity chain and lineage entries are the only stateful artifacts, and their statefulness is explicit and append-only. Callers manage storage.

---

## 6. The Timestamp Analogy

In 1991, Haber and Stornetta published a scheme for timestamping digital documents so that it would be impossible to backdate or forward-date them. The insight: link each document's hash to the previous document's hash and publish the chain. Tampering with any document invalidates all subsequent entries.

ZTI's integrity layer applies the same principle to AI decisions.

Each decision is hashed. Each hash is linked to the previous. The chain is published (to any store — file, database, or log). Any attempt to modify, insert, or delete a decision is detectable by recomputing the chain.

The analogy is structural, not cryptographic in the blockchain sense. ZTI does not require distributed consensus. It requires only that the chain be recomputable from its inputs — which it always is, because it is deterministic.

---

## 7. Use Cases

### 7.1 Enterprise AI Governance

Organizations deploying AI in regulated environments need deterministic audit trails. ZTI provides a complete record of every AI output that was verified, the patterns detected, the signals that triggered detection, the registry version under which verification occurred, and the approval events that followed.

### 7.2 GRC and Compliance

Governance, Risk, and Compliance frameworks require that AI decisions be explainable and auditable. ZTI's explanation artifacts satisfy these requirements structurally — they are produced by the protocol, not retrofitted after the fact. The lineage layer adds a tamper-evident record of who reviewed each decision and what action they took.

### 7.3 Agentic Systems

AI agents that take autonomous actions are high-risk without verification. ZTI can be applied at the action boundary: any action proposed by an agent passes through the verification chain before execution. Agents that produce unverifiable output are stopped. Approval lineage provides a traceable record of human oversight.

### 7.4 Multi-Model Pipelines

In systems where multiple AI models interact, ZTI provides a verification layer between models. The output of one model is not passed to another until it has been verified. Trust does not accumulate across the pipeline.

### 7.5 Adversarial Detection

The integrity chain provides a tamper-evident record of all decisions. Any attempt to retroactively modify, inject, or delete a decision is detectable by chain validation. The lineage layer extends this to approval events: any attempt to forge or backdate an approval is detectable by hash recomputation.

---

## 8. What ZTI Is Not

ZTI is not:

- A model training framework
- A prompt engineering system
- A guardrail or content filter
- An orchestration engine
- A storage system
- An identity or authentication protocol

ZTI is a **verification protocol**. It defines how to verify AI outputs. It does not define what to do with the outputs after verification, how to store the integrity chain, or how to route decisions within a larger system.

---

## 9. Future Direction

### 9.1 Domain Pattern Libraries

Pattern registries can be domain-specific. Legal AI systems need legal patterns. Financial AI systems need financial patterns. ZTI's versioned registry model supports domain-specific libraries with shared verification infrastructure.

### 9.2 Registry Governance

As ZTI matures, formal governance models for registry updates become necessary. Who can update the registry? Under what conditions? With what audit trail? These are open questions the protocol does not yet answer.

### 9.3 Real-Time Verification

Current ZTI implementations operate post-inference. Future work may explore verification closer to inference time — applying registry checks before output leaves the model boundary.

### 9.4 Federated Integrity

In distributed systems, the integrity chain can be federated — multiple independent verification nodes that must agree before a decision is accepted. This extends ZTI's fail-closed model to the verification infrastructure itself.

### 9.5 Lineage Resolution

Future work will define deterministic ordering rules for approval lineage in systems where multiple reviewers act concurrently, and admissibility rules for partial or conflicting approval sequences.

---

## 10. Conclusion

AI is not going to become trustworthy through calibration alone. The probabilistic nature of the technology means that no amount of fine-tuning eliminates the possibility of error. The correct response is not to improve the AI until it is trustworthy. The correct response is to build systems that verify AI outputs deterministically, record them immutably, track approval lineage cryptographically, and fail closed when verification cannot be completed.

ZTI is that system.

The protocol is minimal. The implementation is complete. The principle is absolute.

Don't trust AI. Verify it.

---

*Zero Trust Intelligence (ZTI)*  
*Author: Chad McCormack — © 2026 Chad McCormack*  
*Released under MIT License. Implement freely.*
