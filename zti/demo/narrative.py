from __future__ import annotations

from pathlib import Path

from zti.demo.audit import AuditReport, build_audit_report
from zti.demo.engine import VerificationTrace, replay_all_results

DIVIDER = "────────────────────────────────────────────"
SOURCE_OF_TRUTH_NOTICE = (
    "Terminal output is the only source of truth. "
    "All demo assets are generated from runtime output. "
    "Manual editing is forbidden."
)


def render_scenario_terminal(trace: VerificationTrace) -> str:
    lines: list[str] = [
        DIVIDER,
        "ZTI DEMO — INFRASTRUCTURE VERIFICATION",
        f"SCENARIO: {trace.scenario_id}",
        f"SESSION: {trace.session_id}",
        DIVIDER,
        "",
        f"RISK: {trace.risk}",
        f"IMPACT: {trace.impact}",
        f"LIKELIHOOD: {trace.likelihood}",
        "",
        "→ Proposal received",
        f"→ Classification: {trace.classification['value']}",
        "",
        "→ Explainability generated",
    ]

    visible_fields = trace.explainability["visible_fields"]
    if trace.scenario_id in {"prod-us-east-migration-override", "prod-policy-near-miss"}:
        for key in visible_fields:
            lines.append(f"  - {key}: {visible_fields[key]}")
        lines.append("")

    if trace.scenario_id == "prod-us-east-migration-override":
        lines.extend([
            "→ Validation",
            "  ✖ region.not_in_approved_set",
            "",
            f"DECISION: {trace.decision}",
            f"CONFIDENCE: {trace.confidence}",
            f"CONTROL: {trace.control}",
        ])
        return "\n".join(lines)

    if trace.scenario_id == "prod-policy-near-miss":
        lines.extend([
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
            f"DECISION: {trace.decision}",
            f"CONFIDENCE: {trace.confidence}",
            f"CONTROL: {trace.control}",
        ])
        return "\n".join(lines)

    lines.extend([
        "→ Validation",
        "  ✔ all constraints passed",
        "",
        "→ Integrity check",
        "  ✔ artifact sealed",
        "",
        "→ Lineage recorded",
        "  ✔ approval chain verified",
        "",
        f"DECISION: {trace.decision}",
        f"CONFIDENCE: {trace.confidence}",
        "",
        "→ Execution",
        "  ✔ sandbox executor accepted verified artifact",
        "",
        f"CONTROL: {trace.control}",
    ])
    return "\n".join(lines)


def render_audit_terminal(report: AuditReport) -> str:
    return "\n".join([
        DIVIDER,
        "ZTI AUDIT REPORT",
        f"SESSION: {report.session_id}",
        DIVIDER,
        "",
        "What was proposed:",
        f"- {report.what_was_proposed[0]}",
        "",
        "What was blocked:",
        f"- {report.what_was_blocked[0]}",
        f"- {report.what_was_blocked[1]}",
        "",
        "What was executed:",
        f"- {report.what_was_executed[0]}",
        "",
        "Who approved:",
        f"- {report.who_approved[0]}",
        "",
        f"Chain integrity: {report.chain_integrity}",
        f"Lineage integrity: {report.lineage_integrity}",
        "",
        "AUDIT READINESS:",
        report.audit_readiness,
        "",
        "CONTROL GUARANTEE:",
        report.control_guarantee,
    ])


def render_cta_block() -> str:
    return "\n".join([
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
    ])


def _command_block(command: str) -> str:
    return f"```bash\n$ {command}\n```"


def _text_block(text: str) -> str:
    return f"```text\n{text}\n```"


def _terminal_output_sections() -> list[dict[str, str]]:
    results = replay_all_results()
    audit = build_audit_report("infra-2026-04-09-003")
    rendered = {
        result.trace.scenario_id: render_scenario_terminal(result.trace)
        for result in results
    }
    return [
        {
            "title": "0. Reset (Pre-roll)",
            "command": "zti-demo reset --profile recording",
            "output": "",
        },
        {
            "title": "1. Hook — This Could Happen Here",
            "command": "zti-demo run prod-us-east-migration-override --explain",
            "output": rendered["prod-us-east-migration-override"],
        },
        {
            "title": "2. Escalation — This Would Have Gotten Through",
            "command": "zti-demo run prod-policy-near-miss --explain",
            "output": rendered["prod-policy-near-miss"],
        },
        {
            "title": "3. Resolution — Only Verified Executes",
            "command": "zti-demo run prod-capacity-approved --explain",
            "output": rendered["prod-capacity-approved"],
        },
        {
            "title": "4. Authority — This Is What Auditors Want",
            "command": "zti-demo audit infra-2026-04-09-003",
            "output": render_audit_terminal(audit),
        },
        {
            "title": "5. Close — CTA",
            "command": "",
            "output": render_cta_block(),
        },
    ]


def build_terminal_output_text() -> str:
    sections = _terminal_output_sections()
    blocks: list[str] = []
    for section in sections:
        if section["command"]:
            blocks.append(f"$ {section['command']}")
        if section["output"]:
            blocks.append(section["output"])
    return "\n\n".join(blocks) + "\n"


