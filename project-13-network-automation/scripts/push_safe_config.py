#!/usr/bin/env python3
"""Project 13 gated safe configuration pusher.

The first live push for this project is deliberately low risk: it creates an
unused standard ACL marker named P13-AUTOMATION-MARKER on IOS devices. The ACL
is not applied to any interface, line, SNMP command, or routing process. This
proves controlled configuration deployment without changing packet forwarding.

The script defaults to dry-run. Applying changes requires both --apply and:

  --confirm APPLY_SAFE_CONFIG
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
APPLY_CONFIRMATION = "APPLY_SAFE_CONFIG"


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


def render_commands(device: dict[str, Any], rollback: bool) -> list[str]:
    if device["platform"] == "cisco_asa":
        return [
            "! ASA safe-push intentionally skipped in Project 13 v1",
            "! ASA syntax and SSH reachability are handled as a separate platform exception",
        ]

    if rollback:
        return [
            "no ip access-list standard P13-AUTOMATION-MARKER",
        ]

    return [
        "ip access-list standard P13-AUTOMATION-MARKER",
        f" remark Project 13 automation safe marker on {device['name']}",
        " remark ACL is intentionally unused and has no packet-forwarding effect",
    ]


def apply_device(
    device: dict[str, Any],
    output_dir: Path,
    apply: bool,
    rollback: bool,
    timeout: int,
    read_timeout: int,
) -> dict[str, Any]:
    commands = render_commands(device, rollback)
    result: dict[str, Any] = {
        "name": device["name"],
        "host": device["host"],
        "platform": device["platform"],
        "mode": "rollback" if rollback else "deploy",
        "applied": apply,
        "status": "planned",
        "commands": commands,
        "error": "",
    }

    if device["platform"] == "cisco_asa":
        result["status"] = "skipped"
        return result

    if not apply:
        return result

    try:
        with ConnectHandler(**connect_params(device, timeout)) as connection:
            connection.enable()
            output = connection.send_config_set(commands, read_timeout=read_timeout)
            verify = connection.send_command("show running-config | section P13-AUTOMATION-MARKER", read_timeout=read_timeout)
            connection.save_config()
        output_dir.mkdir(parents=True, exist_ok=True)
        target = output_dir / f"{device['name']}-safe-config-{'rollback' if rollback else 'deploy'}.txt"
        target.write_text(output.rstrip() + "\n\nVERIFY:\n" + verify.rstrip() + "\n", encoding="utf-8")
        result["status"] = "ok"
    except (NetmikoAuthenticationException, NetmikoTimeoutException, OSError, RuntimeError) as exc:
        result["status"] = "failed"
        result["error"] = f"{type(exc).__name__}: {exc}"
    except Exception as exc:  # noqa: BLE001 - keep the fleet run alive
        result["status"] = "failed"
        result["error"] = f"{type(exc).__name__}: {exc}"

    return result


def write_summary(results: list[dict[str, Any]], output_dir: Path) -> None:
    lines = [
        "# Phase 6 Gated Safe Config Push Summary",
        "",
        f"- Generated UTC: {dt.datetime.now(dt.UTC).isoformat()}",
        f"- Devices: {len(results)}",
        f"- Applied mode: {any(item['applied'] for item in results)}",
        "",
        "| Device | Host | Platform | Mode | Applied | Status | Error |",
        "|--------|------|----------|------|---------|--------|-------|",
    ]
    for item in results:
        error = item.get("error", "").replace("|", "\\|")
        lines.append(
            f"| {item['name']} | {item['host']} | {item['platform']} | {item['mode']} | {item['applied']} | {item['status']} | {error} |"
        )
    lines.extend(["", "## Commands", ""])
    for item in results:
        lines.extend([f"### {item['name']}", "", "```text"])
        lines.extend(item["commands"])
        lines.extend(["```", ""])

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (output_dir / "summary.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Dry-run or apply a gated Project 13 safe config marker.")
    parser.add_argument("--inventory", default="configs/inventory-devices.yml", help="inventory YAML path")
    parser.add_argument("--output-dir", default="outputs/phase6-safe-config", help="output directory")
    parser.add_argument("--device", action="append", help="limit push to one or more device names")
    parser.add_argument("--apply", action="store_true", help="apply the commands; default is dry-run only")
    parser.add_argument("--confirm", default="", help=f"must be {APPLY_CONFIRMATION} when --apply is used")
    parser.add_argument("--rollback", action="store_true", help="remove the safe marker instead of deploying it")
    parser.add_argument("--timeout", type=int, default=20, help="connection timeout seconds")
    parser.add_argument("--read-timeout", type=int, default=30, help="command read timeout seconds")
    args = parser.parse_args()

    if args.apply and args.confirm != APPLY_CONFIRMATION:
        print(f"--apply requires --confirm {APPLY_CONFIRMATION}", file=sys.stderr)
        return 2

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
    results = [
        apply_device(device, output_dir, args.apply, args.rollback, args.timeout, args.read_timeout)
        for device in devices
    ]
    write_summary(results, output_dir)
    failed = [item for item in results if item["status"] == "failed"]
    print(f"Safe config {'apply' if args.apply else 'dry-run'} complete: {len(failed)} failed")
    print(f"Output directory: {output_dir}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
