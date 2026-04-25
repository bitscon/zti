# ZTI Repo Audit

*Prepared in advance of renaming `bitscon/zerotrustintelligence` → `bitscon/zti`*

---

## Purpose

This audit prepares the `zerotrustintelligence` repository to become the clean
`bitscon/zti` parent/doctrine repo. It classifies every area of the current repo,
identifies what belongs where, and defines what must be added or revised before
the rename is safe.

---

## Current Repo Summary

`bitscon/zerotrustintelligence` is a mixed-purpose repository. It currently contains:

1. **ZTI doctrine content** — the whitepaper, README doctrine sections, and principles. This is strong, well-written material that belongs in `bitscon/zti`.

2. **A reference Python library (`zti/`)** — a deterministic verification primitive library implementing the ZTI pipeline: Pattern Registry → Detection → Explainability → Validation → Integrity → Lineage. This is open-source, doctrine-level code. It belongs in `bitscon/zti`.

3. **ZTI decision verification schemas (`schemas/`)** — two JSON Schema files defining `AuditReport` and `VerificationTrace` at the ZTI decision level. These are distinct from ZTAP envelope schemas. They belong in `bitscon/zti` under a clearly-named path.

4. **Site infrastructure (`dev/`, `ops/`)** — demo recording scripts, site build tooling, deployment scripts. The adoption site has been migrated to `bitscon/zti-adoption`. This infrastructure is stale in this repo.

5. **Marketing and outreach content (`marketing/`, `resources/outreach/`, `resources/deck/`)** — launch posts, enterprise outreach messages, slide decks, one-liners. These belong in `bitscon/zti-adoption` or the operator's personal notes, not in the doctrine repo.

6. **Demo materials (`resources/demo/`, `zti/demo/`)** — recording scripts, session models, terminal output examples. The library demo (`zti/demo/`) belongs here as part of the reference implementation. The recording/production infrastructure belongs in `ops/` at most, or archived.

7. **Resources/principles (`resources/principles/`)** — boundary principles document, a useful doctrine artifact. Belongs in `bitscon/zti`.

8. **Old repo URL references** — `https://github.com/bitscon/zerotrustintelligence` appears in README.md install instructions and in `resources/principles/boundary.md`. These must be updated to `bitscon/zti` after the rename.

The repo does **not** currently reference ZTAP, ZTI Core, or Billy in any doctrine document. This is good — no cross-contamination to undo. The README and whitepaper are ZTAP-unaware, written before ZTAP existed as a named protocol.

---

## Content Classification

