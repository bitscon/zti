# ZTI Protocol Family

*The Zero Trust Intelligence Ecosystem*

---

## Overview

Zero Trust Intelligence (ZTI) is a doctrine and a family of related protocols and products.
This document defines the current ecosystem and the relationship between its components.

```text
ZTI (doctrine / umbrella)
  ├── ZTAP (open protocol — first protocol under ZTI)
  ├── ZTI Core (separate commercial/control-plane product)
  └── ZTI Adoption (public education and marketing site)
```

---

## ZTI — The Doctrine

**Repository:** this repository (`bitscon/zti` — formerly `bitscon/zerotrustintelligence`)

Zero Trust Intelligence is the governing philosophy for how AI-generated proposals should
relate to the deterministic systems that execute on them.

**Core principle:** Do not trust AI. Verify it. Models draft. Deterministic systems govern.

ZTI is not a product. It is a doctrine. It defines the principles that protocols, libraries,
and products implement.

For the full doctrine statement, see [DOCTRINE.md](DOCTRINE.md).

This repository contains:
- The ZTI doctrine documents
- The `zti` Python reference library (open-source verification primitives)
- ZTI decision-level schemas (`AuditReport`, `VerificationTrace`)
- The ZTI whitepaper (`whitepaper/zti-whitepaper.md`)
- Links to the protocol family

---

## ZTAP — Zero Trust Agent Protocol

**Repository:** [github.com/bitscon/ztap](https://github.com/bitscon/ztap)
**Current version:** `v1.0-draft`
**License:** MIT

ZTAP is the first open protocol under the ZTI doctrine. It defines how agent-initiated
actions — deployments, queries, code changes, governed API calls, and any other consequential
agent work — must be structured so they are:

- authorized by policy,
- verifiable by cryptographic hash, and
- auditable by any person or system that needs to inspect them.

ZTAP governs the **transaction layer** — the envelope, the authorization decision, the
execution receipt, the evidence, and the audit trail. It does not govern which tools, models,
or agent frameworks engineers use.

**Relationship to ZTI:**
- ZTI defines the doctrine: verify before execution; integrity and lineage required.
- ZTAP implements that doctrine at the agent transaction layer.
- A ZTAP transaction is a Verified Decision in ZTI terms, expressed as a structured JSON
  envelope with a hash-linked audit trail.

**Key positioning:**
> Code freedom, Verified.
> ZTAP does not secure the pipe. ZTAP governs the action.

For the full protocol specification, see the [ZTAP repository](https://github.com/bitscon/ztap).

---

## ZTI Core — Commercial Control Plane

**Status:** Separate commercial product. Not part of this repository.

ZTI Core is a commercial SaaS control-plane implementation of the ZTAP protocol and ZTI
governance principles. It is designed to provide:

- an actor and capability registry (register agents, assign roles and capabilities),
- policy authoring and enforcement,
- real-time ZTAP transaction evaluation and authorization,
- human approval workflows with bounded, auditable approval records,
- evidence collection and verification,
- an append-only, hash-linked audit log,
- and an administrative interface for operators.

**Relationship to ZTAP:**
ZTI Core is designed to implement ZTAP. It is not ZTAP. The ZTAP protocol specification at
`bitscon/ztap` is the open standard. ZTI Core is one commercial product that implements that
standard. Organizations may self-host their own ZTAP-compliant control plane instead of using
ZTI Core.

**Relationship to ZTI:**
ZTI Core is not part of the ZTI doctrine repository. It is a separate, commercial product.
The distinction is intentional: the doctrine and open protocol remain open regardless of
commercial implementations.

---

## ZTI Adoption — Public Education and Marketing Site

**Repository:** [github.com/bitscon/zti-adoption](https://github.com/bitscon/zti-adoption)
**Status:** Separate site repository.

The ZTI adoption site is the public-facing education and marketing surface for the ZTI
ecosystem. It contains:

- landing page and marketing materials,
- positioning narrative and educational content,
- links to ZTAP, ZTI Core, and this repository.

The adoption site does not define protocol standards. It is contextual and illustrative.
The authoritative definitions live in the doctrine and protocol repositories.

---

## What Each Component Owns

| Component | Owns | Does Not Own |
|---|---|---|
| ZTI (this repo) | Doctrine, principles, threat model, reference library, ZTI whitepaper | ZTAP protocol files, ZTI Core code, adoption site content |
| ZTAP | Transaction protocol spec, schema, conformance, examples | ZTI doctrine, ZTI Core implementation, marketing |
| ZTI Core | Commercial control-plane implementation | Protocol specification authority, open standard |
| ZTI Adoption | Public education, marketing, launch materials | Protocol standards, product code |

---

## Future Protocols

The ZTI doctrine is intended to be broad enough to support future protocols beyond ZTAP.
ZTAP governs agent-to-agent and agent-to-system transaction governance. Future protocols
under ZTI may address other layers of AI governance.

No future protocols are defined or committed to at this time. This section is included to
make clear that ZTAP is the first protocol under ZTI, not the only possible protocol.

---

*ZTI doctrine: [github.com/bitscon/zti](https://github.com/bitscon/zti)*
*(Note: pending rename from `bitscon/zerotrustintelligence`)*
*ZTAP open protocol: [github.com/bitscon/ztap](https://github.com/bitscon/ztap)*
