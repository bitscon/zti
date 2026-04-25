# ZTI Doctrine

*Zero Trust Intelligence — The Governing Philosophy*

Author: Chad McCormack
© 2026 Chad McCormack

---

## The Core Principle

**Do not trust AI. Verify it.**

AI systems produce outputs that appear intelligent. They are probabilistic, generative, and
often compelling. But a compelling output is not a verified decision. Confidence is not proof.
Capability is not authorization.

Zero Trust Intelligence (ZTI) is built on a single constraint:

**No decision is trusted unless it is proven.**

---

## What ZTI Is

Zero Trust Intelligence is a doctrine — a set of governing principles — for how AI-generated
proposals should relate to the deterministic systems that execute on them.

ZTI defines a new layer in the AI-to-execution stack:

```text
AI system           (stochastic generation layer)
         ↓
ZTI layer           (deterministic decision verification layer)
         ↓
Execution systems   (infrastructure, APIs, databases, agents)
```

This layer does not generate intelligence. It does not improve the AI. It enforces one rule:

**Only verified decisions are allowed to pass.**

---

## The Four Principles

### 1. Models draft. Deterministic systems govern.

An AI agent can propose a deployment, generate a plan, draft a code change, or recommend an
action. That proposal is not a decision. It is a candidate. The verification layer — not the
model's confidence — determines whether the proposal is admitted to execution.

### 2. Trust must be proven, not assumed.

An output from a trusted model, over a secure channel, from a well-known system, is not
authorized to act by any of those facts alone. Authorization comes from a verified record.
Trust that cannot be proven is not trust — it is assumption.

### 3. Every governed action must leave a verifiable record.

If an action cannot be audited — if there is no record of what was proposed, what was
verified, what was authorized, and what executed — then from a governance perspective it
cannot be governed. Governance requires evidence. Evidence requires records. Records require
integrity.

### 4. Verification must be deterministic and reproducible.

A verification result that cannot be reproduced is invalid. The AI generation process does not
need to be deterministic. The verification layer does. Same input, same policy, same result —
every time.

---

## What ZTI Is Not

**ZTI is not a product.** ZTI is a doctrine. Products and protocols can implement ZTI
principles. The doctrine itself is not a product.

**ZTI is not ZTAP.** ZTAP (Zero Trust Agent Protocol) is the first open protocol under the
ZTI doctrine. ZTAP defines how agent-to-agent transactions must be structured to be
authorized, verifiable, and auditable. ZTAP implements ZTI principles at the agent transaction
layer. But ZTI is broader than ZTAP.

**ZTI is not ZTI Core.** ZTI Core is a separate commercial/control-plane product designed to
implement ZTI principles and the ZTAP protocol. ZTI Core is not part of this repository.

**ZTI does not improve AI.** ZTI does not constrain how an AI reasons or what it generates.
It constrains whether the output of that reasoning is admitted to execution.

**ZTI does not eliminate risk.** ZTI constrains where risk is allowed to materialize. Policy
quality matters. Implementation quality matters. ZTI enforces what you declare — it does not
audit the integrity of your policy definitions.

---

## The Decision Boundary

The single most important concept in ZTI doctrine is the decision boundary.

Every AI-to-execution pathway has a point where a proposal becomes an action. That boundary
is the highest-risk surface in AI-driven systems. It is where an incorrect, unauthorized, or
unverified AI output can cause real consequences.

ZTI governs that boundary. It requires that nothing crosses from proposal to execution without
a deterministic verification record that proves:

- the proposal was mapped to an allowed decision class,
- the proposal satisfied declared constraints,
- the proposal was sealed with a tamper-evident integrity record,
- the history of that proposal — where it came from, who approved it — is traceable.

If any of these conditions are absent: **the decision does not exist. It does not execute.**

---

## The Verified Decision

ZTI introduces a formal artifact: the **Verified Decision**.

A Verified Decision is:
- **Derived** — it was produced from a specific proposal
- **Explained** — the reasoning for its admission is recorded
- **Validated** — it satisfied the declared policy constraints
- **Sealed** — it is cryptographically tamper-evident
- **Traceable** — its provenance and approval chain are auditable

A Verified Decision is not proof that the AI was right. It is proof that the proposal
satisfied the execution contract.

Only Verified Decisions are allowed to cross from generation into execution.

---

## Threat Model

ZTI is a security control with a defined scope.

**ZTI governs against:**
- Unauthorized execution of AI-generated actions — unverified proposals reaching execution
- Policy violations — proposals that do not satisfy declared constraints
- Tampered decision records — modification of sealed artifacts

**ZTI does not govern against:**
- Compromised AI models — a poisoned model can still produce outputs that satisfy valid policy
- Incorrect policy definitions — ZTI enforces what is declared; policy authorship is out of scope
- Malicious policy authors — ZTI does not audit who wrote the policy

---

## ZTI and the Agent Ecosystem

ZTI doctrine applies wherever AI-generated proposals drive consequential execution:

- Infrastructure automation (Terraform, Kubernetes, cloud provisioning)
- Security enforcement (access decisions, policy gates)
- Financial systems (trade execution, transaction authorization)
- Agent-to-agent handoffs (multi-agent pipelines)
- Compliance and audit pipelines

For agent-to-agent transactions specifically, **ZTAP** defines the protocol that implements
ZTI governance at that layer.

```text
ZTI doctrine
  └── ZTAP open protocol      ← first open protocol under ZTI
        └── ZTI Core          ← one commercial control-plane implementation
```

---

## Relationship to Zero Trust Security

Zero Trust Security (ZTS) establishes that network position is not a basis for trust.
Every request must be authenticated and authorized, regardless of where it originates.

ZTI extends this principle from network-level requests to AI-generated decisions:

**Network position is not a basis for trust in ZTS.**
**Model confidence is not a basis for trust in ZTI.**

Both demand proof. Both are fail-closed. Both require explicit verification at every boundary.

---

*ZTI doctrine is maintained in this repository.*
*The first open protocol under ZTI doctrine is [ZTAP](https://github.com/bitscon/ztap).*
*For the protocol family and ecosystem overview, see [PROTOCOL_FAMILY.md](PROTOCOL_FAMILY.md).*
