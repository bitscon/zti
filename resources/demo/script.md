# ZTI Demo Script

Generated from the `zti-demo` recording runtime. Do not edit manually.
Terminal output is the only source of truth. All demo assets are generated from runtime output. Manual editing is forbidden.

Goal: ~75–90 seconds total  
Tone: Calm, controlled, confident  
Pacing: Slight pauses between sections (let it breathe)

## 0. Reset (Pre-roll — not narrated)
```bash
$ zti-demo reset --profile recording
```

(No narration — clean slate, deterministic run)

## 1. Hook — THIS COULD HAPPEN HERE (~15 sec)
```bash
$ zti-demo run prod-us-east-migration-override --explain
```

Narration:
> "This is a standard infrastructure change.
> Looks normal... nothing unusual."

```text
────────────────────────────────────────────
ZTI DEMO — INFRASTRUCTURE VERIFICATION
SCENARIO: prod-us-east-migration-override
SESSION: infra-2026-04-09-001
────────────────────────────────────────────

RISK: Deployment to unapproved region
IMPACT: Data sovereignty violation + compliance breach
LIKELIHOOD: High (common pipeline misconfiguration)

→ Proposal received
→ Classification: infrastructure.deployment.ec2

→ Explainability generated
  - module: terraform-aws-ec2-instance
  - region: eu-central-1
  - instance_count: 3

→ Validation
  ✖ region.not_in_approved_set

DECISION: REJECTED
CONFIDENCE: VERIFIED
CONTROL: Execution blocked at verification boundary
```

Narration:
> "ZTI doesn't trust the request.
> It verifies it — before anything runs."

## 2. Escalation — THIS WOULD HAVE GOTTEN THROUGH (~25 sec)
```bash
$ zti-demo run prod-policy-near-miss --explain
```

Narration:
> "Now let's look at something more realistic...
> This one appears fully compliant."

```text
────────────────────────────────────────────
ZTI DEMO — INFRASTRUCTURE VERIFICATION
SCENARIO: prod-policy-near-miss
SESSION: infra-2026-04-09-002
────────────────────────────────────────────

RISK: Unauthorized production deployment
IMPACT: Untracked infrastructure drift
LIKELIHOOD: Medium-High

→ Proposal received
→ Classification: infrastructure.deployment.ec2

→ Explainability generated
  - module: terraform-aws-ec2-instance
  - region: us-east-1
  - instance_count: 2
  - instance_type: m5.xlarge

→ Validation
  ✔ region.approved
  ✔ module.approved
  ✔ instance_type.approved
  ✔ instance_count.within_limit

→ Lineage verification
  ✖ approval.invalid_scope

WITHOUT ZTI: PASSED
WITH ZTI: BLOCKED (approval.invalid_scope)

DECISION: REJECTED
CONFIDENCE: VERIFIED
CONTROL: Execution blocked at verification boundary
```

Narration:
> "Everything looks right...
> this would pass most systems."

(pause)

Narration:
> "But the approval chain is wrong."

## 3. Resolution — ONLY VERIFIED EXECUTES (~20 sec)
```bash
$ zti-demo run prod-capacity-approved --explain
```

Narration:
> "Now — same type of change...
> but fully verified."

```text
────────────────────────────────────────────
ZTI DEMO — INFRASTRUCTURE VERIFICATION
SCENARIO: prod-capacity-approved
SESSION: infra-2026-04-09-003
────────────────────────────────────────────

RISK: Controlled infrastructure deployment
IMPACT: Verified, auditable execution
LIKELIHOOD: Approved

→ Proposal received
→ Classification: infrastructure.deployment.ec2

→ Explainability generated
→ Validation
  ✔ all constraints passed

→ Integrity check
  ✔ artifact sealed

→ Lineage recorded
  ✔ approval chain verified

DECISION: APPROVED
CONFIDENCE: VERIFIED

→ Execution
  ✔ sandbox executor accepted verified artifact

CONTROL: Only verified artifacts allowed to execute
```

Narration:
> "ZTI doesn't block infrastructure...
> it ensures only verified infrastructure runs."

## 4. Authority — THIS IS WHAT AUDITORS WANT (~20 sec)
```bash
$ zti-demo audit infra-2026-04-09-003
```

Narration:
> "Now — audit the execution."

```text
────────────────────────────────────────────
ZTI AUDIT REPORT
SESSION: infra-2026-04-09-003
────────────────────────────────────────────

What was proposed:
- EC2 deployment (Terraform)

What was blocked:
- Region violation (Session 001)
- Invalid approval chain (Session 002)

What was executed:
- Verified, policy-compliant artifact only

Who approved:
- Authorized identity (production scope)

Chain integrity: VALID
Lineage integrity: VALID

AUDIT READINESS:
This execution is fully reconstructable and provable

CONTROL GUARANTEE:
No unverified decision reached execution
```

Narration:
> "This is the difference between trusting a system...
> and proving it."

## 5. Close — CTA (~10 sec)
```text
────────────────────────────────────────────
STATUS: Your current systems operate on trust — not verification

ZTI CORE:
- Enforces verification at execution time
- Produces audit-ready lineage automatically
- Eliminates trust-based infrastructure risk

NEXT STEP:
Request access to deploy ZTI Core in your environment
────────────────────────────────────────────
```

Narration:
> "ZTI doesn't trust AI or infrastructure decisions.
> It proves them."
