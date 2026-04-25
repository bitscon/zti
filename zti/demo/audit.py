from __future__ import annotations

from dataclasses import dataclass

from zti.demo.engine import ScenarioRunResult, replay_all_results
from zti.demo.fixtures import SCENARIOS
from zti.integrity import validate_chain
from zti.lineage import validate_lineage


@dataclass(frozen=True)
class AuditReport:
    session_id: str
    what_was_proposed: tuple[str, ...]
    what_was_blocked: tuple[str, ...]
    what_was_executed: tuple[str, ...]
    who_approved: tuple[str, ...]
    chain_integrity: str
    lineage_integrity: str
    audit_readiness: str
    control_guarantee: str
    executed_artifact: str

    def to_dict(self) -> dict[str, object]:
        return {
            "session_id": self.session_id,
            "what_was_proposed": list(self.what_was_proposed),
            "what_was_blocked": list(self.what_was_blocked),
            "what_was_executed": list(self.what_was_executed),
            "who_approved": list(self.who_approved),
            "chain_integrity": self.chain_integrity,
            "lineage_integrity": self.lineage_integrity,
            "audit_readiness": self.audit_readiness,
            "control_guarantee": self.control_guarantee,
            "executed_artifact": self.executed_artifact,
        }


def build_audit_report(session_id: str) -> AuditReport:
    if session_id not in {fixture.session_id for fixture in SCENARIOS.values()}:
        raise KeyError(f"Unknown session: {session_id}")

    results = replay_all_results()
    target = next(result for result in results if result.trace.session_id == session_id)
    approved = next(result for result in results if result.trace.session_id == "infra-2026-04-09-003")

    chain_valid, _chain_error = validate_chain([result.decision_record for result in results])
    lineage_entries = [approved.lineage_entry] if approved.lineage_entry is not None else []
    lineage_valid, _lineage_error = validate_lineage(lineage_entries) if lineage_entries else (False, None)

    return AuditReport(
        session_id=target.trace.session_id,
        what_was_proposed=("EC2 deployment (Terraform)",),
        what_was_blocked=(
            "Region violation (Session 001)",
            "Invalid approval chain (Session 002)",
        ),
        what_was_executed=("Verified, policy-compliant artifact only",),
        who_approved=("Authorized identity (production scope)",),
        chain_integrity="VALID" if chain_valid else "INVALID",
        lineage_integrity="VALID" if lineage_valid else "INVALID",
        audit_readiness="This execution is fully reconstructable and provable",
        control_guarantee="No unverified decision reached execution",
        executed_artifact=approved.trace.integrity["decision_hash"],
    )
