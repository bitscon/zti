# Product Boundaries

*What belongs in the ZTI doctrine repository — and what does not*

---

## Purpose

This document exists to prevent the `bitscon/zti` repository from accumulating content
that belongs elsewhere. The ZTI repo is the doctrine and reference library home. It is not
a product repo, a site repo, or a marketing repo.

---

## What Belongs in This Repository

**ZTI doctrine documents:**
- `DOCTRINE.md` — the governing philosophy of Zero Trust Intelligence
- `PROTOCOL_FAMILY.md` — the ZTI ecosystem overview
- `PRODUCT_BOUNDARIES.md` — this document
- `whitepaper/zti-whitepaper.md` — the foundational ZTI whitepaper
- `README.md` — ecosystem landing page

**ZTI verification primitives (open-source reference library):**
- `zti/` — the Python reference implementation of the ZTI verification pipeline
- `examples/` — usage examples for the `zti` library
- `tests/` — test suite for the `zti` library

**ZTI decision-level schemas:**
- `schemas/audit_report.json` — ZTI audit report schema
- `schemas/verification_trace.json` — ZTI verification trace schema

**Supporting doctrine materials:**
- `resources/principles/` — boundary and principle definitions

---

## What Does Not Belong in This Repository

**ZTAP protocol files:**
ZTAP has its own repository: [github.com/bitscon/ztap](https://github.com/bitscon/ztap).
The ZTAP spec, schema, conformance docs, examples, and machine-readable schemas belong there.
Do not copy ZTAP files here. Do not make this repo a mirror of ZTAP content.

**ZTI Core SaaS code:**
ZTI Core is a commercial control-plane product. Its implementation code, API, configuration,
and private roadmap do not belong here. ZTI Core may reference this repo (for doctrine and the
open library), but this repo does not reference ZTI Core's implementation.

**Adoption site frontend:**
The public education and marketing site lives in `bitscon/zti-adoption`. Landing page source,
marketing copy, CSS, JavaScript, and assets belong there.

**Marketing and outreach materials:**
Launch posts, social media copy, enterprise outreach messages, pitch decks, and one-liners
belong in `bitscon/zti-adoption` or the operator's personal notes. They are not protocol
content.

**Billy runtime code:**
The `billy-runtime` system is a separate, unrelated project. It is not a protocol authority,
not a ZTI dependency, and not part of this repository. This repository must be fully operable
without Billy runtime being present.

**Private commercial details:**
Pricing, seat models, customer information, NDA'd documentation, or any material that should
not be public does not belong here. This repository is public and MIT-licensed.

---

## The Boundary in One Sentence

This repository contains the **doctrine** and the **open reference implementation**.

Everything else belongs somewhere else.

---

## How to Decide

When adding content to this repository, ask:

1. Is this ZTI doctrine? (principles, philosophy, threat model, verification pipeline definition)
   → Yes: it belongs here.

2. Is this an open-source reference implementation of ZTI verification primitives?
   → Yes: it belongs here.

3. Is this ZTAP protocol content?
   → No. Use `bitscon/ztap`.

4. Is this ZTI Core product code or commercial content?
   → No. Use the private `bitscon/zticore` repository.

5. Is this marketing, adoption, or public education content?
   → No. Use `bitscon/zti-adoption`.

6. Is this Billy runtime content?
   → No. Keep in the Billy workspace.

7. Is this private, commercial, or sensitive?
   → No. This repo is public.

---

*For the full ecosystem overview, see [PROTOCOL_FAMILY.md](PROTOCOL_FAMILY.md).*
*For the ZTI doctrine statement, see [DOCTRINE.md](DOCTRINE.md).*
