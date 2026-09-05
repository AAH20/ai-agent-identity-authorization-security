from __future__ import annotations

import argparse
import json
from pathlib import Path

from .conformance import run_suite


def junit(report: dict) -> str:
    cases = []
    for item in report["results"]:
        failure = "" if item["passed"] else f'<failure message={json.dumps(item["evidence"])} />'
        cases.append(f'<testcase classname="agentiam.core" name="{item["id"]}: {item["name"]}">{failure}</testcase>')
    return f'<?xml version="1.0" encoding="UTF-8"?><testsuite name="AgentIAM" tests="{report["total"]}" failures="{report["total"]-report["passed"]}">{"".join(cases)}</testsuite>\n'


def main() -> None:
    parser = argparse.ArgumentParser(prog="agentiam", description="Run AI agent identity and authorization conformance tests")
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("test")
    run.add_argument("--json", type=Path)
    run.add_argument("--junit", type=Path)
    args = parser.parse_args()
    report = run_suite()
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(report, indent=2) + "\n")
    if args.junit:
        args.junit.parent.mkdir(parents=True, exist_ok=True)
        args.junit.write_text(junit(report))
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if report["passed"] == report["total"] else 1)


if __name__ == "__main__":
    main()
