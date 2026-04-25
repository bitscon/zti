from __future__ import annotations

from dataclasses import dataclass

DIVIDER = "────────────────────────────────────────────"


@dataclass(frozen=True)
class SessionEvent:
    id: str
    kind: str
    text: str
    pause_after_seconds: float
    marker: str | None = None


@dataclass(frozen=True)
class SectionStep:
    kind: str  # event | narration | note
    ref: str | None = None
    lines: tuple[str, ...] = ()


@dataclass(frozen=True)
class SectionMetadata:
    key: str
    heading: str
    steps: tuple[SectionStep, ...]


DELIVERY_NOTES: tuple[str, ...] = (
    "Dark terminal theme",
    "Large readable font",
    "No typos",
    "Clean scroll",
    "Cursor visible but not distracting",
    "Practice once — record second take",
    "Pause after the first REJECTED",
    "Pause after the WITHOUT ZTI / WITH ZTI comparison",
    "Pause after the audit output",
)

PSYCHOLOGICAL_PAYLOAD: tuple[str, ...] = (
    "This happens",
    "We would not catch this",
    "ZTI does",
    "ZTI proves it",
    "We need this",
)

CRITICAL_WARNINGS: tuple[str, ...] = (
    "Do not speed this up",
    "Do not over-explain anything",
    "Do not add extra commentary",
    "The power of this demo is controlled silence plus obvious outcomes",
)


SCENARIO_1_OUTPUT = "\n".join(
    (
        DIVIDER,
        "ZTI DEMO — INFRASTRUCTURE VERIFICATION",
        "SCENARIO: prod-us-east-migration-override",
        "SESSION: infra-2026-04-09-001",
        DIVIDER,
        "RISK: Deployment to unapproved region",
        "IMPACT: Data sovereignty violation + compliance breach",
        "LIKELIHOOD: High (common pipeline misconfiguration)",
        "→ Proposal received",
        "→ Classification: infrastructure.deployment.ec2",
        "→ Explainability generated",
        "  - module: terraform-aws-ec2-instance",
        "  - region: eu-central-1",
        "  - instance_count: 3",
        "",
        "→ Validation",
        "  ✖ region.not_in_approved_set",
        "",
        "DECISION: REJECTED",
        "CONFIDENCE: VERIFIED",
        "CONTROL: Execution blocked at verification boundary",
    )
)

SCENARIO_2_OUTPUT = "\n".join(
    (
        DIVIDER,
        "ZTI DEMO — INFRASTRUCTURE VERIFICATION",
        "SCENARIO: prod-policy-near-miss",
        "SESSION: infra-2026-04-09-002",
        DIVIDER,
        "RISK: Unauthorized production deployment",
        "IMPACT: Untracked infrastructure drift",
        "LIKELIHOOD: Medium-High",
        "",
        "→ Proposal received",
        "→ Classification: infrastructure.deployment.ec2",
        "→ Explainability generated",
        "  - module: terraform-aws-ec2-instance",
        "  - region: us-east-1",
        "  - instance_count: 2",
        "  - instance_type: m5.xlarge",
        "",
        "→ Validation",
        "  ✔ region.approved",
        "  ✔ module.approved",
        "  ✔ instance_type.approved",
        "  ✔ instance_count.within_limit",
        "",
        "→ Lineage verification",
        "  ✖ approval.invalid_scope",
        "",
        "WITHOUT ZTI: PASSED",
        "WITH ZTI: BLOCKED (approval.invalid_scope)",
        "",
        "DECISION: REJECTED",
        "CONFIDENCE: VERIFIED",
        "CONTROL: Execution blocked at verification boundary",
    )
)

