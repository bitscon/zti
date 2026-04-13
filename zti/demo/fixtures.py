from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ScenarioFixture:
    scenario_id: str
    session_id: str
    order: int
    risk: str
    impact: str
    likelihood: str
    cause: str
    classification: str
    provider: str
    module: str
    region: str
    instance_count: int
    instance_type: str
    approval_identity: str | None
    approval_scope: str | None
    required_scope: str
    pipeline_run_id: str
    commit_sha: str
    operator_id: str
    decision_timestamp_ns: int
    lineage_timestamp_ns: int | None


SCENARIOS: dict[str, ScenarioFixture] = {
    "prod-us-east-migration-override": ScenarioFixture(
        scenario_id="prod-us-east-migration-override",
        session_id="infra-2026-04-09-001",
        order=1,
        risk="Deployment to unapproved region",
        impact="Data sovereignty violation + compliance breach",
        likelihood="High (common pipeline misconfiguration)",
        cause="Auto-approved Terraform change bypassed region guardrails",
        classification="infrastructure.deployment.ec2",
        provider="aws",
        module="terraform-aws-ec2-instance",
        region="eu-central-1",
        instance_count=3,
        instance_type="m5.xlarge",
        approval_identity=None,
        approval_scope=None,
        required_scope="production",
        pipeline_run_id="pipe-prod-20260409-001",
        commit_sha="8f4a2c71",
        operator_id="devops-engineer-1",
        decision_timestamp_ns=1744214400000000001,
        lineage_timestamp_ns=None,
    ),
    "prod-policy-near-miss": ScenarioFixture(
        scenario_id="prod-policy-near-miss",
        session_id="infra-2026-04-09-002",
        order=2,
        risk="Unauthorized production deployment",
        impact="Untracked infrastructure drift",
        likelihood="Medium-High",
        cause="Approval chain appears valid but lacks production scope authorization",
        classification="infrastructure.deployment.ec2",
        provider="aws",
        module="terraform-aws-ec2-instance",
        region="us-east-1",
        instance_count=2,
        instance_type="m5.xlarge",
        approval_identity="release-manager@example.com",
        approval_scope="staging",
        required_scope="production",
        pipeline_run_id="pipe-prod-20260409-002",
        commit_sha="be9120af",
        operator_id="platform-bot-7",
        decision_timestamp_ns=1744214400000000002,
        lineage_timestamp_ns=1744214400000000102,
    ),
    "prod-capacity-approved": ScenarioFixture(
        scenario_id="prod-capacity-approved",
        session_id="infra-2026-04-09-003",
        order=3,
        risk="Controlled infrastructure deployment",
        impact="Verified, auditable execution",
        likelihood="Approved",
        cause="Verified identity and policy-compliant infrastructure change",
        classification="infrastructure.deployment.ec2",
        provider="aws",
        module="terraform-aws-ec2-instance",
        region="us-east-1",
        instance_count=2,
        instance_type="m5.xlarge",
        approval_identity="platform-lead@example.com",
        approval_scope="production",
        required_scope="production",
        pipeline_run_id="pipe-prod-20260409-003",
        commit_sha="5ac09de4",
        operator_id="platform-bot-7",
        decision_timestamp_ns=1744214400000000003,
        lineage_timestamp_ns=1744214400000000103,
    ),
}

SCENARIO_ORDER: tuple[str, ...] = tuple(
    scenario_id for scenario_id, _fixture in sorted(SCENARIOS.items(), key=lambda item: item[1].order)
)


def get_fixture(scenario_id: str) -> ScenarioFixture:
    try:
        return SCENARIOS[scenario_id]
    except KeyError as exc:
        raise KeyError(f"Unknown scenario: {scenario_id}") from exc


def ordered_fixtures() -> tuple[ScenarioFixture, ...]:
    return tuple(get_fixture(scenario_id) for scenario_id in SCENARIO_ORDER)


def known_session_ids() -> tuple[str, ...]:
    return tuple(fixture.session_id for fixture in ordered_fixtures())
