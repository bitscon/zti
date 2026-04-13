from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from pathlib import Path
from typing import Iterable

from session_model import (
    CRITICAL_WARNINGS,
    DELIVERY_NOTES,
    PSYCHOLOGICAL_PAYLOAD,
    SECTIONS,
    SESSION,
    SectionMetadata,
    SectionStep,
    SessionEvent,
)

FRAME_TIME = 0.1
COMMAND_LINE_TICKS = 8
OUTPUT_LINE_TICKS = 7
BLANK_LINE_TICKS = 3

BASE_DIR = Path(__file__).resolve().parent
TERMINAL_OUTPUT_PATH = BASE_DIR / "terminal-output.md"
RECORDING_SCRIPT_PATH = BASE_DIR / "recording-script.md"
CAST_PATH = BASE_DIR / "zti-demo.cast"
SHA_PATH = BASE_DIR / "demo.sha256"

GENERATED_NOTICE = "Generated from the deterministic demo compiler. Do not edit manually."
SOURCE_OF_TRUTH_NOTICE = (
    "Terminal output is the only source of truth. "
    "All demo assets are generated from the canonical session model. "
    "Manual editing is forbidden."
)
REQUIRED_LINES = (
    "WITHOUT ZTI: PASSED",
    "WITH ZTI: BLOCKED (approval.invalid_scope)",
    "AUDIT READINESS:",
    "CONTROL GUARANTEE:",
    "STATUS: Your current systems operate on trust — not verification",
)
FORBIDDEN_STRINGS = ("Traceback", "localhost", "/dev/site/")
VALID_EVENT_KINDS = {"command", "output", "pause"}


def pause_to_ticks(pause_after_seconds: float) -> int:
    return int(pause_after_seconds / FRAME_TIME)


def normalize_text(text: str) -> str:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    normalized = "\n".join(line.rstrip(" \t") for line in normalized.split("\n"))
    normalized = normalized.rstrip("\n")
    return f"{normalized}\n"


def event_to_canonical_dict(event: SessionEvent) -> dict[str, object]:
    return {
        "id": event.id,
        "kind": event.kind,
        "marker": event.marker,
        "pause_after_ticks": pause_to_ticks(event.pause_after_seconds),
        "text": event.text,
    }


def canonical_session_json(session: Iterable[SessionEvent]) -> str:
    payload = [event_to_canonical_dict(event) for event in session]
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def build_raw_transcript(session: Iterable[SessionEvent] = SESSION) -> str:
    parts: list[str] = []
    for event in session:
        if event.kind == "command":
            parts.append(f"$ {event.text}\n")
        elif event.kind == "output":
            parts.append(normalize_text(event.text))
        elif event.kind != "pause":
            raise ValueError(f"Unsupported event kind: {event.kind}")
    return normalize_text("".join(parts))


def _quote_narration(lines: tuple[str, ...]) -> list[str]:
    if not lines:
        return []
    if len(lines) == 1:
        return [f'> "{lines[0]}"']
    quoted = [f'> "{lines[0]}']
    quoted.extend(f"> {line}" for line in lines[1:-1])
    quoted.append(f'> {lines[-1]}"')
    return quoted


def _event_map(session: Iterable[SessionEvent] = SESSION) -> dict[str, SessionEvent]:
    return {event.id: event for event in session}


def _command_block(command: str) -> str:
    return f"```bash\n$ {command}\n```"


def _text_block(text: str) -> str:
    return f"```text\n{normalize_text(text)}```"


def build_terminal_output_markdown(session: Iterable[SessionEvent] = SESSION) -> str:
    raw_transcript = build_raw_transcript(session)
    markdown = "\n".join(
        (
            "# ZTI Demo — Terminal Output",
            "",
            GENERATED_NOTICE,
            SOURCE_OF_TRUTH_NOTICE,
            "",
            "```text",
            raw_transcript.rstrip("\n"),
            "```",
        )
    )
    return normalize_text(markdown)