SCENARIO_3_OUTPUT = "\n".join(
    (
        DIVIDER,
        "ZTI DEMO — INFRASTRUCTURE VERIFICATION",
        "SCENARIO: prod-capacity-approved",
        "SESSION: infra-2026-04-09-003",
        DIVIDER,
        "RISK: Controlled infrastructure deployment",
        "IMPACT: Verified, auditable execution",
        "LIKELIHOOD: Approved",
        "",
        "→ Proposal received",
        "→ Classification: infrastructure.deployment.ec2",
        "→ Explainability generated",
        "→ Validation",
        "  ✔ all constraints passed",
        "",
        "→ Integrity check",
        "  ✔ artifact sealed",
        "",
        "→ Lineage recorded",
        "  ✔ approval chain verified",
        "",
        "DECISION: APPROVED",
        "CONFIDENCE: VERIFIED",
        "",
        "→ Execution",
        "  ✔ sandbox executor accepted verified artifact",
        "",
        "CONTROL: Only verified artifacts allowed to execute",
    )
)

AUDIT_OUTPUT = "\n".join(
    (
        DIVIDER,
        "ZTI AUDIT REPORT",
        "SESSION: infra-2026-04-09-003",
        DIVIDER,
        "What was proposed:",
        "- EC2 deployment (Terraform)",
        "",
        "What was blocked:",
        "- Region violation (Session 001)",
        "- Invalid approval chain (Session 002)",
        "",
        "What was executed:",
        "- Verified, policy-compliant artifact only",
        "",
        "Who approved:",
        "- Authorized identity (production scope)",
        "",
        "Chain integrity: VALID",
        "Lineage integrity: VALID",
        "",
        "AUDIT READINESS:",
        "This execution is fully reconstructable and provable",
        "",
        "CONTROL GUARANTEE:",
        "No unverified decision reached execution",
    )
)

CTA_OUTPUT = "\n".join(
    (
        DIVIDER,
        "STATUS: Your current systems operate on trust — not verification",
        "",
        "ZTI CORE:",
        "- Enforces verification at execution time",
        "- Produces audit-ready lineage automatically",
        "- Eliminates trust-based infrastructure risk",
        "",
        "NEXT STEP:",
        "Request access to deploy ZTI Core in your environment",
        DIVIDER,
    )
)

SESSION: tuple[SessionEvent, ...] = (
    SessionEvent(
        id="reset.command",
        kind="command",
        text="zti-demo reset --profile recording",
        pause_after_seconds=0.8,
        marker="reset",
    ),
    SessionEvent(
        id="scenario1.command",
        kind="command",
        text="zti-demo run prod-us-east-migration-override --explain",
        pause_after_seconds=0.8,
        marker="scenario1",
    ),
    SessionEvent(
        id="scenario1.output",
        kind="output",
        text=SCENARIO_1_OUTPUT,
        pause_after_seconds=0.0,
        marker="FIRST_REJECTION",
    ),
    SessionEvent(
        id="pause.first_rejection",
        kind="pause",
        text="",
        pause_after_seconds=2.5,
        marker="FIRST_REJECTION",
    ),
    SessionEvent(
        id="scenario2.command",
        kind="command",
        text="zti-demo run prod-policy-near-miss --explain",
        pause_after_seconds=0.8,
        marker="scenario2",
    ),
    SessionEvent(
        id="scenario2.output",
        kind="output",
        text=SCENARIO_2_OUTPUT,
        pause_after_seconds=0.0,
        marker="COMPARISON_BLOCK",
    ),
    SessionEvent(
        id="pause.comparison_block",
        kind="pause",
        text="",
        pause_after_seconds=2.0,
        marker="COMPARISON_BLOCK",
    ),
    SessionEvent(
        id="scenario3.command",
        kind="command",
        text="zti-demo run prod-capacity-approved --explain",
        pause_after_seconds=0.8,
        marker="scenario3",
    ),
    SessionEvent(
        id="scenario3.output",
        kind="output",
        text=SCENARIO_3_OUTPUT,
        pause_after_seconds=0.0,
        marker="scenario3",
    ),
    SessionEvent(
        id="audit.command",
        kind="command",
        text="zti-demo audit infra-2026-04-09-003",
        pause_after_seconds=0.8,
        marker="audit",
    ),
    SessionEvent(
        id="audit.output",
        kind="output",
        text=AUDIT_OUTPUT,
        pause_after_seconds=0.0,
        marker="AUDIT_OUTPUT",
    ),
    SessionEvent(
        id="pause.audit_output",
        kind="pause",
        text="",
        pause_after_seconds=2.0,
        marker="AUDIT_OUTPUT",
    ),
    SessionEvent(
        id="cta.output",
        kind="output",
        text=CTA_OUTPUT,
        pause_after_seconds=2.0,
        marker="cta",
    ),
)

