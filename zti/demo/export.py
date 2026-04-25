from __future__ import annotations

import re
from pathlib import Path

TEXT_BLOCK_PATTERN = re.compile(r"```text\n(.*?)\n```", re.DOTALL)


def _canonical_transcript(source_root: Path) -> str:
    terminal_output_path = source_root / "resources" / "demo" / "terminal-output.md"
    markdown = terminal_output_path.read_text(encoding="utf-8")
    match = TEXT_BLOCK_PATTERN.search(markdown)
    if match is None:
        raise ValueError(f"Unable to locate transcript text block in {terminal_output_path}")
    transcript = match.group(1).replace("\r\n", "\n").replace("\r", "\n")
    transcript = transcript.rstrip("\n") + "\n"
    return transcript


def export_terminal_output(project_root: Path | None = None) -> Path:
    source_root = Path(__file__).resolve().parents[2]
    output_root = project_root or source_root
    output_path = output_root / "dev" / "site" / "_dist" / "assets" / "demo-output.txt"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(_canonical_transcript(source_root), encoding="utf-8")
    return output_path
