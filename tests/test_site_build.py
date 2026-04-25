from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from dev.site.build import build_site, check_build
from zti.demo.export import export_terminal_output


class SiteBuildTests(unittest.TestCase):
    def test_check_build_passes_for_repo_source(self) -> None:
        check_build()

    def test_build_outputs_root_relative_paths_and_hidden_core_nav(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            artifact_out = build_site(tmp_root / "artifact")

            index_html = (artifact_out / "index.html").read_text(encoding="utf-8")
            adopt_html = (artifact_out / "adopt" / "index.html").read_text(encoding="utf-8")

            self.assertIn('href="/assets/site.css"', index_html)
            self.assertNotIn('/dev/site/', index_html)
            self.assertIn('href="/adopt/request-access/"', index_html)
            self.assertNotIn('>Core</span>', index_html)
            self.assertNotIn('>Core</span>', adopt_html)
            self.assertIn('href="/core/"', adopt_html)
            self.assertIn('<source src="/assets/zti-demo.mp4" type="video/mp4" />', index_html)
            self.assertTrue((artifact_out / "assets" / "zti-demo.mp4").exists())

    def test_build_stages_canonical_transcript_into_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            project_root = Path.cwd()
            build_site(tmp_root / "artifact", project_root=project_root)
            transcript_asset = (tmp_root / "artifact" / "assets" / "demo-output.txt").read_text(encoding="utf-8")
            canonical = export_terminal_output(project_root).read_text(encoding="utf-8")
            self.assertEqual(transcript_asset, canonical)


if __name__ == "__main__":
    unittest.main()
