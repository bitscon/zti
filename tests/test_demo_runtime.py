from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

DEMO_RESOURCE_ROOT = Path(__file__).resolve().parents[1] / "resources" / "demo"
if str(DEMO_RESOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(DEMO_RESOURCE_ROOT))

import generate as demo_generate
from zti.demo.audit import build_audit_report
from zti.demo.engine import latest_trace, reset_runtime, run_scenario
from zti.demo.export import export_terminal_output
from zti.demo.narrative import render_audit_terminal, render_cta_block, render_scenario_terminal


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

    def test_export_terminal_output_writes_canonical_site_asset(self) -> None:
        project_root = Path(self._tmpdir.name) / "project"
        output_path = export_terminal_output(project_root)

        self.assertEqual(
            output_path,
            project_root / "dev" / "site" / "_dist" / "assets" / "demo-output.txt",
        )
        self.assertTrue(output_path.exists())
        self.assertEqual(output_path.read_text(encoding="utf-8"), demo_generate.build_raw_transcript())

    def test_schema_required_keys_cover_payloads(self) -> None:
        reset_runtime("recording")
        trace = run_scenario("prod-policy-near-miss").to_dict()
        report = build_audit_report("infra-2026-04-09-003").to_dict()

        trace_schema = json.loads(Path("schemas/verification_trace.json").read_text(encoding="utf-8"))
        audit_schema = json.loads(Path("schemas/audit_report.json").read_text(encoding="utf-8"))

        self.assertTrue(set(trace_schema["required"]).issubset(trace.keys()))
        self.assertTrue(set(audit_schema["required"]).issubset(report.keys()))

    def test_compiler_outputs_are_deterministic_and_verifiable(self) -> None:
        first = demo_generate.build_artifacts()
        second = demo_generate.build_artifacts()

        self.assertEqual(first, second)
        demo_generate.check_artifacts()

    def test_compiler_cast_matches_transcript_and_required_lines(self) -> None:
        transcript = demo_generate.build_raw_transcript()
        cast_text = demo_generate.reconstruct_visible_text_from_cast(demo_generate.build_cast())

        self.assertEqual(cast_text, transcript)
        for required in demo_generate.REQUIRED_LINES:
            self.assertIn(required, transcript)
        for forbidden in demo_generate.FORBIDDEN_STRINGS:
            self.assertNotIn(forbidden, transcript)
        self.assertGreaterEqual(demo_generate.total_runtime_seconds(), 75)
        self.assertLessEqual(demo_generate.total_runtime_seconds(), 90)

    def test_recording_script_and_cta_lock_psychological_payload(self) -> None:
        recording_md = demo_generate.build_recording_script_markdown()
        cta = render_cta_block()

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
