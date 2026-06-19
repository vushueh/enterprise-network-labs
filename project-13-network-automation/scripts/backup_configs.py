#!/usr/bin/env python3
"""Project 13 redacted running-config backup collector.

The script connects with Netmiko, collects running configs, redacts sensitive
lines, and writes only redacted outputs to disk. Credentials come from the same
environment variables used by collect_baseline.py.
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

SECRET_PATTERNS = [
    re.compile(r"(?i)(enable\s+password\s+).+"),
    re.compile(r"(?i)(enable\s+secret\s+(?:(?:0|5|8|9)\s+)?).+"),
    re.compile(r"(?i)(password\s+(?:(?:0|7|8|9)\s+)?).+"),
    re.compile(r"(?i)(secret\s+(?:(?:0|5|8|9)\s+)?).+"),
    re.compile(r"(?i)(username\s+\S+\s+.*?(?:password|secret)\s+(?:(?:0|5|8|9)\s+)?).+"),
    re.compile(r"(?i)(snmp-server\s+community\s+)\S+(\s+.*)?"),
    re.compile(r"(?i)(snmp-server\s+host\s+\S+(?:\s+\S+)*\s+version\s+\S+\s+)\S+(\s+.*)?"),
    re.compile(r"(?i)(snmp-server\s+user\s+\S+\s+\S+\s+v3\s+auth\s+\S+\s+)\S+(\s+priv\s+\S+\s+)\S+(.*)?"),
    re.compile(r"(?i)(radius-server\s+key\s+).+"),
    re.compile(r"(?i)(tacacs-server\s+key\s+).+"),
    re.compile(r"(?i)(\s+key\s+(?:(?:0|7)\s+)?).+"),
    re.compile(r"(?i)(ip ospf message-digest-key\s+\d+\s+md5\s+(?:(?:0|7)\s+)?).+"),
    re.compile(r"(?i)(ntp authentication-key\s+\d+\s+md5\s+).+"),
    re.compile(r"(?i)(pre-shared-key\s+).+"),
]


def env_prefix(name: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_").upper()
    return f"NETLAB_{normalized}"


def first_env(*names: str) -> str | None:
    for name in names:
        value = os.getenv(name)
        if value:
            return value
    return None


def redact_line(line: str) -> str:
    for pattern in SECRET_PATTERNS:
        match = pattern.search(line)
        if not match:
            continue
        if pattern.pattern.startswith("(?i)(snmp-server\\s+community"):
            suffix = match.group(2) or ""
            return f"{match.group(1)}[REDACTED]{suffix}"
        if pattern.pattern.startswith("(?i)(snmp-server\\s+host"):
            suffix = match.group(2) or ""
            return f"{match.group(1)}[REDACTED]{suffix}"
        if pattern.pattern.startswith("(?i)(snmp-server\\s+user"):
            suffix = match.group(3) or ""
            return f"{match.group(1)}[REDACTED]{match.group(2)}[REDACTED]{suffix}"
        return f"{match.group(1)}[REDACTED]"
    return line


def redact_text(text: str) -> str:
    return "\n".join(redact_line(line) for line in text.splitlines())


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


def backup_device(device: dict[str, Any], output_dir: Path, timeout: int, read_timeout: int) -> dict[str, Any]:
    result = {
        "name": device["name"],
        "host": device["host"],
        "platform": device["platform"],
        "status": "failed",
        "file": "",
        "error": "",
    }

    try:
        with ConnectHandler(**connect_params(device, timeout)) as connection:
            if device["platform"] in {"cisco_ios", "cisco_asa"}:
                try:
                    connection.enable()
                except Exception:
                    pass
            command = "show running-config"
            output = connection.send_command(command, read_timeout=read_timeout)

        output_dir.mkdir(parents=True, exist_ok=True)
        target = output_dir / f"{device['name']}-running-config-redacted.txt"
        header = [
            f"! Project 13 redacted running-config backup",
            f"! Device: {device['name']}",
            f"! Host: {device['host']}",
            f"! Platform: {device['platform']}",
            f"! Collected UTC: {dt.datetime.now(dt.UTC).isoformat()}",
            "!",
            "",
        ]
        target.write_text("\n".join(header) + redact_text(output.rstrip()) + "\n", encoding="utf-8")
        result["status"] = "ok"
        result["file"] = str(target)
    except (NetmikoAuthenticationException, NetmikoTimeoutException, OSError, RuntimeError) as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
    except Exception as exc:  # noqa: BLE001 - keep the fleet run alive
        result["error"] = f"{type(exc).__name__}: {exc}"

    return result


def write_summary(results: list[dict[str, Any]], output_dir: Path) -> None:
    ok = [item for item in results if item["status"] == "ok"]
    failed = [item for item in results if item["status"] != "ok"]
    lines = [
        "# Phase 4 Redacted Config Backup Summary",
        "",
        f"- Collected UTC: {dt.datetime.now(dt.UTC).isoformat()}",
        f"- Devices attempted: {len(results)}",
        f"- Devices successful: {len(ok)}",
        f"- Devices failed: {len(failed)}",
        "",
        "| Device | Host | Platform | Status | File | Error |",
        "|--------|------|----------|--------|------|-------|",
    ]
    for item in results:
        error = item.get("error", "").replace("|", "\\|")
        lines.append(
            f"| {item['name']} | {item['host']} | {item['platform']} | {item['status']} | {item.get('file', '')} | {error} |"
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (output_dir / "summary.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect redacted Project 13 running-config backups.")
    parser.add_argument("--inventory", default="configs/inventory-devices.yml", help="inventory YAML path")
    parser.add_argument("--output-dir", default="outputs/phase4-redacted-backups", help="output directory")
    parser.add_argument("--device", action="append", help="limit backup to one or more device names")
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

    output_dir = Path(args.output_dir)
    results = [backup_device(device, output_dir, args.timeout, args.read_timeout) for device in devices]
    write_summary(results, output_dir)
    failed = [item for item in results if item["status"] != "ok"]
    print(f"Backup complete: {len(results) - len(failed)}/{len(results)} successful")
    print(f"Output directory: {output_dir}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
