# ZTI Demo — Terminal Output

Generated from the deterministic demo compiler. Do not edit manually.
Terminal output is the only source of truth. All demo assets are generated from the canonical session model. Manual editing is forbidden.

```text
$ zti-demo reset --profile recording
$ zti-demo run prod-us-east-migration-override --explain
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
$ zti-demo run prod-policy-near-miss --explain
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
$ zti-demo run prod-capacity-approved --explain
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
$ zti-demo audit infra-2026-04-09-003
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
