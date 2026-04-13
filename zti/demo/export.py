from __future__ import annotations

from pathlib import Path

from zti.demo.narrative import build_terminal_output_text


def export_terminal_output(project_root: Path | None = None) -> Path:
    root = project_root or Path(__file__).resolve().parents[2]
    output_path = root / "dev" / "site" / "_generated" / "demo-output.txt"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(build_terminal_output_text(), encoding="utf-8")
    return output_path
