from __future__ import annotations

from dataclasses import dataclass

from zti.demo.fixtures import ScenarioFixture

APPROVED_REGIONS: tuple[str, ...] = ("us-east-1", "us-west-2")
APPROVED_MODULE = "terraform-aws-ec2-instance"
ALLOWED_INSTANCE_TYPES: tuple[str, ...] = ("m5.xlarge",)
MAX_INSTANCE_COUNT = 10


@dataclass(frozen=True)
class PolicyCheck:
    code: str
    passed: bool


@dataclass(frozen=True)
class ValidationResult:
    status: str
    visible_checks: tuple[PolicyCheck, ...]
    internal_checks: tuple[PolicyCheck, ...]
    failure_code: str | None


@dataclass(frozen=True)
class LineageResult:
    status: str
    failure_code: str | None


def evaluate_validation(fixture: ScenarioFixture) -> ValidationResult:
    checks: list[PolicyCheck] = []
    visible: list[PolicyCheck] = []

    region_check = PolicyCheck("region.approved", fixture.region in APPROVED_REGIONS)
    checks.append(region_check)
    if fixture.scenario_id != "prod-us-east-migration-override":
        visible.append(region_check)
    if not region_check.passed:
        return ValidationResult(
            status="FAILED",
            visible_checks=(PolicyCheck("region.not_in_approved_set", False),),
            internal_checks=tuple(checks),
            failure_code="region.not_in_approved_set",
        )

    module_check = PolicyCheck("module.approved", fixture.module == APPROVED_MODULE)
    checks.append(module_check)
    if fixture.scenario_id == "prod-policy-near-miss":
        visible.append(module_check)
    if not module_check.passed:
        return ValidationResult("FAILED", tuple(visible), tuple(checks), "module.not_approved")

    type_check = PolicyCheck("instance_type.approved", fixture.instance_type in ALLOWED_INSTANCE_TYPES)
    checks.append(type_check)
    if fixture.scenario_id == "prod-policy-near-miss":
        visible.append(type_check)
    if not type_check.passed:
        return ValidationResult("FAILED", tuple(visible), tuple(checks), "instance_type.not_approved")

    count_check = PolicyCheck("instance_count.within_limit", fixture.instance_count <= MAX_INSTANCE_COUNT)
    checks.append(count_check)
    if fixture.scenario_id == "prod-policy-near-miss":
        visible.append(count_check)
    if not count_check.passed:
        return ValidationResult("FAILED", tuple(visible), tuple(checks), "instance_count.exceeds_limit")

    approval_exists = PolicyCheck("approval.present", bool(fixture.approval_identity))
    checks.append(approval_exists)
    if not approval_exists.passed:
        return ValidationResult("FAILED", tuple(visible), tuple(checks), "approval.missing")

    return ValidationResult(
        status="PASSED",
        visible_checks=tuple(visible),
        internal_checks=tuple(checks),
        failure_code=None,
    )


def evaluate_lineage(fixture: ScenarioFixture, validation: ValidationResult) -> LineageResult:
    if validation.status != "PASSED":
        return LineageResult(status="SKIPPED", failure_code=None)

    if not fixture.approval_identity:
        return LineageResult(status="FAILED", failure_code="approval.missing")

    if fixture.approval_scope != fixture.required_scope:
        return LineageResult(status="FAILED", failure_code="approval.invalid_scope")

    return LineageResult(status="PASSED", failure_code=None)
