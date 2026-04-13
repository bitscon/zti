from __future__ import annotations

import json
import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from zti.demo.executor import ExecutionResult, execute_verified_artifact
from zti.demo.fixtures import SCENARIOS, ScenarioFixture, get_fixture, ordered_fixtures
from zti.demo.policy import LineageResult, ValidationResult, evaluate_lineage, evaluate_validation
from zti.integrity import DecisionRecord, create_decision_record
from zti.lineage import ApprovalLineageEntry, create_lineage_entry, validate_lineage

RECORDING_PROFILE = "recording"


@dataclass(frozen=True)
class VerificationTrace:
    scenario_id: str
    session_id: str
    risk: str
    impact: str
    likelihood: str
    cause: str
    proposal: dict[str, Any]
    classification: dict[str, Any]
    explainability: dict[str, Any]
    validation: dict[str, Any]
    integrity: dict[str, Any]
    lineage: dict[str, Any]
    decision: str
    confidence: str
    control: str
    execution: dict[str, Any]
    comparison: dict[str, str] | None = None

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "scenario_id": self.scenario_id,
            "session_id": self.session_id,
            "risk": self.risk,
            "impact": self.impact,
            "likelihood": self.likelihood,
            "cause": self.cause,
            "proposal": self.proposal,
            "classification": self.classification,
            "explainability": self.explainability,
            "validation": self.validation,
            "integrity": self.integrity,
            "lineage": self.lineage,
            "decision": self.decision,
            "confidence": self.confidence,
            "control": self.control,
            "execution": self.execution,
        }
        if self.comparison is not None:
            payload["comparison"] = self.comparison
        return payload


@dataclass(frozen=True)
class ScenarioRunResult:
    trace: VerificationTrace
    decision_record: DecisionRecord
    lineage_entry: ApprovalLineageEntry | None


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def runtime_root() -> Path:
    configured = os.environ.get("ZTI_DEMO_RUNTIME_DIR")
    if configured:
        return Path(configured)
    return _project_root() / ".demo_runtime"


def ensure_runtime_dirs() -> Path:
    root = runtime_root()
    (root / "traces").mkdir(parents=True, exist_ok=True)
    (root / "audit").mkdir(parents=True, exist_ok=True)
    return root


def reset_runtime(profile: str = RECORDING_PROFILE) -> None:
    _require_recording_profile(profile)
    root = runtime_root()
    if root.exists():
        shutil.rmtree(root)
    ensure_runtime_dirs()
    metadata = {
        "profile": profile,
        "scenario_order": [fixture.scenario_id for fixture in ordered_fixtures()],
        "session_order": [fixture.session_id for fixture in ordered_fixtures()],
    }
    (root / "meta.json").write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _require_recording_profile(profile: str) -> None:
    if profile != RECORDING_PROFILE:
        raise ValueError(f"Unsupported profile: {profile}")


def _visible_explainability(fixture: ScenarioFixture) -> dict[str, Any]:
    visible = {
        "module": fixture.module,
        "region": fixture.region,
        "instance_count": fixture.instance_count,
    }
    if fixture.scenario_id == "prod-policy-near-miss":
        visible["instance_type"] = fixture.instance_type
    return visible


def _build_decision_payload(
    fixture: ScenarioFixture,
    validation: ValidationResult,
    lineage: LineageResult,
    decision: str,
) -> bytes:
    payload = {
        "scenario_id": fixture.scenario_id,
        "session_id": fixture.session_id,
        "classification": fixture.classification,
        "validation_status": validation.status,
        "validation_failure": validation.failure_code,
        "lineage_status": lineage.status,
        "lineage_failure": lineage.failure_code,
        "decision": decision,
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _make_lineage_payload(fixture: ScenarioFixture, lineage: LineageResult, entry: ApprovalLineageEntry | None) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "status": lineage.status,
        "failure_code": lineage.failure_code,
        "approval_identity": fixture.approval_identity,
        "approval_scope": fixture.approval_scope,
        "required_scope": fixture.required_scope,
    }
    if entry is not None:
        payload["entry_id"] = entry.entry_id
        payload["entry_hash"] = entry.entry_hash
        entry_valid, _entry_error = validate_lineage((entry,))
        payload["entry_integrity"] = "VALID" if entry_valid else "INVALID"
    return payload


def _comparison_payload(fixture: ScenarioFixture) -> dict[str, str] | None:
    if fixture.scenario_id != "prod-policy-near-miss":
        return None
    return {
        "without_zti": "PASSED",
        "with_zti": "BLOCKED",
    }


