from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from dev.site.build import build_site, check_build
from zti.demo.export import export_terminal_output


class SiteBuildTests(unittest.TestCase):
    def test_check_build_passes_for_repo_source(self) -> None:
        check_build()

    def test_build_outputs_target_specific_paths_and_hidden_core_nav(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            dev_out = build_site("dev", tmp_root / "dev")
            prod_out = build_site("prod", tmp_root / "prod")

            dev_index = (dev_out / "index.html").read_text(encoding="utf-8")
            prod_index = (prod_out / "index.html").read_text(encoding="utf-8")
            prod_adopt = (prod_out / "adopt" / "index.html").read_text(encoding="utf-8")

            self.assertIn('href="/dev/site/assets/site.css"', dev_index)
            self.assertIn('href="/assets/site.css"', prod_index)
            self.assertNotIn('/dev/site/', prod_index)
            self.assertIn('href="/adopt/request-access/"', prod_index)
            self.assertNotIn('>Core</span>', prod_index)
            self.assertNotIn('>Core</span>', prod_adopt)
            self.assertIn('href="/core/"', prod_adopt)

    def test_build_stages_runtime_transcript_into_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            project_root = Path.cwd()
            build_site("prod", tmp_root / "prod", project_root=project_root)
            transcript_asset = (tmp_root / "prod" / "assets" / "demo-output.txt").read_text(encoding="utf-8")
            canonical = export_terminal_output(project_root).read_text(encoding="utf-8")
            self.assertEqual(transcript_asset, canonical)


if __name__ == "__main__":
    unittest.main()
