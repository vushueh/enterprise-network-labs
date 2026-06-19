#!/usr/bin/env python3
"""Push Wazuh syslog settings to CML IOS devices.

This is intentionally separate from push_safe_config.py because it changes
operational logging. The script defaults to dry-run. Applying changes requires:

  --apply --confirm APPLY_WAZUH_SYSLOG
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


APPLY_CONFIRMATION = "APPLY_WAZUH_SYSLOG"
DEFAULT_WAZUH_SYSLOG_SERVER = "192.168.10.156"
IOS_ONLY_PLATFORM = "cisco_ios"
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
        if name in names:
            errors.append(f"duplicate device name: {name}")
        if host in hosts:
            errors.append(f"duplicate host IP: {host}")

        names.add(name)
        hosts.add(host)

        forbidden = FORBIDDEN_INVENTORY_KEYS.intersection(device.keys())
        if forbidden:
            errors.append(f"{name}: credential-like keys are not allowed in inventory: {', '.join(sorted(forbidden))}")

        if device.get("platform") == IOS_ONLY_PLATFORM and not device.get("source_interface"):
            errors.append(f"{name}: cisco_ios devices must define source_interface")

    return errors


def credentials_for(device: dict[str, Any]) -> tuple[str, str, str]:
    device_prefix = env_prefix(device["name"])
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


def render_commands(device: dict[str, Any], server: str, remove: bool) -> list[str]:
    if device["platform"] != IOS_ONLY_PLATFORM:
        return [
            "! skipped: non-IOS syslog syntax is platform-specific",
        ]

    if remove:
        return [
            f"no logging host {server}",
        ]

    return [
        "service timestamps log datetime msec localtime show-timezone",
        "logging origin-id hostname",
        "logging facility local6",
        "logging trap informational",
        f"logging source-interface {device['source_interface']}",
        f"logging host {server}",
    ]


def apply_device(
    device: dict[str, Any],
    output_dir: Path,
    server: str,
    apply: bool,
    remove: bool,
    timeout: int,
    read_timeout: int,
) -> dict[str, Any]:
    commands = render_commands(device, server, remove)
    result: dict[str, Any] = {
        "name": device["name"],
        "host": device["host"],
        "platform": device["platform"],
        "source_interface": device.get("source_interface", ""),
        "server": server,
        "mode": "remove" if remove else "deploy",
        "applied": apply,
        "status": "planned",
        "commands": commands,
        "before": "",
        "after": "",
        "error": "",
    }

    if device["platform"] != IOS_ONLY_PLATFORM:
        result["status"] = "skipped"
        return result

    if not apply:
        return result

    try:
        with ConnectHandler(**connect_params(device, timeout)) as connection:
            connection.enable()
            before = connection.send_command("show running-config | include ^logging", read_timeout=read_timeout)
            push_output = connection.send_config_set(commands, read_timeout=read_timeout)
            after = connection.send_command("show running-config | include ^logging", read_timeout=read_timeout)
            save_output = connection.save_config()

        output_dir.mkdir(parents=True, exist_ok=True)
        target = output_dir / f"{device['name']}-wazuh-syslog-{'remove' if remove else 'deploy'}.txt"
        target.write_text(
            "BEFORE:\n"
            + before.rstrip()
            + "\n\nPUSH:\n"
            + push_output.rstrip()
            + "\n\nAFTER:\n"
            + after.rstrip()
            + "\n\nSAVE:\n"
            + save_output.rstrip()
            + "\n",
            encoding="utf-8",
        )
        result["before"] = before
        result["after"] = after
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
        "# Wazuh Syslog Push Summary",
        "",
        f"- Generated UTC: {dt.datetime.now(dt.UTC).isoformat()}",
        f"- Devices: {len(results)}",
        f"- Applied mode: {any(item['applied'] for item in results)}",
        "",
        "| Device | Host | Platform | Source Interface | Server | Mode | Applied | Status | Error |",
        "|--------|------|----------|------------------|--------|------|---------|--------|-------|",
    ]
    for item in results:
        error = item.get("error", "").replace("|", "\\|")
        lines.append(
            f"| {item['name']} | {item['host']} | {item['platform']} | {item['source_interface']} | "
            f"{item['server']} | {item['mode']} | {item['applied']} | {item['status']} | {error} |"
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
    parser = argparse.ArgumentParser(description="Dry-run or apply Wazuh syslog settings to CML IOS devices.")
    parser.add_argument("--inventory", default="configs/inventory-devices.yml", help="inventory YAML path")
    parser.add_argument("--output-dir", default="outputs/wazuh-syslog", help="output directory")
    parser.add_argument("--server", default="", help="Wazuh syslog server IP; defaults to inventory standards")
    parser.add_argument("--device", action="append", help="limit push to one or more device names")
    parser.add_argument("--apply", action="store_true", help="apply the commands; default is dry-run only")
    parser.add_argument("--confirm", default="", help=f"must be {APPLY_CONFIRMATION} when --apply is used")
    parser.add_argument("--remove", action="store_true", help="remove only this Wazuh syslog host")
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

    server = args.server or data.get("standards", {}).get("wazuh_syslog_server") or DEFAULT_WAZUH_SYSLOG_SERVER
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
        apply_device(device, output_dir, server, args.apply, args.remove, args.timeout, args.read_timeout)
        for device in devices
    ]
    write_summary(results, output_dir)
    failed = [item for item in results if item["status"] == "failed"]
    print(f"Wazuh syslog {'apply' if args.apply else 'dry-run'} complete: {len(failed)} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