def _execute_fixture(fixture: ScenarioFixture, previous_record: DecisionRecord | None) -> ScenarioRunResult:
    validation = evaluate_validation(fixture)
    lineage = evaluate_lineage(fixture, validation)
    approved = validation.status == "PASSED" and lineage.status == "PASSED"
    decision = "APPROVED" if approved else "REJECTED"

    decision_record, decision_error = create_decision_record(
        record_id=f"{fixture.session_id}:{decision.lower()}",
        decision_data=_build_decision_payload(fixture, validation, lineage, decision),
        previous_record=previous_record,
        timestamp_ns=fixture.decision_timestamp_ns,
    )
    if decision_error is not None or decision_record is None:
        raise RuntimeError(f"Failed to create decision record: {decision_error}")

    lineage_entry: ApprovalLineageEntry | None = None
    if fixture.approval_identity and fixture.lineage_timestamp_ns is not None:
        lineage_entry, lineage_error = create_lineage_entry(
            entry_id=f"{fixture.session_id}:approval",
            decision_record_id=decision_record.record_id,
            approver_id=fixture.approval_identity,
            approval_action="approve",
            timestamp_ns=fixture.lineage_timestamp_ns,
        )
        if lineage_error is not None:
            raise RuntimeError(f"Failed to create lineage entry: {lineage_error}")

    execution_result: ExecutionResult = execute_verified_artifact(approved=approved)

    validation_payload = {
        "status": validation.status,
        "failure_code": validation.failure_code,
        "visible_checks": [
            {"code": check.code, "passed": check.passed}
            for check in validation.visible_checks
        ],
        "internal_checks": [
            {"code": check.code, "passed": check.passed}
            for check in validation.internal_checks
        ],
    }

    integrity_payload = {
        "status": "PASSED",
        "artifact_sealed": True,
        "record_id": decision_record.record_id,
        "decision_hash": decision_record.decision_hash,
        "previous_hash": decision_record.previous_hash,
        "chain_hash": decision_record.chain_hash,
        "timestamp_ns": decision_record.timestamp_ns,
    }

    trace = VerificationTrace(
        scenario_id=fixture.scenario_id,
        session_id=fixture.session_id,
        risk=fixture.risk,
        impact=fixture.impact,
        likelihood=fixture.likelihood,
        cause=fixture.cause,
        proposal={
            "provider": fixture.provider,
            "module": fixture.module,
            "region": fixture.region,
            "instance_count": fixture.instance_count,
            "instance_type": fixture.instance_type,
            "approval_identity": fixture.approval_identity,
            "approval_scope": fixture.approval_scope,
            "required_scope": fixture.required_scope,
            "pipeline_run_id": fixture.pipeline_run_id,
            "commit_sha": fixture.commit_sha,
            "operator_id": fixture.operator_id,
        },
        classification={"value": fixture.classification},
        explainability={
            "status": "PASSED",
            "visible_fields": _visible_explainability(fixture),
        },
        validation=validation_payload,
        integrity=integrity_payload,
        lineage=_make_lineage_payload(fixture, lineage, lineage_entry),
        decision=decision,
        confidence="VERIFIED",
        control=(
            "Only verified artifacts allowed to execute"
            if approved
            else "Execution blocked at verification boundary"
        ),
        execution={
            "accepted": execution_result.accepted,
            "message": execution_result.message,
        },
        comparison=_comparison_payload(fixture),
    )
    return ScenarioRunResult(trace=trace, decision_record=decision_record, lineage_entry=lineage_entry)


def replay_all_results(profile: str = RECORDING_PROFILE) -> tuple[ScenarioRunResult, ...]:
    _require_recording_profile(profile)
    results: list[ScenarioRunResult] = []
    previous_record: DecisionRecord | None = None
    for fixture in ordered_fixtures():
        result = _execute_fixture(fixture, previous_record)
        results.append(result)
        previous_record = result.decision_record
    return tuple(results)


def replay_results_through(scenario_id: str, profile: str = RECORDING_PROFILE) -> tuple[ScenarioRunResult, ...]:
    fixture = get_fixture(scenario_id)
    return tuple(result for result in replay_all_results(profile) if SCENARIOS[result.trace.scenario_id].order <= fixture.order)


def latest_trace(profile: str = RECORDING_PROFILE) -> VerificationTrace:
    return replay_all_results(profile)[-1].trace


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def persist_results(results: tuple[ScenarioRunResult, ...]) -> None:
    root = ensure_runtime_dirs()
    for result in results:
        _write_json(root / "traces" / f"{result.trace.session_id}.json", result.trace.to_dict())


def persist_audit_report(session_id: str, payload: dict[str, Any]) -> None:
    root = ensure_runtime_dirs()
    _write_json(root / "audit" / f"{session_id}.json", payload)


def run_scenario(scenario_id: str, profile: str = RECORDING_PROFILE) -> VerificationTrace:
    results = replay_results_through(scenario_id, profile)
    persist_results(results)
    return results[-1].trace
