#!/usr/bin/env python3
"""Render a portfolio summary from Project 13 automation outputs."""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any


def read_json(path: Path) -> Any:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def count_status(items: list[dict[str, Any]] | None, status: str) -> int:
    if not items:
        return 0
    return sum(1 for item in items if item.get("status") == status)


def main() -> int:
    parser = argparse.ArgumentParser(description="Render Project 13 portfolio report.")
    parser.add_argument("--outputs-dir", default="outputs", help="AUTOMATION1 outputs directory")
    parser.add_argument("--report", default="outputs/project13-final-report.md", help="target report path")
    args = parser.parse_args()

    outputs = Path(args.outputs_dir)
    phase3 = read_json(outputs / "phase3-read-only" / "summary.json")
    phase4 = read_json(outputs / "phase4-redacted-backups" / "summary.json")
    phase5 = read_json(outputs / "phase5-compliance" / "summary.json")
    phase6 = read_json(outputs / "phase6-safe-config" / "summary.json")

    lines = [
        "# Project 13 Final Automation Report",
        "",
        f"- Rendered UTC: {dt.datetime.now(dt.UTC).isoformat()}",
        "- Scope: CML enterprise network automation workstation, IOS/IOL fleet, and ASA exception tracking",
        "",
        "## Executive Summary",
        "",
        "I built a network automation workflow around the same enterprise CML lab used in Projects 01-12. "
        "The workflow starts with a structured inventory, proves reachability, collects read-only baselines, "
        "backs up redacted running configs, checks compliance, and provides a dry-run-first config push path.",
        "",
        "## Phase Results",
        "",
        "| Phase | Evidence | Result |",
        "|-------|----------|--------|",
    ]

    if phase3 is not None:
        lines.append(
            f"| 3 read-only collection | {len(phase3)} devices attempted | "
            f"{count_status(phase3, 'ok')} successful, {len(phase3) - count_status(phase3, 'ok')} failed |"
        )
    else:
        lines.append("| 3 read-only collection | missing summary.json | not rendered |")

    if phase4 is not None:
        lines.append(
            f"| 4 redacted backups | {len(phase4)} devices attempted | "
            f"{count_status(phase4, 'ok')} successful, {len(phase4) - count_status(phase4, 'ok')} failed |"
        )
    else:
        lines.append("| 4 redacted backups | missing summary.json | not rendered |")

    if phase5 is not None:
        compliant = count_status(phase5, "compliant")
        non_compliant = count_status(phase5, "non_compliant")
        failed = count_status(phase5, "failed")
        lines.append(
            f"| 5 compliance | {len(phase5)} devices attempted | "
            f"{compliant} compliant, {non_compliant} non-compliant, {failed} failed |"
        )
    else:
        lines.append("| 5 compliance | missing summary.json | not rendered |")

    if phase6 is not None:
        applied = any(item.get("applied") for item in phase6)
        lines.append(f"| 6 gated config push | {len(phase6)} devices planned | applied={applied} |")
    else:
        lines.append("| 6 gated config push | missing summary.json | not rendered |")

    lines.extend(
        [
            "",
            "## Portfolio Takeaway",
            "",
            "This project demonstrates the DevNet side of the lab: I can turn a manually built network into "
            "an inventory-driven automation target, collect evidence at scale, detect configuration drift, "
            "and gate changes so automation is controlled instead of reckless.",
            "",
        ]
    )

    target = Path(args.report)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(lines), encoding="utf-8")
    print(f"Report written: {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
