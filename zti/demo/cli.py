from __future__ import annotations

import argparse
import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

from zti.demo.audit import build_audit_report
from zti.demo.engine import latest_trace, persist_audit_report, reset_runtime, run_scenario
from zti.demo.fixtures import SCENARIOS, ordered_fixtures
from zti.demo.narrative import render_audit_terminal, render_scenario_terminal, sync_demo_assets


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="zti-demo")
    subparsers = parser.add_subparsers(dest="command", required=True)

    reset_parser = subparsers.add_parser("reset")
    reset_parser.add_argument("--profile", required=True, choices=["recording"])

    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("scenario_id", choices=[fixture.scenario_id for fixture in ordered_fixtures()])
    run_parser.add_argument("--explain", action="store_true")

    audit_parser = subparsers.add_parser("audit")
    audit_parser.add_argument("session_id")

    serve_parser = subparsers.add_parser("serve")
    serve_parser.add_argument("--host", default="127.0.0.1")
    serve_parser.add_argument("--port", type=int, default=8787)

    return parser


class _DemoHandler(BaseHTTPRequestHandler):
    server_version = "ZTIDemo/1.0"

    def _json_response(self, payload: dict[str, object], status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload, indent=2, sort_keys=True).encode("utf-8")
        self.send_response(status.value)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path == "/api/v1/demo/scenarios":
            payload = {
                "scenarios": [
                    {
                        "scenario_id": fixture.scenario_id,
                        "session_id": fixture.session_id,
                        "risk": fixture.risk,
                        "impact": fixture.impact,
                        "likelihood": fixture.likelihood,
                    }
                    for fixture in ordered_fixtures()
                ]
            }
            self._json_response(payload)
            return

        if path == "/api/v1/demo/latest":
            self._json_response(latest_trace().to_dict())
            return

        if path.startswith("/api/v1/demo/audit/"):
            session_id = path.rsplit("/", 1)[-1]
            try:
                report = build_audit_report(session_id)
            except KeyError:
                self._json_response({"error": "UNKNOWN_SESSION"}, HTTPStatus.NOT_FOUND)
                return
            persist_audit_report(session_id, report.to_dict())
            self._json_response(report.to_dict())
            return

        self._json_response({"error": "NOT_FOUND"}, HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path == "/api/v1/demo/reset":
            reset_runtime("recording")
            sync_demo_assets()
            self._json_response({"profile": "recording", "status": "reset"})
            return

        if path.startswith("/api/v1/demo/scenarios/") and path.endswith("/run"):
            scenario_id = path.split("/")[-2]
            if scenario_id not in SCENARIOS:
                self._json_response({"error": "UNKNOWN_SCENARIO"}, HTTPStatus.NOT_FOUND)
                return
            trace = run_scenario(scenario_id)
            self._json_response(trace.to_dict())
            return

        self._json_response({"error": "NOT_FOUND"}, HTTPStatus.NOT_FOUND)

    def log_message(self, format: str, *args: object) -> None:  # noqa: A003
        return


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)

    if args.command == "reset":
        reset_runtime(args.profile)
        sync_demo_assets()
        return 0

    if args.command == "run":
        trace = run_scenario(args.scenario_id)
        print(render_scenario_terminal(trace))
        return 0

    if args.command == "audit":
        report = build_audit_report(args.session_id)
        persist_audit_report(args.session_id, report.to_dict())
        print(render_audit_terminal(report))
        return 0

    if args.command == "serve":
        server = ThreadingHTTPServer((args.host, args.port), _DemoHandler)
        try:
            server.serve_forever()
        finally:
            server.server_close()
        return 0

    parser.error("Unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
