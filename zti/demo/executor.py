from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ExecutionResult:
    accepted: bool
    message: str


def execute_verified_artifact(*, approved: bool) -> ExecutionResult:
    if not approved:
        return ExecutionResult(
            accepted=False,
            message="execution blocked at verification boundary",
        )

    return ExecutionResult(
        accepted=True,
        message="sandbox executor accepted verified artifact",
    )
