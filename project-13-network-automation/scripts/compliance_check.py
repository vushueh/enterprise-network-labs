#!/usr/bin/env python3
"""Project 13 network configuration compliance checker.

This checker connects to devices, reads running config, evaluates the Project 13
standards, and writes a report without storing raw secrets. It uses environment
variables for credentials and supports per-device overrides.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

import yaml
from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoAuthenticationException, NetmikoTimeoutException


ALLOWED_PLATFORMS = {"cisco_ios", "cisco_asa"}
FORBIDDEN_INVENTORY_KEYS = {"username", "password", "secret", "enable", "key"}


def env_prefix(name: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_").upper()
    return f"NETLAB_{normalized}"


def first_env(*names: str) -> str | None:
    for name in names:
        value = os.getenv(name)
        if value:
            return value
    return None


def load_inventory(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if "devices" not in data or not isinstance(data["devices"], list):
        raise ValueError("inventory must contain a top-level devices list")
    return data


def validate_inventory(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    names: set[str] = set()
    hosts: set[str] = set()

    for index, device in enumerate(data.get("devices", []), start=1):
        if not isinstance(device, dict):
            errors.append(f"device #{index} is not a mapping")
            continue
        missing = [key for key in ("name", "host", "platform", "role") if key not in device]
        if missing:
            errors.append(f"{device.get('name', f'device #{index}')} missing keys: {', '.join(missing)}")

        name = str(device.get("name", "")).strip()
        host = str(device.get("host", "")).strip()
        platform = str(device.get("platform", "")).strip()

        if name in names:
            errors.append(f"duplicate device name: {name}")
        if host in hosts:
            errors.append(f"duplicate host IP: {host}")
        if platform and platform not in ALLOWED_PLATFORMS:
            errors.append(f"{name}: unsupported platform {platform}")

        names.add(name)
        hosts.add(host)

        forbidden = FORBIDDEN_INVENTORY_KEYS.intersection(device.keys())
        if forbidden:
            errors.append(f"{name}: credential-like keys are not allowed in inventory: {', '.join(sorted(forbidden))}")

    return errors


def credentials_for(device: dict[str, Any]) -> tuple[str, str, str]:
    device_prefix = env_prefix(device["name"])
    if device["platform"] == "cisco_asa":
        username = first_env(f"{device_prefix}_USERNAME", "NETLAB_ASA_USERNAME", "NETLAB_USERNAME")
        password = first_env(f"{device_prefix}_PASSWORD", "NETLAB_ASA_PASSWORD", "NETLAB_PASSWORD")
        secret = first_env(f"{device_prefix}_SECRET", "NETLAB_ASA_SECRET", "NETLAB_SECRET") or password
    else:
        username = first_env(f"{device_prefix}_USERNAME", "NETLAB_IOS_USERNAME", "NETLAB_USERNAME")
        password = first_env(f"{device_prefix}_PASSWORD", "NETLAB_IOS_PASSWORD", "NETLAB_PASSWORD")
        secret = first_env(f"{device_prefix}_SECRET", "NETLAB_IOS_SECRET", "NETLAB_SECRET") or password

    missing = []
    if not username:
        missing.append("NETLAB_USERNAME")
    if not password:
        missing.append("NETLAB_PASSWORD")
    if missing:
        raise RuntimeError(f"missing environment variables: {', '.join(missing)}")
    return username, password, secret or ""


def connect_params(device: dict[str, Any], timeout: int) -> dict[str, Any]:
    username, password, secret = credentials_for(device)
    return {
        "device_type": device["platform"],
        "host": device["host"],
        "username": username,
        "password": password,
        "secret": secret,
        "timeout": timeout,
        "conn_timeout": timeout,
        "auth_timeout": timeout,
        "banner_timeout": timeout,
        "fast_cli": False,
    }


def get_running_config(device: dict[str, Any], timeout: int, read_timeout: int) -> str:
    with ConnectHandler(**connect_params(device, timeout)) as connection:
        if device["platform"] in {"cisco_ios", "cisco_asa"}:
            try:
                connection.enable()
            except Exception:
                pass
        return connection.send_command("show running-config", read_timeout=read_timeout)


def has_line(config: str, pattern: str) -> bool:
    return re.search(pattern, config, flags=re.MULTILINE | re.IGNORECASE) is not None


def add_check(checks: list[dict[str, str]], name: str, status: str, evidence: str) -> None:
    checks.append({"check": name, "status": status, "evidence": evidence})


def check_ios(device: dict[str, Any], config: str, standards: dict[str, Any]) -> list[dict[str, str]]:
    checks: list[dict[str, str]] = []
    syslog_server = re.escape(str(standards.get("syslog_server", "")))
    ntp_server = re.escape(str(standards.get("ntp_server", "")))
    snmp_ro = re.escape(str(standards.get("snmp_ro_community", "")))

    add_check(
        checks,
        "hostname matches inventory",
        "pass" if has_line(config, rf"^hostname\s+{re.escape(device['name'])}$") else "fail",
        f"expected hostname {device['name']}",
    )
    add_check(
        checks,
        "SSHv2 enabled",
        "pass" if has_line(config, r"^ip ssh version 2$") else "fail",
        "requires `ip ssh version 2`",
    )
    add_check(
        checks,
        "syslog points to collector",
        "pass" if syslog_server and has_line(config, rf"^logging host\s+{syslog_server}") else "fail",
        f"expected logging host {standards.get('syslog_server')}",
    )
    add_check(
        checks,
        "NTP points to core time source",
        "pass" if ntp_server and has_line(config, rf"^ntp server\s+{ntp_server}") else "fail",
        f"expected ntp server {standards.get('ntp_server')}",
    )
    add_check(
        checks,
        "SNMP read-only standard present",
        "pass" if snmp_ro and has_line(config, rf"^snmp-server community\s+{snmp_ro}\s+RO") else "fail",
        "expected standard read-only community; report stores only pass/fail",
    )
    add_check(
        checks,
        "config archive present",
        "pass" if has_line(config, r"^archive$") or has_line(config, r"^\s+path\s+") else "fail",
        "expected IOS archive path for rollback evidence",
    )
    plaintext_patterns = [
        r"^\s*password\s+0\s+\S+",
        r"^username\s+\S+.*\spassword\s+0\s+\S+",
        r"^enable\s+password\s+\S+",
    ]
    plaintext = any(has_line(config, pattern) for pattern in plaintext_patterns)
    add_check(
        checks,
        "no obvious plaintext passwords",
        "pass" if not plaintext else "fail",
        "checked for password type 0 and enable password",
    )
    return checks


def check_asa(device: dict[str, Any], config: str, standards: dict[str, Any]) -> list[dict[str, str]]:
    checks: list[dict[str, str]] = []
    syslog_server = re.escape(str(standards.get("syslog_server", "")))
    ntp_server = re.escape(str(standards.get("ntp_server", "")))
    snmp_ro = re.escape(str(standards.get("snmp_ro_community", "")))

    add_check(
        checks,
        "hostname matches inventory",
        "pass" if has_line(config, rf"^hostname\s+{re.escape(device['name'])}$") else "fail",
        f"expected hostname {device['name']}",
    )
    add_check(
        checks,
        "SSHv2 enabled",
        "pass" if has_line(config, r"^ssh version 2$") else "fail",
        "requires `ssh version 2`",
    )
    add_check(
        checks,
        "syslog points to collector",
        "pass" if syslog_server and has_line(config, rf"^logging host\s+\S+\s+{syslog_server}") else "fail",
        f"expected logging host interface {standards.get('syslog_server')}",
    )
    add_check(
        checks,
        "NTP points to core time source",
        "pass" if ntp_server and has_line(config, rf"^ntp server\s+{ntp_server}") else "fail",
        f"expected ntp server {standards.get('ntp_server')}",
    )
    add_check(
        checks,
        "SNMP read-only standard present",
        "pass" if snmp_ro and has_line(config, rf"^snmp-server community\s+{snmp_ro}") else "fail",
        "expected standard read-only community; report stores only pass/fail",
    )
    add_check(checks, "config archive present", "not_applicable", "ASA does not use IOS archive/configure replace")
    plaintext = has_line(config, r"^username\s+\S+\s+password\s+\S+\s*$") or has_line(config, r"^enable password\s+\S+\s*$")
    add_check(
        checks,
        "no obvious plaintext passwords",
        "warn" if plaintext else "pass",
        "ASA password output may be encrypted or masked depending on platform",
    )
    return checks


def check_device(device: dict[str, Any], standards: dict[str, Any], timeout: int, read_timeout: int) -> dict[str, Any]:
    result: dict[str, Any] = {
        "name": device["name"],
        "host": device["host"],
        "platform": device["platform"],
        "status": "failed",
        "checks": [],
        "error": "",
    }
    try:
        config = get_running_config(device, timeout, read_timeout)
        if device["platform"] == "cisco_asa":
            checks = check_asa(device, config, standards)
        else:
            checks = check_ios(device, config, standards)
        result["checks"] = checks
        hard_fail = any(item["status"] == "fail" for item in checks)
        result["status"] = "non_compliant" if hard_fail else "compliant"
    except (NetmikoAuthenticationException, NetmikoTimeoutException, OSError, RuntimeError) as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
    except Exception as exc:  # noqa: BLE001 - keep the fleet run alive
        result["error"] = f"{type(exc).__name__}: {exc}"
    return result


def resolve_standards(standards: dict[str, Any]) -> dict[str, Any]:
    resolved = dict(standards)
    snmp_env = standards.get("snmp_ro_community_env")
    if snmp_env:
        resolved["snmp_ro_community"] = os.getenv(str(snmp_env), "")
    return resolved


def status_counts(results: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in results:
        counts[item["status"]] = counts.get(item["status"], 0) + 1
    return counts


def write_summary(results: list[dict[str, Any]], output_dir: Path) -> None:
    counts = status_counts(results)
    lines = [
        "# Phase 5 Compliance Check Summary",
        "",
        f"- Checked UTC: {dt.datetime.now(dt.UTC).isoformat()}",
        f"- Devices attempted: {len(results)}",
        f"- Compliant: {counts.get('compliant', 0)}",
        f"- Non-compliant: {counts.get('non_compliant', 0)}",
        f"- Failed/unreachable: {counts.get('failed', 0)}",
        "",
        "| Device | Host | Platform | Status | Failing/Warned Checks | Error |",
        "|--------|------|----------|--------|------------------------|-------|",
    ]
    for item in results:
        flagged = [
            f"{check['check']}={check['status']}"
            for check in item.get("checks", [])
            if check["status"] in {"fail", "warn"}
        ]
        error = item.get("error", "").replace("|", "\\|")
        lines.append(
            f"| {item['name']} | {item['host']} | {item['platform']} | {item['status']} | {', '.join(flagged) or 'none'} | {error} |"
        )

    lines.extend(["", "## Detailed Checks", ""])
    for item in results:
        lines.append(f"### {item['name']}")
        if item.get("error"):
            lines.extend(["", f"- Error: `{item['error']}`", ""])
            continue
        lines.extend(["", "| Check | Status | Evidence |", "|-------|--------|----------|"])
        for check in item.get("checks", []):
            evidence = check["evidence"].replace("|", "\\|")
            lines.append(f"| {check['check']} | {check['status']} | {evidence} |")
        lines.append("")

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (output_dir / "summary.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Project 13 network compliance checks.")
    parser.add_argument("--inventory", default="configs/inventory-devices.yml", help="inventory YAML path")
    parser.add_argument("--output-dir", default="outputs/phase5-compliance", help="output directory")
    parser.add_argument("--device", action="append", help="limit checks to one or more device names")
    parser.add_argument("--timeout", type=int, default=20, help="connection timeout seconds")
    parser.add_argument("--read-timeout", type=int, default=45, help="command read timeout seconds")
    args = parser.parse_args()

    data = load_inventory(Path(args.inventory))
    errors = validate_inventory(data)
    if errors:
        print("Inventory validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 2

    devices = [device for device in data["devices"] if device.get("netmiko", True)]
    if args.device:
        selected = set(args.device)
        devices = [device for device in devices if device["name"] in selected]
        missing = selected.difference({device["name"] for device in devices})
        if missing:
            print(f"unknown or non-netmiko devices requested: {', '.join(sorted(missing))}", file=sys.stderr)
            return 2

    standards = resolve_standards(data.get("standards", {}))
    output_dir = Path(args.output_dir)
    results = [check_device(device, standards, args.timeout, args.read_timeout) for device in devices]
    write_summary(results, output_dir)
    counts = status_counts(results)
    print(
        "Compliance complete: "
        f"{counts.get('compliant', 0)} compliant, "
        f"{counts.get('non_compliant', 0)} non-compliant, "
        f"{counts.get('failed', 0)} failed"
    )
    print(f"Output directory: {output_dir}")
    return 1 if counts.get("failed", 0) or counts.get("non_compliant", 0) else 0


if __name__ == "__main__":
    raise SystemExit(main())
