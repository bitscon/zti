from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

from zti.demo.audit import build_audit_report
from zti.demo.engine import latest_trace, reset_runtime, run_scenario
from zti.demo.export import export_terminal_output
from zti.demo.narrative import (
    build_recording_script_markdown,
    build_terminal_output_text,
    build_terminal_output_markdown,
    render_audit_terminal,
    render_cta_block,
    render_scenario_terminal,
    sync_demo_assets,
)


class DemoRuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmpdir.cleanup)
        self.runtime_dir = Path(self._tmpdir.name) / ".demo_runtime"
        self._previous_runtime_dir = os.environ.get("ZTI_DEMO_RUNTIME_DIR")
        os.environ["ZTI_DEMO_RUNTIME_DIR"] = str(self.runtime_dir)
        self.addCleanup(self._restore_runtime_dir)

    def _restore_runtime_dir(self) -> None:
        if self._previous_runtime_dir is None:
            os.environ.pop("ZTI_DEMO_RUNTIME_DIR", None)
        else:
            os.environ["ZTI_DEMO_RUNTIME_DIR"] = self._previous_runtime_dir

    def test_recording_reset_is_deterministic(self) -> None:
        reset_runtime("recording")
        first = run_scenario("prod-us-east-migration-override").to_dict()
        reset_runtime("recording")
        second = run_scenario("prod-us-east-migration-override").to_dict()
        self.assertEqual(first, second)

    def test_near_miss_fails_only_at_lineage_and_has_comparison(self) -> None:
        reset_runtime("recording")
        trace = run_scenario("prod-policy-near-miss").to_dict()

        self.assertEqual(trace["validation"]["status"], "PASSED")
        self.assertTrue(all(check["passed"] for check in trace["validation"]["visible_checks"]))
        self.assertEqual(trace["lineage"]["status"], "FAILED")
        self.assertEqual(trace["lineage"]["failure_code"], "approval.invalid_scope")
        self.assertEqual(trace["comparison"], {"without_zti": "PASSED", "with_zti": "BLOCKED"})

        rendered = render_scenario_terminal(run_scenario("prod-policy-near-miss"))
        self.assertIn("WITHOUT ZTI: PASSED", rendered)
        self.assertIn("WITH ZTI: BLOCKED (approval.invalid_scope)", rendered)

    def test_approved_case_has_exact_control_statement(self) -> None:
        reset_runtime("recording")
        trace = run_scenario("prod-capacity-approved").to_dict()
        rendered = render_scenario_terminal(run_scenario("prod-capacity-approved"))

        self.assertEqual(trace["decision"], "APPROVED")
        self.assertEqual(trace["confidence"], "VERIFIED")
        self.assertEqual(trace["control"], "Only verified artifacts allowed to execute")
        self.assertIs(trace["execution"]["accepted"], True)
        self.assertIn("CONTROL: Only verified artifacts allowed to execute", rendered)

    def test_audit_contains_required_authority_lines(self) -> None:
        reset_runtime("recording")
        report = build_audit_report("infra-2026-04-09-003")
        rendered = render_audit_terminal(report)

        self.assertIn("AUDIT READINESS:", rendered)
        self.assertIn("This execution is fully reconstructable and provable", rendered)
        self.assertIn("CONTROL GUARANTEE:", rendered)
        self.assertIn("No unverified decision reached execution", rendered)

    def test_generated_assets_are_runtime_derived(self) -> None:
        project_root = Path(self._tmpdir.name) / "project"
        demo_dir = project_root / "resources" / "demo"
        demo_dir.mkdir(parents=True)

        sync_demo_assets(project_root)

        script = (demo_dir / "script.md").read_text(encoding="utf-8")
        recording = (demo_dir / "recording-script.md").read_text(encoding="utf-8")
        terminal = (demo_dir / "terminal-output.md").read_text(encoding="utf-8")
        exported_terminal = (project_root / "dev" / "site" / "_generated" / "demo-output.txt").read_text(encoding="utf-8")

        self.assertIn("Terminal output is the only source of truth.", script)
        self.assertIn("Narration is part of the acceptance contract.", recording)
        self.assertIn("STATUS: Your current systems operate on trust — not verification", terminal)
        self.assertIn("WITHOUT ZTI: PASSED", terminal)
        self.assertEqual(exported_terminal, build_terminal_output_text())

    def test_export_terminal_output_writes_generated_site_asset(self) -> None:
        project_root = Path(self._tmpdir.name) / "project"
        output_path = export_terminal_output(project_root)

        self.assertEqual(
            output_path,
            project_root / "dev" / "site" / "_generated" / "demo-output.txt",
        )
        self.assertTrue(output_path.exists())
        self.assertEqual(output_path.read_text(encoding="utf-8"), build_terminal_output_text())

    def test_schema_required_keys_cover_payloads(self) -> None:
        reset_runtime("recording")
        trace = run_scenario("prod-policy-near-miss").to_dict()
        report = build_audit_report("infra-2026-04-09-003").to_dict()

        trace_schema = json.loads(Path("schemas/verification_trace.json").read_text(encoding="utf-8"))
        audit_schema = json.loads(Path("schemas/audit_report.json").read_text(encoding="utf-8"))

        self.assertTrue(set(trace_schema["required"]).issubset(trace.keys()))
        self.assertTrue(set(audit_schema["required"]).issubset(report.keys()))

    def test_terminal_output_and_recording_docs_lock_psychological_payload(self) -> None:
        terminal_md = build_terminal_output_markdown()
        recording_md = build_recording_script_markdown()
        cta = render_cta_block()

        self.assertIn("This Would Have Gotten Through", terminal_md)
        self.assertIn("1. This happens", recording_md)
        self.assertIn("2. We would not catch this", recording_md)
        self.assertIn("3. ZTI does", recording_md)
        self.assertIn("4. ZTI proves it", recording_md)
        self.assertIn("5. We need this", recording_md)
        self.assertIn("STATUS: Your current systems operate on trust — not verification", cta)

    def test_latest_trace_returns_canonical_latest_verification_trace(self) -> None:
        reset_runtime("recording")
        trace = latest_trace().to_dict()

        self.assertEqual(trace["scenario_id"], "prod-capacity-approved")
        self.assertEqual(trace["session_id"], "infra-2026-04-09-003")


if __name__ == "__main__":
    unittest.main()