def _render_section(section: SectionMetadata, events: dict[str, SessionEvent]) -> list[str]:
    lines: list[str] = [section.heading]
    for step in section.steps:
        if step.kind == "event":
            if step.ref is None:
                raise ValueError(f"Event step missing ref in section {section.key}")
            event = events[step.ref]
            if event.kind == "command":
                lines.extend(( _command_block(event.text), ""))
            elif event.kind == "output":
                lines.extend((_text_block(event.text), ""))
            elif event.kind == "pause":
                lines.extend((f"[pause {event.pause_after_seconds:.1f}s]", ""))
            else:
                raise ValueError(f"Unsupported event kind in section rendering: {event.kind}")
        elif step.kind == "narration":
            lines.append("Narration:")
            lines.extend(_quote_narration(step.lines))
            lines.append("")
        elif step.kind == "note":
            lines.extend((*step.lines, ""))
        else:
            raise ValueError(f"Unsupported step kind: {step.kind}")
    while lines and lines[-1] == "":
        lines.pop()
    return lines


def build_recording_script_markdown(
    session: Iterable[SessionEvent] = SESSION,
    sections: Iterable[SectionMetadata] = SECTIONS,
) -> str:
    events = _event_map(session)
    lines: list[str] = [
        "# Demo Recording Script",
        "",
        GENERATED_NOTICE,
        SOURCE_OF_TRUTH_NOTICE,
        "",
        "Narration is part of the acceptance contract.",
        "Recording must match canonical narration phrases exactly.",
        "No improvisation allowed in production recording.",
        "",
        "## Delivery Notes",
        "",
    ]
    lines.extend(f"- {note}" for note in DELIVERY_NOTES)
    lines.extend(
        (
            "",
            "## Psychological Payload",
            "",
        )
    )
    lines.extend(f"{index}. {line}" for index, line in enumerate(PSYCHOLOGICAL_PAYLOAD, start=1))
    lines.extend(
        (
            "",
            "## Critical Warning",
            "",
        )
    )
    lines.extend(f"- {warning}" for warning in CRITICAL_WARNINGS)
    lines.extend(
        (
            "",
            "# ZTI Demo Script",
            "",
            GENERATED_NOTICE,
            SOURCE_OF_TRUTH_NOTICE,
            "",
            "Goal: ~75–90 seconds total  ",
            "Tone: Calm, controlled, confident  ",
            "Pacing: Slight pauses between sections (let it breathe)",
            "",
        )
    )
    for section in sections:
        lines.extend(_render_section(section, events))
        lines.append("")
    return normalize_text("\n".join(lines).rstrip("\n"))


def _timestamp_from_ticks(ticks: int) -> float:
    return float(f"{ticks * FRAME_TIME:.1f}")


def _iter_visual_lines(event: SessionEvent) -> list[str]:
    if event.kind == "command":
        return [f"$ {event.text}\n"]
    if event.kind == "output":
        return normalize_text(event.text).splitlines(keepends=True)
    if event.kind == "pause":
        return []
    raise ValueError(f"Unsupported event kind: {event.kind}")