| Path | Current Purpose | Recommended Destination | Action |
|---|---|---|---|
| `README.md` | Mixed: doctrine + Python install guide + site build guide | keep in ZTI | Revise to be ecosystem landing page; remove site-build instructions; add ZTAP and ecosystem links |
| `whitepaper/zti-whitepaper.md` | ZTI umbrella doctrine whitepaper | keep in ZTI | Keep as-is; it is pre-ZTAP but fully valid doctrine. Update to mention ZTAP as the first protocol. |
| `zti/` (Python package) | Reference implementation of ZTI verification pipeline | keep in ZTI | Keep. This is open-source doctrine-level library, not ZTI Core code. |
| `schemas/audit_report.json` | ZTI decision-level audit report schema | keep in ZTI | Keep. This is a ZTI decision schema, not a ZTAP envelope schema. |
| `schemas/verification_trace.json` | ZTI decision-level verification trace schema | keep in ZTI | Keep. Same — ZTI pipeline, not ZTAP. Update `$id` URL after rename. |
| `examples/` | Python usage examples for the `zti` library | keep in ZTI | Keep. These demonstrate the ZTI reference library. |
| `tests/` | Test suite for `zti` library | keep in ZTI | Keep. Standard test coverage for the reference library. |
| `resources/principles/boundary.md` | Doctrine-level boundary definition | keep in ZTI | Keep. Update old `bitscon/zerotrustintelligence` URL reference. |
| `resources/narrative/60-second-explainer.md` | ZTI positioning narrative | operator decision required | Could stay in ZTI as context doc or move to `zti-adoption`. Not harmful either way. |
| `resources/assets/architecture.md` | Architecture diagram/description | keep in ZTI | Keep as supporting doctrine material. |
| `resources/assets/visual-onepager.md` | Visual one-pager content | move to zti-adoption | Marketing material; belongs with adoption site. |
| `resources/deck/slides.md` | Presentation slides | move to zti-adoption | Marketing material. |
| `resources/demo/recording-script.md` | Demo recording script | archive | Operational, not doctrine. Archive or move to `ops/`. |
| `resources/demo/session_model.py` | Demo session model | keep in ZTI (or move to `zti/demo/`) | Part of the reference implementation demo. |
| `resources/demo/script.md` | Demo script | archive | Operational. |
| `resources/demo/terminal-output.md` | Demo terminal output | archive | Operational. |
| `resources/outreach/pilot.md` | Pilot program outreach | move to zti-adoption | Marketing. |
| `resources/outreach/posts.md` | Social media posts | move to zti-adoption | Marketing. |
| `resources/outreach/enterprise.md` | Enterprise outreach messages | move to zti-adoption | Marketing. References `bitscon/zerotrustintelligence` URL — must update before publication. |
| `marketing/` (top-level) | Launch posts, one-liners, checklist | move to zti-adoption or archive | Marketing/operator notes. Not doctrine. |
| `dev/` | Site source and build tooling | archive | Site has moved to `bitscon/zti-adoption`. Stale here. |
| `ops/` | Deploy, verify, demo recording scripts | archive | Operational tooling for the old site. No longer needed in doctrine repo. |
| `shared/` | (empty) | N/A | No action needed. |
| `AGENTS.md` | Agent operation contract for this repo | keep in ZTI | Keep; update old `zerotrustintelligence` URL reference after rename. |
| `PROJECT_STATUS.md` | Project status checkpoint | keep in ZTI | Keep as internal status doc. Update URL after rename. |
| `pyproject.toml` | Python package config | keep in ZTI | Update package URL after rename. |

**New files to create (this pass):**
- `DOCTRINE.md` — ZTI doctrine statement
- `PROTOCOL_FAMILY.md` — Ecosystem index (ZTI, ZTAP, ZTI Core, adoption)
- `PRODUCT_BOUNDARIES.md` — What belongs where

---

## Schema Classification

| Schema File | Type | Classification | Action |
|---|---|---|---|
| `schemas/audit_report.json` | ZTI decision-level audit report | **ZTI decision schema** — distinct from ZTAP | Keep in `bitscon/zti`. Update `$id` URL from `bitscon.github.io/zerotrustintelligence/` to `bitscon.github.io/zti/` after rename. |
| `schemas/verification_trace.json` | ZTI verification pipeline trace | **ZTI decision schema** — distinct from ZTAP | Same. Keep and update URL. |

**Important distinction:** These schemas define the ZTI decision verification artifact structure (`AuditReport`, `VerificationTrace`) — they capture what was proposed, what was blocked, what was validated, what was sealed. They are not ZTAP envelope schemas (transaction_request, authorization_decision, execution_receipt, etc.). They operate at a different conceptual layer and belong in different repos. No deduplication or merging with ZTAP schemas is needed.

---

## Python Package Classification

The `zti/` Python package is the **reference implementation of the ZTI verification doctrine**. It implements:

- **Pattern Registry** — defines allowed decision classes and constraints
- **Detection** — deterministic classification of proposals
- **Explainability** — produces explicit evidence artifacts
- **Validation** — enforces admissibility against declared constraints
- **Integrity** — cryptographic sealing and chain validation
- **Lineage** — provenance and approval tracking
- **Serialization** — artifact serialization
- **Demo** — demonstration of the pipeline

This library is **not** ZTI Core. ZTI Core is a commercial SaaS control plane. This library is an open-source reference implementation of the verification primitives described in the whitepaper. Anyone can import it and use it as the basis for their own ZTI-compliant verification layer.