SECTIONS: tuple[SectionMetadata, ...] = (
    SectionMetadata(
        key="reset",
        heading="## 0. Reset (Pre-roll — not narrated)",
        steps=(
            SectionStep(kind="event", ref="reset.command"),
            SectionStep(kind="note", lines=("(No narration — clean slate, deterministic run)",)),
        ),
    ),
    SectionMetadata(
        key="scenario1",
        heading="## 1. Hook — THIS COULD HAPPEN HERE (~15 sec)",
        steps=(
            SectionStep(kind="event", ref="scenario1.command"),
            SectionStep(
                kind="narration",
                lines=(
                    "This is a standard infrastructure change.",
                    "Looks normal... nothing unusual.",
                ),
            ),
            SectionStep(kind="event", ref="scenario1.output"),
            SectionStep(kind="event", ref="pause.first_rejection"),
            SectionStep(
                kind="narration",
                lines=(
                    "ZTI doesn't trust the request.",
                    "It verifies it — before anything runs.",
                ),
            ),
        ),
    ),
    SectionMetadata(
        key="scenario2",
        heading="## 2. Escalation — THIS WOULD HAVE GOTTEN THROUGH (~25 sec)",
        steps=(
            SectionStep(kind="event", ref="scenario2.command"),
            SectionStep(
                kind="narration",
                lines=(
                    "Now let's look at something more realistic...",
                    "This one appears fully compliant.",
                ),
            ),
            SectionStep(kind="event", ref="scenario2.output"),
            SectionStep(
                kind="narration",
                lines=(
                    "Everything looks right...",
                    "this would pass most systems.",
                ),
            ),
            SectionStep(kind="event", ref="pause.comparison_block"),
            SectionStep(
                kind="narration",
                lines=("But the approval chain is wrong.",),
            ),
        ),
    ),
    SectionMetadata(
        key="scenario3",
        heading="## 3. Resolution — ONLY VERIFIED EXECUTES (~20 sec)",
        steps=(
            SectionStep(kind="event", ref="scenario3.command"),
            SectionStep(
                kind="narration",
                lines=(
                    "Now — same type of change...",
                    "but fully verified.",
                ),
            ),
            SectionStep(kind="event", ref="scenario3.output"),
            SectionStep(
                kind="narration",
                lines=(
                    "ZTI doesn't block infrastructure...",
                    "it ensures only verified infrastructure runs.",
                ),
            ),
        ),
    ),
    SectionMetadata(
        key="audit",
        heading="## 4. Authority — THIS IS WHAT AUDITORS WANT (~20 sec)",
        steps=(
            SectionStep(kind="event", ref="audit.command"),
            SectionStep(kind="narration", lines=("Now — audit the execution.",)),
            SectionStep(kind="event", ref="audit.output"),
            SectionStep(kind="event", ref="pause.audit_output"),
            SectionStep(
                kind="narration",
                lines=(
                    "This is the difference between trusting a system...",
                    "and proving it.",
                ),
            ),
        ),
    ),
    SectionMetadata(
        key="cta",
        heading="## 5. Close — CTA (~10 sec)",
        steps=(
            SectionStep(kind="event", ref="cta.output"),
            SectionStep(
                kind="narration",
                lines=(
                    "ZTI doesn't trust AI or infrastructure decisions.",
                    "It proves them.",
                ),
            ),
        ),
    ),
)