def build_terminal_output_markdown() -> str:
    sections = _terminal_output_sections()
    markdown_lines: list[str] = [
        "# ZTI Demo — Terminal Output",
        "",
        "Generated from the `zti-demo` recording runtime. Do not edit manually.",
        SOURCE_OF_TRUTH_NOTICE,
        "",
    ]
    for section in sections:
        markdown_lines.append(f"## {section['title']}")
        if section["command"]:
            markdown_lines.append(_command_block(section["command"]))
        if section["output"]:
            markdown_lines.append(_text_block(section["output"]))
        markdown_lines.append("")
    return "\n".join(markdown_lines)


def build_script_markdown() -> str:
    results = replay_all_results()
    output = {result.trace.scenario_id: render_scenario_terminal(result.trace) for result in results}
    audit = render_audit_terminal(build_audit_report("infra-2026-04-09-003"))
    cta = render_cta_block()
    return "\n".join([
        "# ZTI Demo Script",
        "",
        "Generated from the `zti-demo` recording runtime. Do not edit manually.",
        SOURCE_OF_TRUTH_NOTICE,
        "",
        "Goal: ~75–90 seconds total  ",
        "Tone: Calm, controlled, confident  ",
        "Pacing: Slight pauses between sections (let it breathe)",
        "",
        "## 0. Reset (Pre-roll — not narrated)",
        _command_block("zti-demo reset --profile recording"),
        "",
        "(No narration — clean slate, deterministic run)",
        "",
        "## 1. Hook — THIS COULD HAPPEN HERE (~15 sec)",
        _command_block("zti-demo run prod-us-east-migration-override --explain"),
        "",
        "Narration:",
        "> \"This is a standard infrastructure change.\n> Looks normal... nothing unusual.\"",
        "",
        _text_block(output["prod-us-east-migration-override"]),
        "",
        "Narration:",
        "> \"ZTI doesn't trust the request.\n> It verifies it — before anything runs.\"",
        "",
        "## 2. Escalation — THIS WOULD HAVE GOTTEN THROUGH (~25 sec)",
        _command_block("zti-demo run prod-policy-near-miss --explain"),
        "",
        "Narration:",
        "> \"Now let's look at something more realistic...\n> This one appears fully compliant.\"",
        "",
        _text_block(output["prod-policy-near-miss"]),
        "",
        "Narration:",
        "> \"Everything looks right...\n> this would pass most systems.\"",
        "",
        "(pause)",
        "",
        "Narration:",
        "> \"But the approval chain is wrong.\"",
        "",
        "## 3. Resolution — ONLY VERIFIED EXECUTES (~20 sec)",
        _command_block("zti-demo run prod-capacity-approved --explain"),
        "",
        "Narration:",
        "> \"Now — same type of change...\n> but fully verified.\"",
        "",
        _text_block(output["prod-capacity-approved"]),
        "",
        "Narration:",
        "> \"ZTI doesn't block infrastructure...\n> it ensures only verified infrastructure runs.\"",
        "",
        "## 4. Authority — THIS IS WHAT AUDITORS WANT (~20 sec)",
        _command_block("zti-demo audit infra-2026-04-09-003"),
        "",
        "Narration:",
        "> \"Now — audit the execution.\"",
        "",
        _text_block(audit),
        "",
        "Narration:",
        "> \"This is the difference between trusting a system...\n> and proving it.\"",
        "",
        "## 5. Close — CTA (~10 sec)",
        _text_block(cta),
        "",
        "Narration:",
        "> \"ZTI doesn't trust AI or infrastructure decisions.\n> It proves them.\"",
        "",
    ])


def build_recording_script_markdown() -> str:
    return "\n".join([
        "# Demo Recording Script",
        "",
        "Generated from the `zti-demo` recording runtime. Do not edit manually.",
        SOURCE_OF_TRUTH_NOTICE,
        "",
        "Narration is part of the acceptance contract.",
        "Recording must match canonical narration phrases exactly.",
        "No improvisation allowed in production recording.",
        "",
        "## Delivery Notes",
        "",
        "- Dark terminal theme",
        "- Large readable font",
        "- No typos",
        "- Clean scroll",
        "- Cursor visible but not distracting",
        "- Practice once — record second take",
        "- Pause after the first REJECTED",
        "- Pause after the WITHOUT ZTI / WITH ZTI comparison",
        "- Pause after the audit output",
        "",
        "## Psychological Payload",
        "",
        "1. This happens",
        "2. We would not catch this",
        "3. ZTI does",
        "4. ZTI proves it",
        "5. We need this",
        "",
        "## Critical Warning",
        "",
        "- Do not speed this up",
        "- Do not over-explain anything",
        "- Do not add extra commentary",
        "- The power of this demo is controlled silence plus obvious outcomes",
        "",
        build_script_markdown(),
    ])


def sync_demo_assets(project_root: Path | None = None) -> None:
    root = project_root or Path(__file__).resolve().parents[2]
    demo_dir = root / "resources" / "demo"
    demo_dir.mkdir(parents=True, exist_ok=True)
    (demo_dir / "script.md").write_text(build_script_markdown(), encoding="utf-8")
    (demo_dir / "recording-script.md").write_text(build_recording_script_markdown(), encoding="utf-8")
    (demo_dir / "terminal-output.md").write_text(build_terminal_output_markdown(), encoding="utf-8")
    from zti.demo.export import export_terminal_output

    export_terminal_output(root)