**Recommendation:** Keep in `bitscon/zti`. It is valuable, relevant, and doctrine-consistent. It should be described in the README as a reference implementation, not a production-ready product.

---

## Risky / Confusing Content

| Issue | Location | Risk | Action |
|---|---|---|---|
| Old repo URL (`bitscon/zerotrustintelligence`) | README.md (install section), `resources/principles/boundary.md`, `resources/outreach/enterprise.md`, `resources/outreach/posts.md` | After rename, install instructions will point to wrong URL | Update all occurrences to `bitscon/zti` after rename |
| Schema `$id` values pointing to `bitscon.github.io/zerotrustintelligence/` | `schemas/audit_report.json`, `schemas/verification_trace.json` | Schema IDs will be stale after rename | Update after rename |
| README presents ZTI as primarily a Python library | README.md | Readers may think ZTI is a Python library rather than a doctrine/protocol. The library is *part of* ZTI, not the whole thing. | Revise README to lead with doctrine, position library as reference implementation |
| README includes site build instructions (`dev/site/build.py`, `./ops/verify.sh`) | README.md | Site lives in `zti-adoption` now; these instructions are stale and confusing | Remove from README |
| Marketing copy references `bitscon/zerotrustintelligence` | `resources/outreach/enterprise.md`, `resources/outreach/posts.md`, `marketing/` | Live outreach materials point to old URL | Update before external use |
| No ecosystem context | Entire repo | The repo has no mention of ZTAP as the first open protocol under ZTI. A reader has no way to connect ZTI doctrine to the ZTAP protocol. | Add `PROTOCOL_FAMILY.md` and update README/whitepaper |
| No product boundary statement | Entire repo | Nothing clearly separates ZTI (doctrine/library) from ZTI Core (commercial product). A reader might assume the Python library IS ZTI Core. | Add `PRODUCT_BOUNDARIES.md` |

---

## Recommended Cleanup Plan

**Phase 1 — Add doctrine docs (this pass, no file moves)**

1. Create `DOCTRINE.md` — canonical ZTI doctrine statement
2. Create `PROTOCOL_FAMILY.md` — ecosystem index linking to ZTAP, describing ZTI Core
3. Create `PRODUCT_BOUNDARIES.md` — boundary definition for the repo
4. Revise `README.md` — lead with doctrine, add ecosystem links, remove stale site-build instructions

**Phase 2 — Update stale URLs (after rename)**

5. Update `bitscon/zerotrustintelligence` → `bitscon/zti` in all files that reference it
6. Update schema `$id` URLs from `bitscon.github.io/zerotrustintelligence/` → `bitscon.github.io/zti/`
7. Update `pyproject.toml` package URL if it references the old name

**Phase 3 — Move/archive non-doctrine content (operator decision)**

8. Move `marketing/` → operator personal notes or `zti-adoption`
9. Move `resources/outreach/` → `zti-adoption` or operator notes
10. Move `resources/deck/` → `zti-adoption` or operator notes
11. Archive `dev/` and `ops/` (stale site infrastructure)
12. Review `resources/demo/` — keep `session_model.py` in library, archive production scripts

**Phase 4 — GitHub rename**

13. Operator: rename `bitscon/zerotrustintelligence` → `bitscon/zti` on GitHub
14. Codex: `git remote set-url origin https://github.com/bitscon/zti.git`
15. Commit and tag

---

## Rename Readiness

**Not yet ready to rename.**

The repo is not ready to rename for two reasons:

1. **Missing ecosystem context docs.** A reader arriving at `bitscon/zti` today would see a mixed Python library / site management repo with no mention of ZTAP. The doctrine docs (`DOCTRINE.md`, `PROTOCOL_FAMILY.md`, `PRODUCT_BOUNDARIES.md`) and the README revision must be in place first.

2. **Stale content still present.** Site-build instructions, marketing copy, and old URL references should be resolved or flagged before the renamed repo receives public attention.

Once Phase 1 is complete (this pass), the repo will be ready for rename. Phases 2 and 3 can follow after the rename.