def build_cast(session: Iterable[SessionEvent] = SESSION) -> str:
    lines: list[str] = [
        json.dumps(
            {
                "version": 2,
                "width": 132,
                "height": 40,
                "env": {"TERM": "xterm-256color"},
            },
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
    ]
    current_ticks = 0
    for event in session:
        for visual_line in _iter_visual_lines(event):
            lines.append(
                json.dumps(
                    [_timestamp_from_ticks(current_ticks), "o", visual_line],
                    ensure_ascii=False,
                    separators=(",", ":"),
                )
            )
            if visual_line == "\n":
                current_ticks += BLANK_LINE_TICKS
            elif event.kind == "command":
                current_ticks += COMMAND_LINE_TICKS
            else:
                current_ticks += OUTPUT_LINE_TICKS
        current_ticks += pause_to_ticks(event.pause_after_seconds)
    return normalize_text("\n".join(lines))


def build_demo_sha256(session: Iterable[SessionEvent] = SESSION) -> str:
    payload = canonical_session_json(session) + build_raw_transcript(session)
    return f"{hashlib.sha256(payload.encode('utf-8')).hexdigest()}\n"


def build_artifacts(session: Iterable[SessionEvent] = SESSION) -> dict[Path, str]:
    return {
        TERMINAL_OUTPUT_PATH: build_terminal_output_markdown(session),
        RECORDING_SCRIPT_PATH: build_recording_script_markdown(session, SECTIONS),
        CAST_PATH: build_cast(session),
        SHA_PATH: build_demo_sha256(session),
    }


def reconstruct_visible_text_from_cast(cast_content: str) -> str:
    chunks: list[str] = []
    lines = normalize_text(cast_content).splitlines()
    if not lines:
        raise ValueError("Cast content is empty")
    json.loads(lines[0])
    for line in lines[1:]:
        timestamp, event_type, text = json.loads(line)
        if not isinstance(timestamp, (int, float)):
            raise ValueError("Cast timestamp must be numeric")
        if event_type != "o":
            raise ValueError(f"Unsupported cast event type: {event_type}")
        chunks.append(text)
    return normalize_text("".join(chunks))


def total_runtime_seconds(session: Iterable[SessionEvent] = SESSION) -> float:
    current_ticks = 0
    for event in session:
        for visual_line in _iter_visual_lines(event):
            if visual_line == "\n":
                current_ticks += BLANK_LINE_TICKS
            elif event.kind == "command":
                current_ticks += COMMAND_LINE_TICKS
            else:
                current_ticks += OUTPUT_LINE_TICKS
        current_ticks += pause_to_ticks(event.pause_after_seconds)
    return current_ticks * FRAME_TIME


def validate_session(session: Iterable[SessionEvent] = SESSION) -> None:
    seen_ids: set[str] = set()
    ordered_ids: list[str] = []
    for event in session:
        if event.kind not in VALID_EVENT_KINDS:
            raise SystemExit(f"Unsupported event kind: {event.kind}")
        if event.id in seen_ids:
            raise SystemExit(f"Duplicate event id: {event.id}")
        seen_ids.add(event.id)
        ordered_ids.append(event.id)
    expected_order = [event.id for event in SESSION]
    if ordered_ids != expected_order:
        raise SystemExit("Event order differs from the frozen session model")

    transcript = build_raw_transcript(session)
    for required in REQUIRED_LINES:
        if required not in transcript:
            raise SystemExit(f"Missing required line: {required}")
    for forbidden in FORBIDDEN_STRINGS:
        if forbidden in transcript:
            raise SystemExit(f"Forbidden string present in transcript: {forbidden}")

    duration = total_runtime_seconds(session)
    if duration < 75 or duration > 90:
        raise SystemExit(f"Total runtime {duration:.1f}s is outside the 75–90 second window")

    cast_text = reconstruct_visible_text_from_cast(build_cast(session))
    if cast_text != transcript:
        raise SystemExit("Generated cast text does not match the normalized transcript")


def write_artifacts() -> None:
    validate_session(SESSION)
    for path, content in build_artifacts(SESSION).items():
        path.write_text(content, encoding="utf-8")


def check_artifacts() -> None:
    validate_session(SESSION)
    expected = build_artifacts(SESSION)
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        for path, content in expected.items():
            generated_path = tmpdir / path.name
            generated_path.write_text(content, encoding="utf-8")
            if not path.exists():
                raise SystemExit(f"Missing canonical artifact: {path}")
            actual = path.read_bytes()
            regenerated = generated_path.read_bytes()
            if actual != regenerated:
                raise SystemExit(f"Artifact drift detected: {path}")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate deterministic ZTI demo artifacts.")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = _parser().parse_args(list(argv) if argv is not None else None)
    if args.write == args.check:
        raise SystemExit("Choose exactly one of --write or --check")
    if args.write:
        write_artifacts()
        return 0
    check_artifacts()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
